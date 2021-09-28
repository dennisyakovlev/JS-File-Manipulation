# Javascript comment remover

## Contents

* [Aim](#Project-aim)
* [Usage](#Usage)
* [Documentation](#Documentation)
* [Example](#Example-usage)

## Project aim

Python library to allow for removal of comments from javascript code.

## Usage

Import the module JsManipulate from src/comments.

Function ```start``` with runs the module.

Changed files will be outputted to ```start_path/out```.

## Documentation

```JsManipulate.start(obj, start_path)```

```obj``` - Python dictionary of the format
```python
{
    dirNoSubDir: [properties, ...],
    dirWithSubDir: [
        {
            subDir1: [properties, ...],
            subDir2: [properties, ...],
        },
        properties, ...
    ]
}
```
where fileName is a dictionary of the form
```python
{
    name: fileName,
    jsdoc [optional]: bool, 
    single [optional]: bool,
    multi [optional]: bool
}
```

```name``` - the name of file to be converted. .js extension should NOT be added. ie the file "Foo.js" should be "Foo" \
```jsdoc``` - ```True``` to remove jsdoc comment (/** \*/), ```False``` to keep \
```single``` - ```True``` to remove single line (//) comments, ```False``` to keep \
```multi``` - ```True``` to remove multi lined (/* */) comments, ```False``` to keep

Not adding a key will set it to its default value. \
To set default to all, can have dict with {'name': fileName} or simply 'fileName'.

```start_path``` - string of the base directory to begin searching for files from

## Example usage

An example usage for the following directiory structure with the goal of removing all comments in all files in Project/client. 

If ```remover.py``` is the file calling ```start```.

```
Project
|   main.py
|   server.js
|   remover.py
|
|---src
|       source code for comment remover   
|
|---routes
|       route1.js
|       route2.js
|
|---client
|   |   main.js
|   |
|   |---svg
|   |   |
|   |   |---curves   
|   |   |       curve1.js
|   |   |       curve2.js
|   |   |
|   |   |---lines
|   |   |       line1.js
|   |   |       line2.js
|   |   
|   |---animations
|   |       click.js
|   |       hide.js
```

The python code could look something like
```python
from src.comments import JsManipulate as manip
import os

init_path = os.getcwd()

manip.start({
    'client': [
        'main',
        {
            'svg': [
                { 'curves': ['curve1', 'curve2'] },
                { 'lines': ['line1', 'line2'] }
            ]
        },
        {
            'animations': ['click', 'hide']
        }
    ]
}, init_path)
```