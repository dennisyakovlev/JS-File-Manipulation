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

    if (_find_startJsDoc(line)):
        while line and not _find_endJsDoc(line):
            line = f.readline()
        line = f.readline()

    return (f, line)
    
def _find_single(s):
    ''' Find single line comments
    '''
    pass

def _parse_single(f, line):
    if (_find_single(line)):
        line = f.readline()

    return (f, line)
