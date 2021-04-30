# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:03

from setuptools import setup

__version__ = '0.0.1'

long_description = """

"""

setup(
    name="flask-openapi3",
    version=__version__,
    url='https://github.com/luolingchun/flask-openapi3',
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='llc',
    author_email='luolingchun@outlook.com',
    license='GPLv3',
    packages=['flask_openapi3'],
    include_package_data=True,
    python_requires=">=3.6",
    zip_safe=False,
    platforms='any',
    install_requires=['PyQt5', 'QScintilla']
)
