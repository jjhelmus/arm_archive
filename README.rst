arm_archive.py is a Python module for accessing data from the
`ARM archive <http://www.archive.arm.gov>`_.

Requirements
------------

* Python 2.7, 3.3, 3.4.
* `Suds <https://pypi.python.org/pypi/suds>`_ with Python 2.7.
* `Suds-jurko <https://pypi.python.org/pypi/suds-jurko>`_ with Python 3.3/3.4.

Install
-------

To install using pip use::

    pip install arm_archive

To install from source in your home directory, use::
    
    python setup.py install --user

To install for all users on Unix/Linux::

    python setup.py install

Use
---
The functions in the module can be used in Python after importing the module.

The module can also be used from the command line using::

    python -m arm_archive

This can be aliased in bash using::

    alias apu='python -m arm_archive'


Command line examples
---------------------

These examples assume that the above alias has been created so that
'python -m arm_archive' can be executed using 'apu'. Addition help for each
command can be obtained using 'apu command -h', for example 'apu list -h'.

List available datastreams which match a regular expression::

    $ apu datastreams sgpceil
    sgpceilB1.b1
    sgpceilB4.b1
    sgpceilB5.b1
    sgpceilB6.b1
    sgpceilC1.b1
    sgpceilpblhtC1.a0

List available files for a specific time period::

    $ apu list sgpceilC1.b1 20141001 20141005
    sgpceilC1.b1.20141001.000010.nc
    sgpceilC1.b1.20141002.000008.nc
    sgpceilC1.b1.20141003.000004.nc
    sgpceilC1.b1.20141004.000002.nc
    sgpceilC1.b1.20141005.000000.nc

Leaving off the end date will find file for only a single day::

    $ apu list sgpceilC1.b1 20141015
    sgpceilC1.b1.20141015.000009.nc

Ordering data for a specific datastream and time period::

    $ apu order -d sgpceilC1.b1 20141001 20141005 username
    Success 5 file(s) ordered, order_id: 123456

Ordering data by supplying a list of filenames::

    $ apu order username sgpceilC1.b1.20141015.000009.nc
    Success 1 file(s) ordered, order_id: 123456

Check that status of an order::

    $ apu status 123456
    processing

List files in a complete order::

    $ apu files username 123456
    AAA.files_not_found
    sgpceilC1.b1.20141005.000000.nc
    sgpceilC1.b1.20141015.000009.nc

Download file from a complete order to the current directory::

    $ apu download username 168977
    Retrieving: AAA.files_not_found
    Retrieving: sgpceilC1.b1.20141005.000000.nc
    Retrieving: sgpceilC1.b1.20141015.000009.nc

Download a single file from a complete order::

    $ apu download username 168977 sgpceilC1.b1.20141005.000000.nc
    Retrieving: sgpceilC1.b1.20141005.000000.nc

Canceling an order::

    $ apu cancel username 123456
    True

List all orders with some files ready to download for a given user::

    $ apu ready username
    123456
    123457
