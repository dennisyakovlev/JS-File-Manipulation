import os

from src.comments.comment_types import jsdoc
from src.comments.comment_types import single
from src.comments.comment_types import multi

PROPERTY_NAME_KEY = 'name'
PROPERTY_KEYS = {
    'jsdoc': {
        'default': True,
        'function': jsdoc._parse_jsdoc
    }, 
    'single': {
        'default': True,
        'function': single._parse_single
    }, 
    'multi': {
        'default': True
    }, 
}

def _createDir(dir):

    if not os.path.exists(dir):
        os.mkdir(dir)

def _defaultProp(name):
    ''' Get default properties
    '''

    ret = {PROPERTY_NAME_KEY: name}

    for key in PROPERTY_KEYS:
        ret[key] = PROPERTY_KEYS[key]['default']

    return ret

def _getProp(var):
    ''' Get properties from input.
    '''

    ret = {}

    if isinstance(var, str):
        return _defaultProp(var)

    if PROPERTY_NAME_KEY in var:
        ret[PROPERTY_NAME_KEY] = var[PROPERTY_NAME_KEY]
        var.pop(PROPERTY_NAME_KEY)
    else:
        raise Exception('must have "name" key')

    keys = list(PROPERTY_KEYS.keys())

    for key in var:
        if key in keys:
            ret[key] = var[key]
            keys.pop(keys.index(key))
        else:
            raise Exception(f'"{key}"" invalid key')

    for key in keys: # assign defult to unspecified keys
        ret[key] = PROPERTY_KEYS[key]['default']

    return ret

def _convertFile(dir, properties):
    ''' Remove comments from file as specified with <properties>.
    '''
    f = open(dir, 'r')

    trueKeys = []
    for key in properties:
        if properties[key] == True:
            trueKeys.append(key)

    arrFile = []

    line = ' '
    while line:
        line = f.readline()

        for key in trueKeys:
            tupe = PROPERTY_KEYS[key]['function'](f, line)
            f = tupe[0]
            line = tupe[1]

        arrFile.append(line)

    f.close()

    return arrFile

def _wrtieFile(dir, name, arr):

    f = open(os.path.join(dir, name + '.js'), 'w')

    f.writelines(arr)

    f.close()

def _has_literal(s):
    ''' Whether s has any of ", ', or `.
    '''

    arr = ['"', "'", '`']
    res = [(quote in s) for quote in arr]

    for item in res:
        if item:
            return True
    
    return False

def _remove_inner(arr):
    ''' Remove all inner indicies.

        An inner set of quotes will NEVER overlap (as in "oka'y"') with its parent
        set of quotes.

        Ex: "hello 'inside' world"
            the 'inside' is inner indicies
    '''

    arrLocal = arr[:]
    ret = []

    curr = arrLocal.pop()
    while not arrLocal == []:
        i = 0
        while i != len(arrLocal) and not (curr[0] > arrLocal[i][0] and curr[1] < arrLocal[i][1]): # loop until curr is found out to be inner literal
            i += 1

        if i == len(arrLocal): # not inner
            ret.append(curr)
            curr = arrLocal.pop()
        else: # inner
            curr = arrLocal.pop(i)

    ret.append(curr)

    return ret