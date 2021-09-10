import os

def _convertFile(dir):
    ''' Remove comments from file.
    '''
    f = open(dir)

    for line in f:
        print(line)

# depth first search for files
def start(obj, start_path = '', path = ''):
    ''' Remove all comments from files in array. File names do not have to include .js

        <obj> object of format 
        {
            directory: [fileName, ...]
            directory2: [
                {
                    directory3: [fileName, ...],
                    directory4: [fileName, ...],
                },
                fileName, ...
            ]
        }

              where fileName is the name of file to be converted. .js is not needed
        <start_path> the base directory to begin searching for files from
    '''

    if isinstance(obj, str):
        _convertFile(os.path.join(start_path, path, obj + '.js'))
        return

    for key in obj:
        elem = obj[key]

        for item in elem:
            start(item, start_path, os.path.join(path, key))





