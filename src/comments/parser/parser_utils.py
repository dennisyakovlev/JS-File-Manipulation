# Author: Dennis Yakovlev

# Related parsing items needed in parsing files.

import re
from src.comments.parser import parser_literals as literals
from src.comments.parser import parser_multi as multi

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
            Hold('d', literals._quote_double_start(currStr)),
            Hold('s', literals._quote_single_start(currStr)),
            Hold('m', multi._comment_multi_start(currStr))
        ]

        if not False in [i.val == -1 for i in arr]:
            return Info(i, retArr)

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
                i += literals._quote_single_end(currStr)
                retArr.append((tempI + minHold.val, i))
            elif minHold.ty == 'd':
                i += literals._quote_double_end(currStr)
                retArr.append((tempI + minHold.val, i))
            else:
                i += multi._comment_multi_end(currStr)

        if not True in [j.lessThan(character) for j in arr]: # if character is located before the start of any found
            if minHold != None and (minHold.ty == 's' or minHold.ty == 'd'):
                retArr.pop()
            return Info(tempI + re.search(f'{char}', s[tempI : ]).span()[1], retArr)

