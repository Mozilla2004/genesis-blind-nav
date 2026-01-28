
from setuptools import setup, find_packages

setup(
    name="genesis-kernel",
    version="0.1.0",
    author="Genesis Team",
    description="Quantum Intelligence Activation Protocol v9.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.3.0",
    ],
    python_requires=">=3.7",
    license="Apache 2.0",
)
