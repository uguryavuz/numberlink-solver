# Author: Ugur Yavuz
# August 2019
# setup.py: Installs necessary libraries.

import importlib.util               # To determine if libraries are installed.
from pip._internal import main      # Pip, to install libraries.

LIBS = ['ortools', 'pygame', 'pygbutton']

for library in LIBS:
    # Install library if not installed.
    if not importlib.util.find_spec(library):
        main(['install', library])
