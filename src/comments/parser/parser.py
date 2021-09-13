import re

def _find_double_quote(s):
    ''' Find string literal which uses double quotes
    '''

    return re.finditer(r'\"(\\\"|[^\"])*\"', s)

def _find_single_quote(s):
    ''' Find string literal which uses single quotes
    '''

    return re.finditer(r'\'(\\\'|[^\'])*\'', s)

def _find_back_quote(s):
    ''' Find string literal which uses back quotes
    '''

    return re.finditer(r'`(\\`|[^`])*`', s)

def _find_indicies(s):
    ''' Find all the idicies of the string literals.
    '''

    arr = []

    [arr.append(match.span()) for match in _find_double_quote(s)]
    [arr.append(match.span()) for match in _find_single_quote(s)]
    [arr.append(match.span()) for match in _find_back_quote(s)]

    return arr


def _find_match(s, ignore, func):
    ''' Assume <s> has valid string literals in it. 

        <ignore> array from _remove_inner(_find_indicies(line))
        <func> function to return match
    '''

    j = 0
    for i in range(len(ignore)):
        ignore_elem = ignore[i]

        match = func(s[j : ignore_elem[0]])

        if not match == None: # found the comment
            return j + match.span()[0]

        j = ignore_elem[1]

    match = func(s[j : -1])

    return j + match.span()[0] # comment is in last non string literal section
    