# -*- coding: utf-8 -*-
import os, os.path

def publish(path):
    return os.sep.join((os.path.split(__file__)[0], path,))

current_dir_support = publish('current_dir_support.py')
namespace_package_support = publish('namespace_package_support.py')
profile_support = publish('profile_support.py')
