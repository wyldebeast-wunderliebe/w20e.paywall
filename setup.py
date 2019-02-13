from setuptools import setup, find_packages
# from pip.req import parse_requirements

import os

name = "w20e.paywall"
version = "1.0.0"

install_requires = []
with open('requirements.txt') as fp:
    install_requires = fp.read()


setup(
    name=name,
    version=version,
    description="Paywall",
    # long_description=read('README.md'),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Framework :: Flask',
    ],
    keywords="flask,mollie,payment,paywall",
    author="Wietze Helmantel",
    author_email='helmantel@turftorr.nl',
    url='http://turftorr.nl',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    """,
)
