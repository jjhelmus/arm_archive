"""
Python Function for interacting with the ARM Archive.

By: Jonathan J. Helmus (jhelmus@anl.gov)
"""

from __future__ import print_function

import re as _re
from datetime import datetime as _datetime
from datetime import timedelta as _timedelta
from ftplib import FTP as _FTP

from suds.client import Client as _Client

__version__ = '0.2.0.dev'

_ARM_WS_URL = 'http://www.archive.arm.gov/armws/services/arm?wsdl'
_ARM_FTP = 'ftp.archive.arm.gov'


def _init_client():
    """ Initialize a client to the ARM Archive Web service. """
    return _Client(_ARM_WS_URL)


def _regex_filter(sequence, pattern):
    """ Filter a sequence based on a regular expression """
    if pattern is None:
        return sequence
    else:
        p = _re.compile(pattern)
        return filter(p.search, sequence)


def list_datastreams(pattern=None):
    """
    List datastreams available at the ARM Archive.

    Parameters
    ----------
    pattern : str, optional
        Regular expression used to filter the datastream names,
        None will return all datastreams.

    Returns
    -------
    datastreams : list
        List of datastreams, optionally filter according to the regular
        expression `pattern`.

    """
    client = _init_client()
    datastreams = client.service.getDataStreams()
    return sorted(_regex_filter(datastreams, pattern))


def list_files(datastreams, startdate, enddate=None, pattern=None):
    """
    List the files in one or more datastreams in the ARM Archive.

    Parameters
    ----------
    datastreams : str or list
        Datastream or list of datastreams
    startdate : str
        Starting date for listing, formatted as YYYYMMDD.
    enddate : str or None, optional
        Ending date for listing, formatted as YYYYMMDD. None will select the
        next day after startdate.
    pattern : str, optional
        Regular expression used to filter the datastream names,
        None will return all datastreams.

    Returns
    -------
    files : list
        List of file in datastreams

    """
    client = _init_client()
    if enddate is None:
        dt = _datetime.strptime(startdate, '%Y%m%d')
        enddate = (dt + _timedelta(days=1)).strftime('%Y%m%d')
    files = client.service.getFiles(datastreams, startdate, enddate)
    if len(files) == 1 and files[0] == 'No data files found':
        return []
    return sorted(_regex_filter(files, pattern))


def valid_user(user):
    """
    Check if a user is valid.

    Parameters
    ----------
    user : str
        Username to check.

    Returns
    -------
    check : bool
        True if user is valid, False if not valid.

    """
    client = _init_client()
    valid = client.service.isValidUser(user)
    if valid == 'true':
        return True
    return False


def order_files(user, filenames):
    """
    Order files from the ARM Archive.

    Parameters
    ----------
    user : str
        Username.
    filenames : list
        List of filesname to order.

    Returns
    -------
    flag : bool
        True or False indicating if the order was successful.
    status : str or tuple
        If the order successed, then contains a tuple containing the user,
        order_id, and number of files as strings.  If the order failed
        contains the response from the server.

    """
    client = _init_client()
    response = client.service.processOrder(user, filenames)

    pattern = _re.compile(r'user:\s*([a-z]+), '
                          r'order session ID:\s*([0-9]+) '
                          r'number of files ordered:\s*([0-9]+)')
    match = pattern.search(response)
    if match:
        return True, match.groups()
    else:
        return False, response


def order_status(order_id):
    """
    Check on an order.

    Parameters
    ----------
    order_id : str or int
        Order id

    Returns
    -------
    status : str
        Order status, one of 'complete', 'processing', or 'problem'.
    """
    client = _init_client()
    return client.service.getOrderStatus(order_id)


def order_clear(user, order_id):
    """
    Clear (cancel) and order.

    Parameters
    ----------
    user : str
        Username used to order the data.
    order_id : str or int
        Order id.

    Returns
    -------
    success : bool
        True of order was cleared, False if the clear failed.

    """
    client = _init_client()
    response = client.service.clearOrder(user, order_id)
    if response == 'true':
        return True
    else:
        return False


def order_download(user, order_id, files=None):
    """
    Download files from a ARM Archive order.

    Files are stored in the current working directory, no return.

    Parameters
    ----------
    user : str
        Username
    order_id : str or int
        Order id.
    files : list, str or None, optional.
        Files to download, either a single file, a list of files, or None
        to retrieve all files in the order.

    """
    # log into the FTP server
    ftp = _FTP(_ARM_FTP)
    ftp.login()

    # change to the correct directory
    ftp.cwd(user)
    ftp.cwd(str(order_id))

    # grab the files
    if files is None:
        files = ftp.nlst()
    if isinstance(files, str):
        files = [files]
    for filename in files:
        print("Retrieving:", filename)
        ftp.retrbinary('RETR ' + filename, open(filename, 'wb').write)
    ftp.quit()
    return


def list_order_files(user, order_id):
    """
    List the file in an ARM Archive order.

    Parameters
    ----------
    user : str
        Username
    order_id : str or int
        Order id.

    Returns
    -------
    files : list
        List of files in the order.

    """
    # log into the FTP server
    ftp = _FTP(_ARM_FTP)
    ftp.login()

    # change to the correct directory
    ftp.cwd(user)
    ftp.cwd(str(order_id))

    return ftp.nlst()


