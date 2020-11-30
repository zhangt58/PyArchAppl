from setuptools import setup

install_requires = [
    'pandas',
    'tzlocal',
    'requests',
    'simplejson',
]

extra_require = {
    'test': 'pytest',
    'fancy': 'tqdm',
    'doc': 'sphinx', 'pydata_sphinx_theme',
}

setup(
        name='pyarchappl',
        version='0.9.2',
        description='Python interface to Archiver Appliance',
        author='Tong Zhang',
        author_email='zhangt@frib.msu.edu',
        packages=['archappl.admin',
                  'archappl.data',
                  'archappl.client',
                  'archappl.contrib',
                  'archappl'],
        package_dir={
            'archappl.admin': 'main/mgmt',
            'archappl.data' : 'main/data',
            'archappl.client': 'main/client',
            'archappl.contrib': 'main/contrib',
            'archappl': 'main'
        },
        install_requires=install_requires,
        extra_require=extra_require,
)
