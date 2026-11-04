import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from turtlesim.srv import SetPen, TeleportAbsolute

from relay_interfaces.msg import Turn

MY_ID = 5
N = 6                 # group size; numbers run 1..2N
SLOT = (5.5, 5.4)     # bottom-center; 1.0 unit gap below the top row
COLOR = (255, 0, 255)  # magenta
HEIGHT = 1.6          # same digit height as members 1 and 3
DIGIT_WIDTH = 1.0
DIGIT_GAP = 0.2

# Polylines in a 1.0 x 1.6 box, origin at bottom-left.
DIGITS = {
    '1': [[(0.25, 1.3), (0.5, 1.6), (0.5, 0.0)]],
    '5': [[(1.0, 1.6), (0.0, 1.6), (0.0, 0.8),
           (1.0, 0.8), (1.0, 0.0), (0.0, 0.0)]],
}


def main():
    rclpy.init()
    node = Node('member_5')
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
        call(teleport, TeleportAbsolute.Request(x=SLOT[0] + x, y=SLOT[1] - HEIGHT / 2 + y))

    def draw(number):
        digits = str(number)
        width = len(digits) * DIGIT_WIDTH + (len(digits) - 1) * DIGIT_GAP
        for index, digit in enumerate(digits):
            offset = -width / 2 + index * (DIGIT_WIDTH + DIGIT_GAP)
            for line in DIGITS[digit]:
                pen(1)              # pen up while moving to the stroke start
                go(offset + line[0][0], line[0][1])
                pen(0)
                for x, y in line[1:]:
                    go(offset + x, y)
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
                        or msg.current_number != expected_number):
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