def list_orders_ready(user):
    """
    List all Archive orders which are ready for download.

    Parameters
    ----------
    user : str
        Username

    Returns
    -------
    order_ids : list
        List of open order ids for the user.

    """
    # log into the FTP server, change to users directory
    ftp = _FTP(_ARM_FTP)
    ftp.login()
    ftp.cwd(user)
    return ftp.nlst()


# ARM Archive Webservice SOAP Methods:
#
# Implemented
# -----------
# isValidUser(userID)
# getDataStreams()
# getFiles(datastreams, startDate, endDate)
# processOrder(userID, filesNamesList)
# getOrderStatus(sessionID)
# clearOrder(archID,sessionID)
#
# Not Implemented
# ---------------
# getDQRs(datastream, startDate, endDate, measurement)
# main(args)
# processCommonOrder(userID, filesNamesList)    # ???
# processRawOrder(userID, filesNamesList)       # Order with version


def main(args=None):
    """ Main function for use in scripts. """
    import argparse

    # argument parser
    description = ("ARM Archive Python Utility: a tool for searching, "
                   "ordering and managing orders at the ARM Archive")
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(title='valid commands', dest='cmd',
                                       metavar='')

    # datastreams command parser
    ds_parser = subparsers.add_parser(
        'datastreams', help='list datastreams',
        description='List datastreams avialable at Archive')
    ds_parser.add_argument('regex', nargs='?',
                           help='regular expression to filter list')

    # order command parser
    order_parser = subparsers.add_parser(
        'order', help='order files',
        description='Order files from Archive')
    order_parser.add_argument('user', help='archive username')
    order_parser.add_argument('files', nargs='*')
    order_parser.add_argument(
        '-d', '--dates', nargs=3, metavar=('DATASTREAM', 'START', 'END'),
        help='Datastream name, start and ending dates')
    order_parser.add_argument(
        '-f', '--file', metavar=('FILE'),
        help='File to read files from')

    # list command parser
    list_parser = subparsers.add_parser(
        'list', help='list available files ',
        description='List files available in Archive')
    list_parser.add_argument(
        'datastream', help='datastream to list files from')
    list_parser.add_argument(
        'start', help='starting date, YYMMDDDD')
    list_parser.add_argument(
        'end', nargs='?',
        help='ending date, YYMMDDDD, single day if not specified')
    list_parser.add_argument(
        '-r', '--regex', help='regular expression to filter files')

    # cancel command parser
    cancel_parser = subparsers.add_parser(
        'cancel', help='cancel an order',
        description='Cancel an Archive order')
    cancel_parser.add_argument('user', help='archive username')
    cancel_parser.add_argument('order_id', help='order id')

    # status command parser
    status_parser = subparsers.add_parser(
        'status', help='check an orders status',
        description='Check the status of an Archive order')
    status_parser.add_argument('order_id', help='order id')

    # download command parser
    download_parser = subparsers.add_parser(
        'download', help='download an order',
        description='Download an Archive order into the current directory')
    download_parser.add_argument('user', help='archive username')
    download_parser.add_argument('order_id', help='order id')
    download_parser.add_argument(
        '-r', '--regex', help='regular expression to filter files')
    download_parser.add_argument(
        'files', nargs='*',
        help='files to download, if missing all files are downloaded')

    # files command parser
    files_parser = subparsers.add_parser(
        'files', help='list files in an order',
        description='List files in an Archive order')
    files_parser.add_argument('user', help='archive username')
    files_parser.add_argument('order_id', help='order id')

    # ready command parser
    ready_parser = subparsers.add_parser(
        'ready', help='list orders ready to download',
        description='List Archive order that are ready for download')
    ready_parser.add_argument('user', help='archive username')

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args(args)
    # List datastreams, datastreams command
    if args.cmd == 'datastreams':
        for ds in list_datastreams(args.regex):
            print(ds)

    # Order files from Archive, order command
    elif args.cmd == 'order':

        if args.dates is None and args.file is None and len(args.files) == 0:
            raise SystemExit('error: no files to order')

        if len(args.files) != 0:
            files = args.files
        elif args.file is not None:
            files = [l.strip() for l in open(args.file)]
        elif args.dates is not None:
            dataset, start, end = args.dates
            files = list_files(dataset, start, end)

        status, flag = order_files(args.user, files)
        if status:
            print("Success %s file(s) ordered, order_id: %s" % (flag[2],
                                                                flag[1]))
        else:
            print("Order failed, response from server:\n", flag)

    # List files in Archive, list command
    elif args.cmd == 'list':
        fs = list_files(args.datastream, args.start, args.end, args.regex)
        for f in fs:
            print(f)

    # Cancel Archive Order, cancel command
    elif args.cmd == 'cancel':
        print(order_clear(args.user, args.order_id))

    # Order status, status command
    elif args.cmd == 'status':
        print(order_status(args.order_id))

    # Download files from archive, download command
    elif args.cmd == 'download':
        if args.regex is not None:
            files = list_order_files(args.user, args.order_id)
            files = _regex_filter(files, args.regex)
        else:
            if len(args.files) == 0:
                files = None
            else:
                files = args.files

        order_download(args.user, args.order_id, files=files)

    # List files in order, files command
    elif args.cmd == 'files':
        for f in list_order_files(args.user, args.order_id):
            print(f)

    # List Orders which are ready for download, ready command
    elif args.cmd == 'ready':
        for order in list_orders_ready(args.user):
            print(order)

    else:
        parser.print_usage()
        raise SystemExit("\nerror: invalid command '%s'" % (args.command))


if __name__ == "__main__":
    main()
