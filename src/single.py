import re

# NOTTTTTTTTTTTTTTe: for node-gyp instead of using node-gyp to compile try taking the macros (to export the c++ functions) and compiling using gcc
#                    manually along with the required v8 files from platform. FIRST try compiling the v8 files using
#                    gcc manually outside the project, then adding in the node-gyp macros

def _find_double_quote(s):
    ''' Find string literal which uses double quotes
    '''

    return re.finditer(r'\"(\\\"|[^\"])*\"', s)

# can have string inside another string like `${'word'}`, the indicies will overlap, need to remove the overlaped indicies

def _find_indicies(s):
    ''' Find all the idicies of the string literals made using double quotes.
    '''

    matches = _find_double_quote(s)

    return [match.span() for match in matches]


def _find_normal_single(s):
    ''' Find a single line comment in line where no double quote string literal exist.
        Consequently, any // found WILL be the start of a comment.
    '''

    return re.search('\/\/', s)

def _new_with_double_quote(s, ignore):

    j = 0
    for i in range(len(ignore)):
        ignore_elem = ignore[i]

        match = _find_normal_single(s[j : ignore_elem[0]])

        if not match == None: # found the comment
            return s[0: j + match.span()[0]]

        j = ignore_elem[1]

    match = _find_normal_single(s[j : -1])

    return s[0: j + match.span()[0]] # comment is in last non string literal section
    

def _new_without_double_single(s):

    index = _find_normal_single(s).span()[0]

    # return '\n' if index == 0 else s[0: index]
    return s[0: index]

def _parse_single(f, s):
    ''' If single line comment is found, remove it.
    '''

    if _find_normal_single(s) == None: # // not even in line
        return (f, s)

    if '"' in s:
        indices = _find_indicies(s) # match for when a string using " " exists

        if len(indices) > 0:
            return (f, _new_with_double_quote(s, indices) + '\n')

    return (f, _new_without_double_single(s) + '\n')     


# a line can have all 3 types of string literals `` "" '', check for all for all of them
# then add them to the indicies to be ignored