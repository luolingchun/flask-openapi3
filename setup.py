# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:03
import os
import re

from setuptools import setup, find_packages

version_file = os.path.join(os.path.dirname(__file__), 'flask_openapi3', '__version__.py')
with open(version_file, 'r', encoding='utf-8') as f:
    version = re.findall(r"__version__ = '(.*?)'", f.read())[0]

long_description = open('README.md', 'r', encoding='utf-8').read()

install_requires = []
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r', encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip()
        if line:
            install_requires.append(line)

setup(
    name="flask-openapi3",
    version=version,
    url='https://github.com/luolingchun/flask-openapi3',
    description='Generate REST API and OpenAPI documentation for your Flask project.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    license_files='LICENSE.rst',
    author='llc',
    author_email='luolingchun@outlook.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    extras_require={'yaml': ['pyyaml']},
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha    ',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)
