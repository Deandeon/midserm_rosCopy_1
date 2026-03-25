from setuptools import find_packages, setup

package_name = "maze_energy"

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
    maintainer="David Orhin",
    maintainer_email="david.orhin@ashesi.edu.gh",
    description="Energy accounting for the maze rover",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "energy_node = maze_energy.energy_node:main",
        ],
    },
)
