# Author: Dennis Yakovlev

# File related to the combined parsing of a line in a file.

import re

from src.comments.parser import parser_single as single
from src.comments.parser import parser_back as back
from src.comments.parser import parser_literals as literals
from src.comments.parser import parser_multi as multi
from src.comments.parser import parser_utils as utils

LITERALS_PROPERTIES = {}

LITERALS_PROPERTIES = {
    '"': {
        'start': literals._quote_double_start,
        'end': literals._quote_double_end
    },
    "'": {
        'start': literals._quote_single_start,
        'end': literals._quote_single_end
    }, 
    '`': {
        'start': back._quote_back_start,
        'end': back._quote_back_end
    }
}

def _find_indicies(s):
    ''' Find all the indicies of the string literal characters.
    '''

    res = utils._search_until(s, '`')

    if res.index == 0: # didnt find `` literal
        return utils._search_until(s, '//')

    ret = utils.Info(0, [])
    while True:
        start = utils._search_until(s[ret.index : ], '`') # starting `
        [ret.arr.append((ret.index + i[0], ret.index + i[1])) for i in start.arr] # add literals outside of ``
        ret.index += start.index # go to starting `

        if back._quote_back_start(s[ret.index : ]) == -1:
            break 

        end = back._quote_back_end(s[ret.index : ]) # ending 
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
    res = _find_indicies(s) # match for all string literal characters in a line
                            # not a gaurentee that a valid string literal exists
    indices = res.arr
    if len(indices) != 0: # empty indicies indicate no possiblly valid string literals
        
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
            # try:
            matchArr = _find(s[j : ignore_elem[0]])
            # except:
                # return []

            _marge_j(j, matchArr, ret)

            j = ignore_elem[1]

        # try:
        matchArr = _find(s[j : -1])
        # except:
            # return []

        _marge_j(j, matchArr, ret)

        return ret

    # no literal characters
    return _find(s)
