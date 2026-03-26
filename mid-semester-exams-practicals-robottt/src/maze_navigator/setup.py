from setuptools import setup
import os
from glob import glob

package_name = "maze_navigator"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*")),
        (os.path.join("share", package_name, "launch"), glob("launch/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="ubuntu",
    maintainer_email="mamadoufatchima15@gmail.com",
    description="Maze navigation node using right-hand wall following",
    license="MIT",
    entry_points={
        "console_scripts": [
            "navigator_node = maze_navigator.navigator_node:main",
        ],
    },
)
