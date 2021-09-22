import re

from src.comments.comment_types import single
from src.comments.comment_types import multi
from src.comments import utils

def _find_double_quote(s):
    ''' Look for a pattern which match that of a double quoted ("")
        string literal.
    '''

    return re.finditer(r'\"(\\\"|[^\"])*\"', s)

def _find_single_quote(s):
    ''' Look for a pattern which match that of a single quoted ('')
        string literal.
    '''

    return re.finditer(r'\'(\\\'|[^\'])*\'', s)

def _find_back_quote(s):
    ''' Look for a pattern which match that of a back quoted (``)
        string literal.
    '''

    return re.finditer('`(\\`|[^`])*`', s)

# `` comments arent the same "" or '' comments

LITERALS_PROPERTIES = {}

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

def _quote_double_start(s):
    ''' Look for the start of double quoted ("") string literal.
    '''

    res = re.search(r'\"', s)
    return res.span()[0] if res != None else -1

def _quote_double_end(s):
    ''' Look for the end of double quoted ("") string literal.

        Assume already inside a valid double quoted string literal.
    '''

    res = re.search(r'[^(\\\")]\"', s)
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

    res = re.search(r'[^(\\\')]\'', s)
    return res.span()[1] if res != None else -1

def _quote_back_start(s):
    ''' Look for the start of back quoted (``) string literal.
    '''

    res = re.search(r'`', s)
    return res.span()[0] if res != None else -1

class Info:
    def __init__(self, index, arr) -> None:
        self.index = index
        self.arr = arr

class Hold:
    def __init__(self, ty, val) -> None:
        self.ty = ty
        self.val = val

    def lessThan(self, num):

        return False if self.val == -1 else self.val < num

    def __str__(self) -> str:
        return f'{self.ty} {self.val}, '

def _search_until(s, char):
    ''' Search past '', "", and /**/ in s until char is found

        <return> index of found char, 0 if not found
    '''

    if re.search(f'{char}', s) == None:
        return Info(0, [])

    i = 0
    retArr = []

    while True:
        currStr = s[i : ]

        arr = [
            Hold('d', _quote_double_start(currStr)),
            Hold('s', _quote_single_start(currStr)),
            Hold('m', _comment_multi_start(currStr))
        ]

        character = re.search(f'{char}', currStr).span()[0]

        minHold = None
        # find smallest Hold
        for k in range(len(arr)):
            if minHold == None:
                if arr[k].val != -1:
                    minHold = arr[k]
            else:
                if arr[k].lessThan(minHold.val):
                    minHold = arr[k]

        tempI = i

        if minHold == None:
            pass
        else:
            i += minHold.val
            currStr = s[i : ]
            if minHold.ty == 's':
                i += _quote_single_end(currStr)
                retArr.append((tempI + minHold.val, i))
            elif minHold.ty == 'd':
                i += _quote_double_end(currStr)
                retArr.append((tempI + minHold.val, i))
            else:
                i += _comment_multi_end(currStr)

        if not True in [j.lessThan(character) for j in arr]: # if character is located before the start of any found
            if minHold != None and (minHold.ty == 's' or minHold.ty == 'd'):
                retArr.pop()
            return Info(tempI + re.search(f'{char}', s[tempI : ]).span()[1], retArr)

def _parse_bracket(s):
    ''' parse a single ${} inside a ``

        <return> index of ending after closing }
    '''

    startBracket = re.search('\${', s)

    i = 0 # the current index of the str which determines what to search

    if startBracket != None: # found a ${} section inside
                             # means potential for inner ``
        i = startBracket.span()[1]

        endBracket = _search_until(s[i : ], '}')
        # endBack = _search_until(s[i : ], '`')

        # if endBack.index < endBracket.index:
        #     return Info(0, [])

        arr = [(0, max(i - 2, 0))] 
        [arr.append((i + j[0], i + j[1])) for j in endBracket.arr]

        return Info(i + endBracket.index, arr)

    return Info(0, [])

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

    return Info(i, arr)
        
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

LITERALS_PROPERTIES = {
    '"': {
        'start': _quote_double_start,
        'end': _quote_double_end
    },
    "'": {
        'start': _quote_single_start,
        'end': _quote_single_end
    }, 
    '`': {
        'start': _quote_back_start,
        'end': _quote_back_end
    }
}

def _find_indicies(s):
    ''' Find all the indicies of the string literal characters.
    '''

    res = _search_until(s, '`')

    if res.index == 0: # didnt find `` literal
        return _search_until(s, r'\n')
    
    ret = Info(0, [])
    while True:
        start = _search_until(s[ret.index : ], '`') # starting `
        [ret.arr.append((ret.index + i[0], ret.index + i[1])) for i in start.arr] # add literals outside of ``
        ret.index += start.index # go to starting `

        if _quote_back_start(s[ret.index : ]) == -1:
            break 

        end = _quote_back_end(s[ret.index : ]) # ending 
        [ret.arr.append((ret.index + i[0], ret.index + i[1])) for i in end.arr] # add literals inside of ``
        ret.index += end.index # go to after ending `

    return ret

