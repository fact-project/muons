from setuptools import setup, find_packages

setup(
    name='muons',
    version='0.0.1',
    description='Extract muons from FACT photon stream',
    url='https://github.com/fact-project/',
    author=['Sebastian Achim Mueller', "Laurits Tani"],
    author_email='sebmuell@phys.ethz.ch',
    license='MIT',
    packages=find_packages(),
    package_data={
        'muons': [
            'tests/resources/*', ]
    },
    install_requires=[
        'docopt',
        'scipy',
        'scikit-learn',
        'scikit-image',
        'pyfact',
        'pandas',
        'photon_stream',
        'msgpack_numpy',
        'circlehough',
        'scoop',
        'numpy>=1.15.0'
    ],
    entry_points={'console_scripts': [
        'phs_extract_muons = ' +
        'muons.isdc_production.worker_node_main:main', ]},
    zip_safe=False,
)
