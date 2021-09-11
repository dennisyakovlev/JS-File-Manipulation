import os
import re

# Add options to remove jsdoc, comments, and line spacing seperately

def _find_startJsDoc(s):
    ''' Find if <s> has starting jsdoc pattern
    '''

    return re.search('^\s*\/\*{2}', s)

def _find_endJsDoc(s):
    ''' Find if <s> has ending jsdoc pattern
    '''

    return re.search('\*\/$', s)

def _convertFile(dir):
    ''' Remove comments from file.
    '''
    f = open(dir, 'r')

    arrFile = []

    line = ' '
    while line:
        line = f.readline()

        if (_find_startJsDoc(line)):
            while line and not _find_endJsDoc(line):
                line = f.readline()
            line = f.readline()

        arrFile.append(line)

    f.close()

    return arrFile

def _wrtieFile(dir, name, arr):

    f = open(os.path.join(dir, name + '.js'), 'w')

    f.writelines(arr)

    f.close()

def _createDir(dir):

    if not os.path.exists(dir):
        os.mkdir(dir)

# depth first search for files
def start(obj, start_path = '', path = ''):
    ''' Remove all comments from files in array. File names do not have to include .js

        <obj> object of format 
        {
            directory: [fileName, ...],
            directory2: [
                {
                    directory3: [fileName, ...],
                    directory4: [fileName, ...],
                },
                fileName, ...
            ]
        }

              where fileName is dict
              {
                  name: fileName,
                  jsdoc: bool, 
                  single: bool,
                  multi: bool
              }
              name - the name of file to be converted. .js extension should NOT be added
              jsdoc - True to remove jsdoc comment
              single - True to remove single line // comments
              multi - True to remove multi line /* */ comments
        <start_path> the base directory to begin searching for files from
    '''
    
    outPath = os.path.join(start_path, 'out', path) # path in the output folder

    if path == '':
        _createDir(outPath)

    if isinstance(obj, str):
        arr = _convertFile(os.path.join(start_path, path, obj + '.js'))
        _wrtieFile(outPath, obj, arr)
        return


    for key in obj:
        _createDir(os.path.join(outPath, key))

        elem = obj[key]

        for item in elem:
            start(item, start_path, os.path.join(path, key))
