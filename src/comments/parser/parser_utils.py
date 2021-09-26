# Author: Dennis Yakovlev

# Related parsing items needed in parsing files.

import re
from src.comments.parser.strings import parser_literals as literals
from src.comments.parser.comments import parser_multi as multi
from src.comments.parser.comments import parser_single as single

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

def _found_any(arr):
    ''' Checks for array of Hold and whether they all are -1.

        <return> True if every Hold in <arr> has value -1. 
    '''

    return not False in [i.val == -1 for i in arr]

def _find_min_hold(arr):
    ''' Find the minimum hold value in <arr>, which is array of Hold.
    '''

    minHold = None

    for k in range(len(arr)):
        if minHold == None:
            if arr[k].val != -1:
                minHold = arr[k]
        else:
            if arr[k].lessThan(minHold.val):
                minHold = arr[k]

    return minHold

def _search_until(s, char):
    ''' Search past '', "", /**/ AND search until // in <s> until char is found

        <return> index of found char, 0 if not found and list of found 
                 literal indicies. 
    '''

    if re.search(f'{char}', s) == None:
        return Info(0, [])

    i = 0
    retArr = []

    while True:
        currStr = s[i : ]

        arr = [
            Hold('d', literals._quote_double_start(currStr)),
            Hold('s', literals._quote_single_start(currStr)),
            Hold('m', multi._comment_multi_start(currStr)),
            Hold('c', single._comment_single_start(currStr))
        ]

        if _found_any(arr): # didnt find literal
            return Info(i, retArr)

        # character = re.search(f'{char}', currStr).span()[0]
        character = re.search(f'{char}', currStr)
        if character == None:
            return Info(0, [])

        character = character.span()[0]

        # MOVED THIS TO END FOR SOME REASON
        if not True in [j.lessThan(character) for j in arr]: # if character is located before the start of any found
            return Info(i + re.search(f'{char}', s[i : ]).span()[1], retArr)

        minHold = _find_min_hold(arr)

        tempI = i

        if minHold == None:
            pass
        else:
            i += minHold.val
            currStr = s[i : ]
            if minHold.ty == 's':
                i += literals._quote_single_end(currStr)
                retArr.append((tempI + minHold.val, i))
            elif minHold.ty == 'd':
                i += literals._quote_double_end(currStr)
                retArr.append((tempI + minHold.val, i))
            elif minHold.ty == 'm':
                end = multi._comment_multi_end(currStr)
                if end == -1:
                    return Info(tempI + minHold.val + end, retArr)

                i += end
            else:
                return Info(tempI + minHold.val, retArr)


        if not True in [j.lessThan(character) for j in arr]: # if character is located before the start of any found
            # if minHold != None and (minHold.ty == 's' or minHold.ty == 'd'):
                # retArr.pop()
            if minHold != None:
                retArr.pop()
            return Info(tempI + re.search(f'{char}', s[tempI : ]).span()[1], retArr)

def _search_comments(s):
    ''' return array containing indicies in <s> of where comments
        are [start, end) indicies and type 'm' or 's'. 
        return [] if no comments in line.

        s should NOT conatin ANY valid string literals
    '''

    i = 0
    retArr = []

    while True:
        currStr = s[i : ]

        arr = [
            Hold('m', multi._comment_multi_start(currStr)),
            Hold('s', single._comment_single_start(currStr)),
        ]

        if _found_any(arr): # didnt find comments
            return retArr

        minHold = _find_min_hold(arr)

        tempI = i

        if minHold == None:
            break

        i += minHold.val
        currStr = s[i : ]
        if minHold.ty == 'm':
            end = multi._comment_multi_end(currStr)
            if end == -1: # found start of multiple line /**/ comment
                retArr.append({
                    'type': 'M',
                    'span': (i, i + len(currStr))
                })

                return retArr

            retArr.append({
                'type': 'm',
                'span': (i, i + end)
            })

            i += end

        else:
            retArr.append({
                'type': 's',
                'span': (i, i + len(currStr))
            })

            i += len(currStr)
