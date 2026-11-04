from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='turtlesim', executable='turtlesim_node'),
        Node(package='digit_relay', executable='member_1', output='screen'),
        Node(package='digit_relay', executable='member_2', output='screen'),
        Node(package='digit_relay', executable='member_3', output='screen'),
        Node(package='digit_relay', executable='member_4', output='screen'),
        Node(package='digit_relay', executable='member_5', output='screen'),
        # Add member_6 here once its entry point exists in setup.py
    ])
