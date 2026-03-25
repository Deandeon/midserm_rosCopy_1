from setuptools import setup

package_name = "maze_energy"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="ubuntu",
    maintainer_email="mamadoufatchima15@gmail.com",
    description="Energy consumption tracking node for maze robot",
    license="MIT",
    entry_points={
        "console_scripts": [
            "energy_node = maze_energy.energy_node:main",
        ],
    },
)
