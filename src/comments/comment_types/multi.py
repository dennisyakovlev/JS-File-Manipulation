# Author: Dennis Yakovlev

# Related to the modification of any ret containing or compassed by
# a /**/ comment.

from src.comments.parser import parser as ps
from src.comments.parser.comments import parser_multi as multi

# note when parsing a multiline comment,
# do not exclude the entire line of the ending multiline comment
# instead parse to the closing */

def _parse_multi(f, line, parse):
    '''
    '''

    commentArr = ps._get_comments(line)

    if len(commentArr) != 0:

        ret = ''
        j = 0

        for i in range(len(commentArr) - 1): # for every except last comment
            elem = commentArr[i]

            ret += line[j : elem['span'][0]]
            if parse:
                ret += ' ' * (elem['span'][1] - elem['span'][0])
            else:
                ret += line[elem['span'][0] : elem['span'][1]]

            j = elem['span'][1]

        elem = commentArr[-1]

        if elem['type'] == 's': # single line comment is last comment
                                # means it goes to end of line
            ret += line[j : ]
        else: # multi line comment is last comment

            if elem['type'] == 'M': # multiple line /**/ comment

                if parse:
                    ret += line[j : elem['span'][0]] + (' ' * (len(line[elem['span'][0] : ]) - 1)) + '\n'
                else:
                    ret += line
                line = f.readline()

                while multi._find_normal_multi_end(line) == None:
                    if parse:
                        ret += (' ' * (len(line) - 1)) + '\n'
                    else:
                        ret += line
                    line = f.readline()

                if parse:
                    ret += (' ' * (len(line) - 1)) + '\n'
                else:
                    ret += line

                return {
                    'file': f,
                    'line': ret,
                    'parsed': True
                }

            ret += line[j : elem['span'][0]]
            if parse:
                ret += ' ' * (elem['span'][1] - elem['span'][0] - 1)
            else:
                ret += line[elem['span'][0] : elem['span'][1]]
            ret += line[elem['span'][1] : ]

        return {
            'file': f,
            'line': ret,
            'parsed': False
        }

    return {
        'file': f,
        'line': line,
        'parsed': False
    }
