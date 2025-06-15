from setuptools import setup, find_packages

setup(
    name="resume-parser",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "alembic",
        "psycopg2-binary",
    ],
)