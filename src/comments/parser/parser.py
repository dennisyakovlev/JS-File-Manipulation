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

    return re.finditer(r'`(\\`|[^`])*`', s)

def _find_indicies(s):
    ''' Find all the idicies of the string literal characters.
    '''

    arr = []

    [arr.append(match.span()) for match in _find_double_quote(s)]
    [arr.append(match.span()) for match in _find_single_quote(s)]
    [arr.append(match.span()) for match in _find_back_quote(s)]

    return arr

# should be able to match multiple sections for multiple inline /**/ comments

# currently matches the // inside the /**/, need to check if inside a /**/ comment

def _find_match(s, ignore, func):
    ''' Assume <s> has valid string literals in it. 

        <ignore> array from _remove_inner(_find_indicies(line))
        <func> function to return match

        <return> tuple of:
            - start index of section which comment is found in
            - index of start of comment
    '''
    print('the string', s)
    j = 0
    for i in range(len(ignore)):
        ignore_elem = ignore[i]

        match = func(s[j : ignore_elem[0]])
        print('match', ignore_elem, match)
        if not match == None: # found the comment
            return (j, j + match.span()[0])

        j = ignore_elem[1]

    match = func(s[j : -1])

    return (j, j + match.span()[0]) # comment is in last non string literal section
    
def _is_first(s, ty):
    ''' Whether // appears before /* of vice versa.
        If <ty> is 's' then, look for // first.
        If <ty> is 'm' then look for /* first

        Return true if selected character appears first OR 
        the other character doesnt appear.
    '''

    first = None
    second = None

    if ty == 'm':
        first = multi._find_normal_multi_start(s)
        second = single._find_normal_single(s)
    else:
        first = single._find_normal_single(s)
        second = multi._find_normal_multi_start(s)

    if second is None:
        return False

    return first.span()[0] < second.span()[0]

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

    sStart = singleStart.span()[0]
    mStart = multiStart.span()[0]

    if (not singleStart == None) and (not multiStart == None): # both types found
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
            'start': mStart
        }
    else:
        return {
            'type': 's',
            'start': sStart
        }

def _find(s):
    ''' return array containing indicies in s of where comments
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
