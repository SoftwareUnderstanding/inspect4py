import os
from distutils.core import setup
from setuptools import find_packages  # type: ignore

from inspect4py import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


with open('requirements.txt', 'r') as f:
    install_requires = list()
    dependency_links = list()
    for line in f:
        re = line.strip()
        if re:
            if re.startswith('git+') or re.startswith('svn+') or re.startswith('hg+'):
                dependency_links.append(re)
            else:
                install_requires.append(re)

packages = find_packages()

setup(
    name='inspect4py',
    version=__version__,
    packages=packages,
    url='https://github.com/SoftwareUnderstanding/inspect4py',
    license='Apache2.0',
    author='Rosa Filgueira and Daniel Garijo',
    description='Package for performing static code analysis on Python projects',
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    entry_points={
        'console_scripts': [
            'inspect4py = inspect4py.cli:main',
        ],
    }
)
