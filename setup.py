from os import path
from setuptools import setup, find_packages


def load_readme_text():
    """Load in README file as a string."""
    try:
        dir_path = path.abspath(path.dirname(__file__))
        with open(path.join(dir_path, 'README.md'), encoding='utf-8') as filename:
            return filename.read()
    except FileNotFoundError:
        print("No README file found")


setup(
    name='smartstopos',
    version='0.2.0',
    author='Ariana Torres-Knoop',
    author_email='ariana.torres-knoop@surfsara.nl',
    description='Tools for running parameters exploration and optimization locally and on the HPC',
    long_description=load_readme_text(),
    install_requires=['numpy', 'pandas'],
    packages=find_packages(),
    setup_requires=['pytest-runner', 'flake8'],
    zip_safe=False,
    platforms='any',
    package_data={'smartstopos': ['runscripts/run_local.sh', 'runscripts/run.sh', 'runscripts/input_ini.file',
                                  'runscripts/analysis.job', 'runscripts/stopos.job', 'docs/inputfile.rst']}
    # test_requires='pytests',
    # extra_requires={'interactive': ['matplotlib']},
)
