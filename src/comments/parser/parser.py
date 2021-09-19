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
    return res.span()[1] if res != None else -1

# need to go through and return indicies of found valid literals
# as this is the original point of _find_indicies

def _search_literals_until(s, char):
    ''' search <s> for all literals until <char> is found outside a literal

        search only "" and '' literals not ``

        <return> index of found <char>
    '''

    if re.search(f'{char}', s) == None:
        return 0

    i = 0

    while True:
        currStr = s[i : ]

        double = _quote_double_start(currStr) + 1 # add one to not index currStr later
        single = _quote_single_start(currStr) + 1 # add one to not index currStr later
        
        character = re.search(f'{char}', currStr).span()[0]

        if character >= double or character >= single: # if character is located before the start of either possible literals
            i += character + len(char)
            break

        if double < single:
            i += _quote_double_end(currStr)
        else:
            i += _quote_single_end(currStr)

    return i

def _parse_bracket(s, level = 0):
    ''' parse a single ${} inside a ``

        <return> index of ending after closing }
    '''

    # needs to now account for inner `` and recurse

    startBracket = re.search('\${', s)

    i = 0 # the current index of the str which determines what to search

    # Accounts for string literals inside ${} by skipping over them and only caring for /**/ comments
    if startBracket != None: # found a ${} section inside
                             # means potential for inner ``
        i = startBracket.span()[1]
        multiCommentStart = _search_literals_until(s[i : ], r'\/\*')


        # if multiCommentStart != None: # found a /* character
        if multiCommentStart != 0 and multiCommentStart < _search_literals_until(s[i : ], r'}'): # found a /* character before a } character
                                                                                                 # this does not make } the closing }
                                                                                                 # finding this outside literal means single line /**/ comment nested in the ${}
            # NEED TO DO FOLLOWING
            # OR encounter2 a ` outside a /**/ comment, which indicates a new literal, add a level and recurse

            # found a /*, means a /**/ comment exists
            # must loop ignoring whats inside /**/ looking for closing }
            # after loop, i will be after closing }
            while True:
                i += multiCommentStart # move past /*
                multiCommentEnd = multi._find_normal_multi_end(s[i : ]) # find */
                i += multiCommentEnd.span()[1] # move past */
                
                endBracket = re.search(r'}', s[i  : ]) # find }

                multiCommentStart = _search_literals_until(s[i : ], r'\/\*') # find potential /*
                if multiCommentStart != 0: # found new /*, will be a /**/ comment
                    if multiCommentStart < endBracket.span()[0]: # the found } after /*
                        continue
                    else: # /**/ exists somewhere after closing } 
                        i += endBracket.span()[1] # move past }
                        break
                else: # no more /**/ comments, found ending }
                    i += endBracket.span()[1] # move past }
                    break                
            
            return i

        return i + _search_literals_until(s[i : ], '}')

    return 0

class Hold:
    def __init__(self, ty, val) -> None:
        self.ty = ty
        self.val = val

    def lessThan(self, num):

        return False if self.val == -1 else self.val < num

    def __str__(self) -> str:
        return f'{self.ty} {self.val}, '

def _temp(currStr):

    return [
        Hold('d', _quote_double_start(currStr)),
        Hold('s', _quote_single_start(currStr)),
        Hold('m', _comment_multi_start(currStr))
    ]

def _search_until(s, char):
    ''' Search past '', "", and /**/ in s until char is found

        <return> index of found char, 0 if not found
    '''

    if re.search(f'{char}', s) == None:
        return 0

    i = 0

    while True:
        currStr = s[i : ]

        arr = _temp(currStr)

        character = re.search(f'{char}', currStr).span()[1]

        # WAS HERE

        minHold = None
        # find smallest Hold
        for k in range(len(arr)):
            if minHold == None:
                if arr[k].val != -1:
                    minHold = arr[k]
            else:
                if arr[k].lessThan(minHold.val):
                    minHold = arr[k]

        i += 1 # increment past the found starting character so the the find end
               # function does not pick it up
        currStr = s[i : ]

        if minHold.ty == 's':
            i += _quote_single_end(currStr)
        elif minHold.ty == 'd':
            i += _quote_double_end(currStr)
        else:
            i += _comment_multi_end(currStr)

        if not True in [i.lessThan(character) for i in arr]: # if character is located before the start of any found
            i += re.search(f'{char}', s[i : ]).span()[1]
            break

    return i

def _parse_bracket_temp(s, level = 0):
    ''' parse a single ${} inside a ``

        <return> index of ending after closing }
    '''

    # needs to now account for inner `` and recurse

    startBracket = re.search('\${', s)

    i = 0 # the current index of the str which determines what to search

    # Accounts for string literals inside ${} by skipping over them and only caring for /**/ comments
    if startBracket != None: # found a ${} section inside
                             # means potential for inner ``
        i = startBracket.span()[1]

        endBracket = _search_until(s[i : ], '}')
        innerBack = _search_until(s[i : ], '`')

        if endBracket < innerBack: # found } before an inner `` quote
            return i + endBracket
        else: # found inner `` before end }
            return -1 # should recurse

    return 0

def _parse_brackets(s):
    ''' parse through multiple ${} inside ``.

        <return> index of last ending bracket of a ${}
    '''
    print('line:', s)

    index = _parse_bracket_temp(s)
    i = index
    while index != 0:
        print(s[ : i])
        index = _parse_bracket_temp(s[i : ])
        i += index
        
    print(s[:i])



    return i + re.search(r'`', s[i : ]).span()[1]
        
def _quote_back_end(s):
    ''' Look for the end of a back quoted (``) string literal.

        <level> how many `` quotes down we are

        Assume already inside a valid back quoted string literal.
    '''

    endBracket = _parse_brackets(s)
    if endBracket != 0:
        return endBracket

    return re.search(r'[^(\\\`)]`', s).span()[1] # no ${} means no possibilty for /**/ comment, first ` will be end

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
    ''' Find all the idicies of the string literal characters.
    '''

    arr = []

    for i in range(len(s)):
        if s[i] in utils.LITERALS_ARR: # found literal character
            pass

    # [arr.append(match.span()) for match in _find_double_quote(s)]
    # [arr.append(match.span()) for match in _find_single_quote(s)]
    # print('curr', arr)
    # # inside the current indicies are VALID "" and '' comments, ignore all `
    # # now go about finding the `` comments 
    # [arr.append(match.span()) for match in _find_back_quote(s)]

    # FIRST parse any `` comments, and that will return its respective list of ignore
    # then parse "" and '' comments

    return arr

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
