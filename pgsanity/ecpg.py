from __future__ import print_function
import subprocess
import re
import os

def check_syntax(line_offset, string):
    """ Check syntax of a string of PostgreSQL-dialect SQL """
    args = ["ecpg", "-o", "-", "-"]

    with open(os.devnull, "w") as devnull:
        try:
            proc = subprocess.Popen(args, shell=False,
                                    stdout=devnull,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    universal_newlines=True)
            _, err = proc.communicate(string)
        except OSError:
            msg = "Unable to execute 'ecpg', you likely need to install it.'"
            raise OSError(msg)
        if proc.returncode == 0:
            return (True, [])
        else:
            return (False, parse_error(line_offset, err))

def parse_error(line_offset, error):
    # The split generates a trailing empty line
    errlist = filter(lambda e: e != '', error.split('stdin'))
    msglist = []
    for e in errlist:
        e = re.findall(r":([0-9]*): ERROR:(.*)", e.translate(None, '\n'))
        msglist.append('line ' + repr(int(e[0][0]) + line_offset) + ':' + e[0][1])
    return msglist
