from setuptools import find_packages, setup

package_name = "rover_navigation"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Student",
    maintainer_email="student@example.com",
    description="Maze solving logic for the CS353 rover",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "maze_finder_node = rover_navigation.maze_finder_node:main",
        ],
    },
)
