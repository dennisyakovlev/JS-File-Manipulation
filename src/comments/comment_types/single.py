# Author: Dennis Yakovlev

# File related to the modification of any single line (//) comments in
# a line.

from src.comments.parser import parser as ps

def _parse_single(f, line, parse):
    ''' If single line comment is found, remove the comment from the line.
    '''

    if not parse:
        return {
            'file': f,
            'line': line,
            'parsed': False
        }

    commentArr = ps._get_comments(line)

    if len(commentArr) != 0: # has atleast one comment
        last = commentArr.pop() # // comment will always be last comment

        if last['type'] == 's': # // comment
            return {
                'file': f,
                'line': line[0 : last['span'][0]] + (' ' * (last['span'][1] - last['span'][0])) + '\n',
                'parsed': False
            }

    return {
        'file': f,
        'line': line,
        'parsed': False
    }