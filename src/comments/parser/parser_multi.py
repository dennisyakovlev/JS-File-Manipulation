# Author: Denins Yakovlev

# File for functions related to parsing multi line (/**/) comments
# These comments can be multi line or single line and
# nested within code

import re

def _comment_multi_start(s):
    ''' Look for the start of multi line (/**/) comment.
    '''

    res = re.search(r'\/\*', s)
    return res.span()[0] if res != None else -1

def _comment_multi_end(s):
    ''' Look for the end of multi line (/**/) comment.
    '''

    res = re.search(r'\*\/', s)
    return res.span()[1] if res != None else -1

def _find_normal_multi_start(s):
    ''' Find the start of a multi line comment character (/*). 
    '''

    return re.search(r'\/\*', s)

def _find_normal_multi_end(s):
    ''' Find the end of a multi line comment character (*/). 
    '''

    return re.search(r'\*\/', s)
