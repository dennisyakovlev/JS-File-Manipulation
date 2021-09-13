import re

# NOTTTTTTTTTTTTTTe: for node-gyp instead of using node-gyp to compile try taking the macros (to export the c++ functions) and compiling using gcc
#                    manually along with the required v8 files from platform. FIRST try compiling the v8 files using
#                    gcc manually outside the project, then adding in the node-gyp macros

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

def _remove_inner(arr):
    ''' Remove all inner indicies.

        An inner set of quotes will NEVER overlap (as in "oka'y"') with its parent
        set of quotes.

        Ex: "hello 'inside' world"
            the 'inside' is inner indicies
    '''

    arrLocal = arr[:]
    ret = []

    curr = arrLocal.pop()
    while not arrLocal == []:
        i = 0
        while i != len(arrLocal) and not (curr[0] > arrLocal[i][0] and curr[1] < arrLocal[i][1]): # loop until curr is found out to be inner literal
            i += 1

        if i == len(arrLocal): # not inner
            ret.append(curr)
            curr = arrLocal.pop()
        else: # inner
            curr = arrLocal.pop(i)

    ret.append(curr)

    return ret

def _find_normal_single(s):
    ''' Find a single line comment in line where no double quote string literal exist.
        Consequently, any // found WILL be the start of a comment.
    '''

    return re.search('\/\/', s)

def _new_with_literal(s, ignore):
    ''' The line has string literals in it. 

        <ignore> array from _remove_inner(_find_indicies(line))
    '''

    j = 0
    for i in range(len(ignore)):
        ignore_elem = ignore[i]

        match = _find_normal_single(s[j : ignore_elem[0]])

        if not match == None: # found the comment
            return s[0: j + match.span()[0]]

        j = ignore_elem[1]

    match = _find_normal_single(s[j : -1])

    return s[0: j + match.span()[0]] # comment is in last non string literal section
    
def _new_without_literal(s):
    ''' The line has no string literals in it. By extension any //
        in the line IS the start of a comment.
    '''

    index = _find_normal_single(s).span()[0]

    return s[0: index]

def _has_literal(s):
    ''' Whether s has any of ", ', or `.
    '''
    arr = ['"', "'", '`']
    res = [(quote in s) for quote in arr]

    for item in res:
        if item:
            return True
    
    return False

def _parse_single(f, s):
    ''' If single line comment is found, remove it.

        This function does NOT remove lines from the file. No matter what.
        If a line was soley a commend, then it is kept just as empty.
    '''

    if _find_normal_single(s) == None: # // not even in line
        return (f, s)

    if _has_literal(s):
        indices = _find_indicies(s) # match for when a string using " " exists

        if indices == []: # empty indicies indicate a literal character was found ONLY INSIDE a comment
            return (f, _new_without_literal(s) + '\n')

        indices = _remove_inner(indices) # see _remove_inner doc
        indices = sorted(indices, key = lambda tupe : tupe[0]) # sort by first val

        return (f, _new_with_literal(s, indices) + '\n') # add newline to keep original file formatting

    return (f, _new_without_literal(s) + '\n') # add newline to keep original file formatting 
