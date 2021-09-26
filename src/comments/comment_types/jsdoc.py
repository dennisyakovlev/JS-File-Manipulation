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

def _parse_jsdoc(f, line, parse):
    ''' If jsdoc is found, skip past all the commented lines.

        This function does NOT remove lines from the file. No matter what.
        Blank lines are left in place of the jsdoc comment.
    '''

    ret = ''
    parsed = False

    if (_find_startJsDoc(line)):
        parsed = True
        while line and not _find_endJsDoc(line):
            if parse:
                ret += '\n'
            else:
                ret += line
            line = f.readline()
            
        if parse:
            ret += '\n'
        else:
            ret += line
        line = f.readline()

    return {
        'file': f,
        'line': ret + line,
        'parsed': parsed
    }
