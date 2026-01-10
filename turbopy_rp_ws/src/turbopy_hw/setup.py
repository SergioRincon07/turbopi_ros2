from setuptools import find_packages, setup

package_name = 'turbopy_hw'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sergiopi',
    maintainer_email='sergiorincon50@gmail.com',
    description='Hardware abstraction layer for TurboPi (motors, LEDs, buzzer, battery, etc.).',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
