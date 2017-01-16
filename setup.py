from setuptools import setup, find_packages
from pip.req import parse_requirements

import os

name = "w20e.paywall"
version = "1.0.0"

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session='hack')
reqs = [str(ir.req) for ir in install_reqs]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name=name,
    version=version,
    description="Paywall",
    long_description=read('README.md'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Framework :: Flask',
    ],
    keywords="flask,mollie,payment,paywall",
    author="Wietze Helmantel",
    author_email='helmantel@w20e.com',
    url='http://wyldebeast-wunderliebe.com',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs,
    entry_points="""
    [console_scripts]
    """,
)
