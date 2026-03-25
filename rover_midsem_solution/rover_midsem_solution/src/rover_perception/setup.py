from setuptools import find_packages, setup

package_name = "rover_perception"

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
    description="Gem detector for the CS353 rover",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "gem_detector_node = rover_perception.gem_detector_node:main",
        ],
    },
)
