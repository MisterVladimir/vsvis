# -*- coding: utf-8 -*-
"""
@author: Vladimir Shteyn
@email: vladimir.shteyn@googlemail.com

Copyright Vladimir Shteyn, 2018

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from setuptools import setup

with open('README.md', 'r') as f:
    README = f.read()


def get_requirements():
    with open('requirements.txt', 'r') as f:
        raw = f.read().replace(' ', '')
        return raw.split('\n')


if __name__ == '__main__':
    from setuptools import find_packages
    ver = '0.1'
    url = r'https://github.com/MisterVladimir/vsvis'
    setup(name='vsvis',
          packages=find_packages(),
          version=ver,
          ext_modules=[],
          python_requires='>=3.6',
          install_requires=get_requirements(),
          setup_requires=["pytest-runner"],
          tests_require=["pytest", "pytest-qt", "pytest-cov", "pandas"],
          include_package_data=True,
          author='Vladimir Shteyn',
          author_email='vladimir.shteyn@googlemail.com',
          url=url,
          download_url=r'{0}/archive/{1}.tar.gz'.format(url, ver),
          long_description=README,
          license="GNUv3",
          classifiers=[
              'Intended Audience :: Science/Research',
              'Topic :: Scientific/Engineering :: Medical Science Apps.',
              'Topic :: Scientific/Engineering :: Image Recognition',
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3.7'])
