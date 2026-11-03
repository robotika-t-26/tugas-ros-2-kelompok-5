import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_srvs.srv import Empty
from turtlesim.srv import SetPen, TeleportAbsolute

from relay_interfaces.msg import Turn

MY_ID = 1
N = 6                 # group size; numbers run 1..2N
SLOT = (2.0, 8.0)     # center of slot 1 (top-left)
COLOR = (255, 0, 0)

# Polylines in a 1.0 x 1.6 box, origin at bottom-left
DIGITS = {
    1: [[(0.25, 1.3), (0.5, 1.6), (0.5, 0.0)]],
    7: [[(0.0, 1.6), (1.0, 1.6), (0.3, 0.0)]],
}


def main():
    rclpy.init()
    node = Node('member_1')
    # transient_local so late-starting nodes still get the last turn
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
    pub = node.create_publisher(Turn, 'turn', qos)
    inbox = []
    node.create_subscription(Turn, 'turn', inbox.append, qos)
    set_pen = node.create_client(SetPen, 'turtle1/set_pen')
    teleport = node.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')
    clear = node.create_client(Empty, 'clear')

    def call(client, req):
        client.wait_for_service()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(node, future)

    def pen(off):
        call(set_pen, SetPen.Request(r=COLOR[0], g=COLOR[1], b=COLOR[2], width=3, off=off))

    def go(x, y):
        call(teleport, TeleportAbsolute.Request(x=SLOT[0] - 0.5 + x, y=SLOT[1] - 0.8 + y))

    def draw(number):
        for line in DIGITS[number]:
            pen(1)
            go(*line[0])
            pen(0)
            for p in line[1:]:
                go(*p)
        pen(1)

    log = node.get_logger()
    try:
        log.info('waiting for turtlesim...')
        draw(1)
        pub.publish(Turn(current_number=2, active_member=2))
        log.info('drew 1, turn -> member 2')
        done = False
        while rclpy.ok() and not done:
            rclpy.spin_once(node)
            while inbox:
                msg = inbox.pop(0)
                if msg.current_number > 2 * N:
                    done = True
                elif msg.active_member == MY_ID and msg.current_number == N + 1:
                    call(clear, Empty.Request())
                    draw(N + 1)
                    pub.publish(Turn(current_number=N + 2, active_member=2))
                    log.info(f'drew {N + 1}, turn -> member 2')
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    rclpy.try_shutdown()
