# -*- coding: utf-8 -*-

import sys
from setuptools import setup


def readme() -> str:
    with open('README.md', 'r') as f:
        return f.read()


def read_requires(filepath: str) -> list[str]:
    lines = []
    for line in open(filepath, "r"):
        lines.append(line.strip())

py_ver = (sys.version_info.major, sys.version_info.minor)
if py_ver in [(3, 9), (3, 10), (3, 11)]:
    install_requires = read_requires("requirements.txt")
elif py_ver in [(3, 12), (3, 13)]:
    install_requires = read_requires("requirements-3.13.txt")
else:
    install_requires = []


extras_require = {
    'test': ['pytest'],
    'doc': ['sphinx', 'pydata_sphinx_theme'],
}


def set_entry_points():
    r = {
        'console_scripts': [
            'pyarchappl-get=archappl.scripts.get:main',
            'pyarchappl-inspect=archappl.scripts.inspect:main',
        ]
    }
    return r


setup(
    name='pyarchappl',
    version='1.0.0',
    description='Python interface to Archiver Appliance',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url="https://github.com/zhangt58/pyarchappl",
    author='Tong Zhang',
    packages=[
        'archappl.admin', 'archappl.data', 'archappl.data.pb',
        'archappl.client', 'archappl.contrib', 'archappl.config',
        'archappl.scripts', 'archappl'
    ],
    package_dir={
        'archappl.admin': 'main/mgmt',
        'archappl.data': 'main/data',
        'archappl.data.pb': 'main/data/pb',
        'archappl.client': 'main/client',
        'archappl.contrib': 'main/contrib',
        'archappl.config': 'main/config',
        'archappl.scripts': 'main/scripts',
        'archappl': 'main'
    },
    include_package_data=True,
    entry_points=set_entry_points(),
    install_requires=install_requires,
    extras_require=extras_require,
    license='GPL3+',
    keywords="Archiver EPICS CA PVA",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
