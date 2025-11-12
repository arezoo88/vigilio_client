from setuptools import setup, find_packages

setup(
    name="vigilio_client",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.50.0",
        "protobuf>=4.0.0"
    ],
    python_requires=">=3.8",
    include_package_data=True
)