def _potential_comment(s):
    ''' Whether <s> has a potential comment of /* or //.

        return True if one of the comment characters is found.
    '''

    return (not single._find_normal_single(s) == None) or (not multi._find_normal_multi_start(s) == None)

def _find_comment_beg(s):
    ''' Find begenning of correct comment.

        return object contained 'm' or 's' for comment type and the 
        span of match

        assume there DOES exist a comment
    '''

    # only need to find first case of comment start
    singleStart = single._find_normal_single(s)
    multiStart = multi._find_normal_multi_start(s)


    if (not singleStart == None) and (not multiStart == None): # both types found
        sStart = singleStart.span()[0]
        mStart = multiStart.span()[0]

        if sStart < mStart:
            return {
                'type': 's',
                'start': sStart
            }
        else :
            return {
                'type': 'm',
                'start': mStart
            }
    
    if singleStart is None:
        return {
            'type': 'm',
            'start': multiStart.span()[0]
        }
    else:
        return {
            'type': 's',
            'start': singleStart.span()[0]
        }

def _find(s):
    ''' return array containing indicies in <s> of where comments
        are [start, end) indicies and type 'm' or 's'. 
        return [] if no comments in line.

        s should NOT conatin ANY valid string literals
    '''
    
    ret = []
    
    if _potential_comment(s): # has found comment begin character(s)
        comm = _find_comment_beg(s) # find comment beginning

        if comm['type'] == 'm': # /* start found
                                # potential for multiple /**/ in one line
            if multi._find_normal_multi_end(s) is None: # not a single line /* comment, spans rest of line
                return [{
                    'type': 'm',
                    'span': (comm['start'], len(s))
                }]

            # atleast one single line /* comment
            i = 0
            start = comm['start']
            end = start + multi._find_normal_multi_end(s[start : ]).span()[1]
            while True: # find all /**/ comments
                ret.append({
                    'type': 'm',
                    'span': (start, end)
                })

                startTemp = multi._find_normal_multi_start(s[end : ])

                if startTemp is None:
                    break

                start = end + startTemp.span()[0]
                end = start + multi._find_normal_multi_end(s[start : ]).span()[1]

            startTemp = single._find_normal_single(s[end : ])

            if not startTemp is None: # found // comment at end
                ret.append({
                    'type': 's',
                    'span': (end + startTemp.span()[0], len(s))
                })

            return ret

        return [{ # // start found, rest of line is comment
            'type': 's',
            'span': (single._find_normal_single(s).span()[0], len(s))
        }]
        
    return ret

def _marge_j(j, matchArr, ret):
    ''' Helper function to avoid repetitive code.

        Merge <matchArr> into <ret> while shifting indicies of
        <matchArr> by <j>.
    '''
    
    for obj in matchArr:
        objSpan = obj['span']
        ret.append({
            'type': obj['type'],
            'span': (j + objSpan[0], j + objSpan[1])
        })

# return unsupported comment type of 'u' and log to file
# so user knows to remove manually

def _get_comments(s):
    ''' return array containing indicies in s of where comments
        are [start, end) indicies and type 'm' or 's'. return None if no comments in line.
        this function looks in line which are NOT complete comments.
        in
        str = 'a' /* make str a when in dir C://
                     something
                     something */
        this function would only be used on first line, then the multi
        function would take care of next 2 lines looking for end

        <s> should be a raw line
    '''

    ret = []

    indices = _find_indicies(s) # match for all string literal characters in a line
                                # not a gaurentee that a valid string literal exists
    if len(indices) != 0: # empty indicies indicate no possiblly valid string literals
        
        indices = utils._remove_inner(indices) # see _remove_inner doc
        indices = sorted(indices, key = lambda tupe : tupe[0]) # sort by first val

        # at this point indicies is a list of tuples of which are [start, end) indicies
        # of parts of the string to ignore since they are flagged literals and cannot
        # contain a comment

        j = 0
        # loop through looking for sections which are not valid
        # string literals
        for i in range(len(indices)):
            ignore_elem = indices[i]

            # incase something thats not support happens to be in a line
            try:
                matchArr = _find(s[j : ignore_elem[0]])
            except:
                return []

            _marge_j(j, matchArr, ret)

            j = ignore_elem[1]

        try:
            matchArr = _find(s[j : -1])
        except:
            return []

        _marge_j(j, matchArr, ret)

        return ret

    # no literal characters
    return _find(s)
