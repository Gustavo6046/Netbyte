import yaml

from setuptools import setup, find_packages
from os import path

# read the contents of README file
this_dir = path.abspath(path.dirname(__file__))

with open(path.join(this_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="Netbyte",
    version=yaml.load(open("changelog.yml"))['versions'][-1]['name'],
    packages=["netbyte"],
    
    # metadata to display on PyPI
    author="Gustavo6046",
    author_email="gugurehermann@gmail.com",
    description="A language with interpreter and compiler: silk flexibility with network level versatility!",
    license="MIT",
    keywords="compiler language interpreter bytecode",
    url="https://github.com/Gustavo6046/Netbyte",
    package_data={
        'netbyte': ['*.nbc', '*.nbe', ''],
    },
    
    long_description=long_description,
    long_description_content_type='text/markdown'
)