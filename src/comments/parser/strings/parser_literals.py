# Author: Dennis Yakovlev

# File for functions related to parsing string literals ('') and ("")

import re

def _quote_double_start(s):
    ''' Look for the start of double quoted ("") string literal.
    '''

    res = re.search(r'\"', s)
    return res.span()[0] if res != None else -1

def _quote_double_end(s):
    ''' Look for the end of double quoted ("") string literal.

        Assume already inside a valid double quoted string literal.
    '''

    res = re.search(r'[^\\\"]\"', s)
    return res.span()[1] if res != None else -1

def _quote_single_start(s):
    ''' Look for the start of single quoted ('') string literal.
    '''

    res = re.search(r'\'', s)
    return res.span()[0] if res != None else -1

def _quote_single_end(s):
    ''' Look for the end of single quoted ('') string literal.

        Assume already inside a valid single quoted string literal.
    '''

    res = re.search(r'[^\\\']\'', s)
    return res.span()[1] if res != None else -1
