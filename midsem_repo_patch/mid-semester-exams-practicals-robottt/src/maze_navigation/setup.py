from setuptools import find_packages, setup

package_name = "maze_navigation"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/config", ["config/maze_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="David Orhin",
    maintainer_email="david.orhin@ashesi.edu.gh",
    description="Maze solving logic for the rover",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "maze_finder_node = maze_navigation.maze_finder_node:main",
        ],
    },
)
