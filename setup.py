from setuptools import setup, find_packages

setup(
    name="ping-pong",          # Package name
    version="0.1",             # Version number
    package_dir={"": "src"},   # Tells setuptools where packages are located
    packages=find_packages(where="src"),  # Automatically find all packages in src/
    install_requires=[         # List of dependencies
        "pygame",
        # other dependencies
    ],
)
