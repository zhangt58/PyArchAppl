# -*- coding: utf-8 -*-

from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


install_requires = [
    'numpy>=1.0,<2.0',
    'pandas>=1.0,<2.0',
    'openpyxl>3.0,<3.1',
    'tzlocal>=4.0,<5.0',
    'requests>=2.0,<3.0',
    'simplejson>=3.0,<4.0',
    'tqdm>=4.0,<5.0',
    'tables>=3.0,<4.0',
    'protobuf>=3.0,<4.0',
]

extra_require = {
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
    url="https://github.com/archman/pyarchappl",
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
    extra_require=extra_require,
    license='GPL3+',
    keywords="Archiver EPICS CA PVA",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
