# Synchronize documentation with Confluence

## How to run and use the script

This Python script allows to sync the documentation of a repo with a Confluence instance. It is written for Python 3.6 and has only been tested under 3.6, 3.5 and 3.4.

The script can be ran under two modes:

* `create`: posts all the markdown files to Confluence assuming the files don't already exists.
* `delete`: deletes from Confluence all the markdown files found in the repository.

example:

```
$ python3 script.py create
```

or

```
$ python3 script.py delete
```

## Script explanations

The script as a main function which iterates through a directory, starting from the current position where the script was launched.
Depending on the mode in which the script was launched it calls a delete function or creation function.

While iterating through the files, every time the script encounters a directory it creates (or deletes) a simple page indicating what the next section will be about.

If it encounters a markdown file, it converts it in command line with the tool and python package `pandoc`and store the result in a HTML file, which will be open by the script and modified to adjust the images addresses (function `prepare_html()`).

Once the html is ready, the script send an API call to the Confluence instance in order to post(or delete) the content in the knowledge base.

The functions making API calls are:

* `write_data()` => page creation
* `delete_page()` => page deletion
* `get_page_info()` => get the informations of an already existing page (used to get back information from the parent page in this script)

The scripts also uses tool functions:

* `selectLastDir()` => select and return the last directory of a path.
* `removeLastDirFromFilepath()` => remove the last directory of a path and return the path without this directory
* `replaceBetween()` => replace a sub string with another value between two given indexes.
