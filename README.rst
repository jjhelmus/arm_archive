arm_archive.py is a Python module for accessing data from the  
`ARM archive <http://www.archive.arm.gov/armlogin/login.jsp>`_.

Requirements
------------

* Python 2.7 (3.3 might work)
* `Suds <https://fedorahosted.org/suds/>`_, tested with version 0.4


Install
-------
Copy the file arm_archive.py to the site-packages directory, add a .pth file, or
add the directory to the PYTHON_PATH.

Use
---
The functions in the module can be used in Python after importing the module.

The module can also be used from the command line using:

    python -m arm_archive

This can be aliased in bash using:
    
    alias apu='python -m arm_archive'
