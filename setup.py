import os
from pip.req import parse_requirements
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

setup(
    name='django-rest-secureview',
    version='0.0.2',
    url='https://github.com/fmitra/django-rest-secureview',
    download_url = 'https://github.com/fmitra/django-rest-secureview/tarball/0.0.1',
    license='MIT',
    author='Francis Mitra',
    author_email='francismitra@gmail.com',
    description='Enforces client ViewSet requirements for Django Rest Framework',
    keywords = ['django', 'django-restframework'],
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=reqs
)

