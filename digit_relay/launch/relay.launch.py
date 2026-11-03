from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='turtlesim', executable='turtlesim_node'),
        Node(package='digit_relay', executable='member_1', output='screen'),
        Node(package='digit_relay', executable='member_2', output='screen'),
        # Add member_3 .. member_6 here once their entry points exist in setup.py
    ])
