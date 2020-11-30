from setuptools import setup


setup(
        name='pyarchappl',
        version='0.9.1',
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
)
