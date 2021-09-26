# Author: Dennis Yakovlev 

# File for functions related to parsing single line (//) comments
# These comments are at the end of any code and span until the end of the line

import re

def _find_normal_single(s):
    ''' Find a single line comment in line where no double quote string literal exist.
        Consequently, any // found WILL be the start of a comment.
    '''

    return re.search('\/\/', s)

def _comment_single_start(s):
    ''' Look for the start of a single line comment (//).
    '''

    res = re.search(r'\/\/', s)
    return res.span()[0] if res != None else -1