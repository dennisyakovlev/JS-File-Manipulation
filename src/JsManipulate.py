import os

from src import utils

def _isBaseCase(obj):
    ''' Determine whether object is property object.
    '''

    # if PROPERTY_NAME_KEY is a directory then its value will be a list
    if utils.PROPERTY_NAME_KEY in obj and isinstance(obj[utils.PROPERTY_NAME_KEY], list):
        return False
        
    return True if utils.PROPERTY_NAME_KEY in obj else False # if PROPERTY_NAME_KEY is a key in object, then property object

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
              jsdoc - True to remove jsdoc comment, False to keep
              single - True to remove single line // comments, False to keep
              multi - True to remove multi line /* */ comments, False to keep

              - Not adding a key will set it to its default value.
              - If want to set default to all, instead of dict simply have the file name as a string OR
                dict with just {'name': fileName}.

        <start_path> the base directory to begin searching for files from
    '''
    
    outPath = os.path.join(start_path, 'out', path) # path in the output folder

    if path == '':
        utils._createDir(outPath)

    # base case 
    if _isBaseCase(obj):
        properties = utils._getProp(obj)
        arr = utils._convertFile(os.path.join(start_path, path, properties[utils.PROPERTY_NAME_KEY] + '.js'), properties)
        utils._wrtieFile(outPath, properties[utils.PROPERTY_NAME_KEY], arr)
        return

    for key in obj:
        utils._createDir(os.path.join(outPath, key))

        elem = obj[key]

        for item in elem:
            start(item, start_path, os.path.join(path, key))
