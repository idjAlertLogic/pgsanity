#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
# The following two lines are to work around Python's apparently broken pipe
# handling.  For more information see: http://docs.python.org/library/signal.html
# http://newbebweb.blogspot.co.uk/2012/02/python-head-ioerror-errno-32-broken.html
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)
import argparse
import sys

from pgsanity import sqlprep
from pgsanity import ecpg

def get_config(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Check syntax of SQL for PostgreSQL')
    parser.add_argument('files', nargs='*', default=None)
    return parser.parse_args(argv)

def check_file(filename=None):
    """
    Check whether an input file is valid PostgreSQL. If no filename is
    passed, STDIN is checked.

    Returns a status code: 0 if the input is valid, 1 if invalid.
    """
    # either work with sys.stdin or open the file
    if filename is not None:
        with open(filename, "r") as filelike:
            sql_string = filelike.read()
    else:
        with sys.stdin as filelike:
            sql_string = sys.stdin.read()

    results = check_string(sql_string)
    if results:
        print_results(filename, results)
        return 1
    return 0

def check_string(sql_string):
    """
    Check whether a string is valid PostgreSQL. Returns a list of messages
    from ecpg, which will be the empty list if the input was valid, or a
    list of error messages otherwise.
    """
    prepped_sql = sqlprep.prepare_sql(sql_string)
    results = []
    for (line_offset, sql) in prepped_sql:
        success, msglist = ecpg.check_syntax(line_offset, sql)
        if not success:
            results.extend(msglist)
    return results

def check_files(files):
    if files is None or len(files) == 0:
        return check_file()
    else:
        accumulator = 0
        for filename in files:
            accumulator |= check_file(filename)
        return accumulator

def print_results(filename, results):
    prefix = ""
    if filename is not None:
        print("File: " + filename + ":")
        prefix = "  "
    for msg in results:
        print(prefix + "Error: " + msg)

def main():
    config = get_config()
    return check_files(config.files)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
