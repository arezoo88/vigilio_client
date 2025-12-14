from setuptools import setup, find_packages
from pathlib import Path


readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="vigilio_client",
    version="1.0.4",
    description="gRPC client and Django REST API for Vigilio shareholder service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Iman Sadeghian",
    author_email="i.sadeghian1999@gmail.com",
    url="https://github.com/imansmd/",

    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        'vigilio_client': ['*.proto'],
    },


    install_requires=[
        "grpcio>=1.50.0",
        "protobuf>=4.0.0",
        'djangorestframework>=3.15.0',
        'pandas>=2.3.0',
        'openpyxl>=3.1.0',
    ],


    python_requires=">=3.10",
    include_package_data=True,
)