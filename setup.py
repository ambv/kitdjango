# -*- encoding: utf-8 -*-
# Copyright (C) 2010 LangaCore
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from setuptools import setup, find_packages

assert sys.version_info >= (2, 7), "Python 2.7+ required."

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as ld_file:
    long_description = ld_file.read()

from doc.conf import release

setup (
    name = 'langacore.kit.django',
    version = release,
    author = 'LangaCore, Lukasz Langa',
    author_email = 'support@langacore.org, lukasz@langa.pl',
    description = "Various common Django-related routines.",
    long_description = long_description,
    url = 'http://packages.python.org/langacore.kit.django/',
    keywords = '',
    platforms = ['any'],
    license = 'GPL v3',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['langacore', 'langacore.kit'],
    zip_safe = False, # because executing support extensions for settings.py
                      # requires actual files
    install_requires = [
        'langacore.kit.common',
        'langacore.kit.i18n',
        'setuptools',
        'django>=1.2',
        'postmarkup',
        ],

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )
