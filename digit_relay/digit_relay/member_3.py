import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from turtlesim.srv import SetPen, TeleportAbsolute

from relay_interfaces.msg import Turn

MY_ID = 3
N = 6                 # group size; numbers run 1..2N
SLOT = (9.0, 8.0)     # center of slot 3 (top-right)
COLOR = (0, 0, 255)   # blue

# Polylines in a 1.0 x 1.6 box, origin at bottom-left
DIGITS = {
    3: [[(0.0, 1.6), (1.0, 1.6), (1.0, 0.0), (0.0, 0.0)],
        [(0.3, 0.8), (1.0, 0.8)]],
    9: [[(1.0, 0.8), (0.0, 0.8), (0.0, 1.6), (1.0, 1.6),
         (1.0, 0.0), (0.0, 0.0)]],
}


def main():
    rclpy.init()
    node = Node('member_3')
    # transient_local so late-starting nodes still get the last turn
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
    pub = node.create_publisher(Turn, 'turn', qos)
    inbox = []
    node.create_subscription(Turn, 'turn', inbox.append, qos)
    set_pen = node.create_client(SetPen, 'turtle1/set_pen')
    teleport = node.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')

    def call(client, req):
        if not client.wait_for_service():
            raise ExternalShutdownException()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(node, future)
        if not rclpy.ok():
            raise ExternalShutdownException()
        return future.result()

    def pen(off):
        call(set_pen, SetPen.Request(r=COLOR[0], g=COLOR[1], b=COLOR[2], width=3, off=off))

    def go(x, y):
        call(teleport, TeleportAbsolute.Request(x=SLOT[0] - 0.5 + x, y=SLOT[1] - 0.8 + y))

    def draw(number):
        for line in DIGITS[number]:
            pen(1)              # pen up while moving to the stroke start
            go(*line[0])
            pen(0)              # pen down to draw the stroke
            for point in line[1:]:
                go(*point)
        pen(1)

    log = node.get_logger()
    try:
        log.info('waiting for turn...')
        expected_number = MY_ID
        done = False
        while rclpy.ok() and not done:
            rclpy.spin_once(node)
            while inbox:
                msg = inbox.pop(0)
                if msg.current_number > 2 * N:
                    done = True
                    break
                if (msg.active_member != MY_ID
                        or msg.current_number != expected_number
                        or msg.current_number not in DIGITS):
                    continue
                number = msg.current_number
                expected_number += N
                draw(number)
                pub.publish(Turn(current_number=number + 1, active_member=MY_ID + 1))
                log.info(f'drew {number}, turn -> member {MY_ID + 1}')
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
