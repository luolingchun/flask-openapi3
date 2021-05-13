# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:03

from setuptools import setup, find_packages

__version__ = '0.9.0'

long_description = open('README.md', 'r').read()

setup(
    name="flask-openapi3",
    version=__version__,
    url='https://github.com/luolingchun/flask-openapi3',
    description='Generate RESTful API and OpenAPI document for your Flask project.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD-3-Clause',
    license_files='LICENSE.rst',
    author='llc',
    author_email='luolingchun@outlook.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    zip_safe=False,
    platforms='any',
    install_requires=['Flask>=1.0.0', 'pydantic>=1.0.0'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)
