# Author: Denins Yakovlev

# File for functions related to parsing special literals (``) 
# These literals can contain ${} within then which contains special
# parsing rules.

import re
from src.comments.parser import parser_utils as utils

def _quote_back_start(s):
    ''' Look for the start of back quoted (``) string literal.
    '''

    res = re.search(r'`', s)
    return res.span()[0] if res != None else -1

def _parse_bracket(s):
    ''' parse a single ${} inside a ``

        <return> index of ending after closing }
    '''

    startBracket = re.search('\${', s)

    i = 0 # the current index of the str which determines what to search

    if startBracket != None: # found a ${} section inside
                             # means potential for inner ``
        i = startBracket.span()[1]

        endBracket = utils._search_until(s[i : ], '}')

        arr = [(0, max(i - 2, 0))] 
        [arr.append((i + j[0], i + j[1])) for j in endBracket.arr]

        return utils.Info(i + endBracket.index, arr)

    return utils.Info(0, [])

def _parse_brackets(s):
    ''' parse through multiple ${} inside ``.

        <return> index of last ending bracket of a ${}
    '''

    res = _parse_bracket(s)
    i = res.index
    arr = res.arr
    uh = re.search('`', s[i : ]).span()[1]
    while True:
        res = _parse_bracket(s[i : ])
        uh = re.search('`', s[i : ]).span()[1]
        if uh < res.index or res.index == 0:
            break
        [arr.append((i + j[0], i + j[1])) for j in res.arr]
        i += res.index

    return utils.Info(i, arr)
        
def _quote_back_end(s):
    ''' Look for the end of a back quoted (``) string literal.

        <level> how many `` quotes down we are

        Assume already inside a valid back quoted string literal.
    '''

    endBracket = _parse_brackets(s) # get end of ${}

    end = re.search(r'(^`)|([^(\\)]`)', s[endBracket.index : ]).span()[1] # find closing `

    endBracket.arr.append((endBracket.index, endBracket.index + end))
    endBracket.index += end

    return endBracket