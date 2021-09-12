import os
from src import jsdoc
from src import single
from src import multi

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
