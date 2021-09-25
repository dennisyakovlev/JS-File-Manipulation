import re

from src.comments.parser import parser as ps

def _parse_single(f, s):
    ''' If single line comment is found, remove the comment from the line.

        This function does NOT remove lines from the file. No matter what.
        If a line was soley a comment, then it is kept just as empty.
    '''

    commentArr = ps._get_comments(s)

    if len(commentArr) != 0: # has atleast one comment
        last = commentArr.pop() # // comment will always be last comment

        if last['type'] == 's': # // comment
            return (f, s[0 : last['span'][0]] + '\n')

    return (f, s)