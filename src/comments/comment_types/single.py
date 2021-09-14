import re

from src.comments.parser import parser as ps
from src.comments import utils

def _find_normal_single(s):
    ''' Find a single line comment in line where no double quote string literal exist.
        Consequently, any // found WILL be the start of a comment.
    '''

    return re.search('\/\/', s)

def _new_without_literal(s):
    ''' The line has no string literals in it. By extension any //
        in the line IS the start of a comment.
    '''

    index = _find_normal_single(s).span()[0]

    return s[0: index]

def _parse_single(f, s):
    ''' If single line comment is found, remove the comment from the line.

        This function does NOT remove lines from the file. No matter what.
        If a line was soley a comment, then it is kept just as empty.
    '''

    commentArr = ps._get_comments(s)

    if len(commentArr) != 0: # has atleast one comment
        last = commentArr.pop() # // comment will always be last comment

        if last['type'] == 's': # // comment
            return (f, s[0 : last['span'][0]] + '\n')

    return (f, s)