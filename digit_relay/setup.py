from setuptools import setup

package_name = 'digit_relay'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/relay.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'member_1 = digit_relay.member_1:main',
            'member_2 = digit_relay.member_2:main',
            'member_3 = digit_relay.member_3:main',
            'member_4 = digit_relay.member_4:main',
            'member_5 = digit_relay.member_5:main',
        ],
    },
)
