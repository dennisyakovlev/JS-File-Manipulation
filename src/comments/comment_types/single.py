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
    ''' If single line comment is found, remove it.

        This function does NOT remove lines from the file. No matter what.
        If a line was soley a commend, then it is kept just as empty.
    '''

    if _find_normal_single(s) == None: # // not even in line
        return (f, s)

    if utils._has_literal(s):
        indices = ps._find_indicies(s) # match for when ", ', or ` exists in a line
                                    # not a gaurentee that a string literal exists

        if indices == []: # empty indicies indicate a literal character was found ONLY INSIDE a comment
            return (f, _new_without_literal(s) + '\n')

        indices = utils._remove_inner(indices) # see _remove_inner doc
        indices = sorted(indices, key = lambda tupe : tupe[0]) # sort by first val

        start_match = ps._find_match(s, indices, _find_normal_single) # find start of // comment
        return (f, s[0: start_match] + '\n')

    return (f, _new_without_literal(s) + '\n') # add newline to keep original file formatting 
