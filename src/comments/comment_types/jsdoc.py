import re

# JsDoc comment should NOT have any text infront of them except for whitespce.

def _find_startJsDoc(s):
    ''' Find if <s> has starting jsdoc pattern
    '''

    return re.search('^\s*\/\*{2}', s)

def _find_endJsDoc(s):
    ''' Find if <s> has ending jsdoc pattern
    '''

    return re.search('\*\/$', s)

def _parse_jsdoc(f, line):
    ''' If jsdoc is found, skip past all the commented lines.

        This function does NOT remove lines from the file. No matter what.
        Blank lines are left in place of the jsdoc comment.
    '''
    ret = ''

    if (_find_startJsDoc(line)):
        while line and not _find_endJsDoc(line):
            line = f.readline()
            ret += '\n'
        line = f.readline()
        ret += '\n'

    return (f, ret + line)
