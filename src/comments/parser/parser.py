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

def _quote_double_start(s):
    ''' Look for the start of double quoted ("") string literal.
    '''

    return re.search(r'\"', s).span()[0]

def _quote_double_end(s):
    ''' Look for the end of double quoted ("") string literal.

        Assume already inside a valid double quoted string literal.
    '''

    return re.search(r'[^(\\\")]\"', s).span()[1]

def _quote_single_start(s):
    ''' Look for the start of single quoted ('') string literal.
    '''

    return re.search(r'\'', s).span()[0]

def _quote_single_end(s):
    ''' Look for the end of single quoted ('') string literal.

        Assume already inside a valid single quoted string literal.
    '''

    return re.search(r'[^(\\\')]\'', s).span()[1]

def _quote_back_start(s):
    ''' Look for the start of back quoted (``) string literal.
    '''

    return re.search(r'`', s).span()[0]

# need to go through and return indicies of found valid literals
# as this is the original point of _find_indicies

def _parse_bracket(s, level = 0):
    ''' parse a single ${} inside a ``

        <return> index of ending after closing }
    '''

    # needs to now account for inner `` and recurse

    startBracket = re.search('\${', s)

    i = 0 # the current index of the str which determines what to search

    if startBracket != None: # found a ${} section inside
                             # means potential for inner ``
        i = startBracket.span()[1]

        multiCommentStart = multi._find_normal_multi_start(s[i : ])

        if multiCommentStart != None: # found a /* character
                                      # finding this outside literal means single line /**/ comment nested in the ${}
            # NEED TO DO FOLLOWING
            # OR encounter2 a ` outside a /**/ comment, which indicates a new literal, add a level and recurse

            # found a /*, mean a /**/ comment exists
            # must loop ignoring whats inside /**/ looking for closing }
            # after loop, i will be after closing }
            while True:
                i += multiCommentStart.span()[1] # move past /*
                multiCommentEnd = multi._find_normal_multi_end(s[i : ]) # find */
                i += multiCommentEnd.span()[1] # move past */
                
                endBracket = re.search(r'}', s[i  : ]) # find }

                multiCommentStart = multi._find_normal_multi_start(s[i : ]) # find potential /*
                if multiCommentStart != None: # found new /*, will be a /**/ comment
                    if multiCommentStart.span()[0] < endBracket.span()[0]: # the found } after /*
                        continue
                    else: # /**/ exists somewhere after closing } 
                        i += endBracket.span()[1] # move past }
                        break
                else: # no more /**/ comments, found ending }
                    i += endBracket.span()[1] # move past }
                    break                
            
            # can now find ` normally ignore valid string literals since they cant exist inside
            # a `` comment they just count as another character
            i += re.search(r'[^(\\\`)]`', s[i : ]).span()[1]

            return i

    return 0

def _parse_brackets(s):
    ''' parse through multiple ${} inside ``.

        <return> index of last ending bracket of a ${}
    '''

    index = _parse_bracket(s)

    i = 0
    while index != 0:
        i += index

        index = _parse_bracket(s[i : ])

    return i
        

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
