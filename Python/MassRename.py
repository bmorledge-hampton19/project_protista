# This script takes a given directory, a substring to search for, and a string to replace that substring with.
# Using this information, the script recursively renames files and directories with the given substring.
# This script is potentially DANGEROUS. Use with care.

import os
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory


def massRename(parentDirectory, searchString: str, replaceString: str, verbose = False):

    assert searchString, "Search string cannot be empty."

    # Iterate through the given directory
    for item in os.listdir(parentDirectory):
        path = os.path.join(parentDirectory,item)

        # Recursively search directories
        if os.path.isdir(path): 
            if verbose: print(f"Recursing into directory: {item}")
            massRename(path, searchString, replaceString)

        # Check for the search string, and replace it if found.
        if searchString in item:

            if verbose: print(f"Found item with search string: {item}")
            newItem = item.replace(searchString, replaceString)
            if verbose: print(f"Replacing with new name: {newItem}")


            try:
                # If all that's changing is case, we need to do an intermediate renaming (IDK, it just works this way).
                if searchString.lower() == replaceString.lower():
                    intermediateItem = item.replace(searchString, replaceString + 'BeN_wUz_HeRe')
                    os.rename(path, os.path.join(parentDirectory, intermediateItem))
                    os.rename(os.path.join(parentDirectory, intermediateItem), os.path.join(parentDirectory, newItem))
                else: os.rename(path, os.path.join(parentDirectory, newItem))
            except PermissionError:
                print(f"WARNING: Permission denied at {path}\nUnable to rename.")



def main():

    #Create the Tkinter UI
    with TkinterDialog(workingDirectory=getDataDirectory()) as dialog:
        dialog.createFileSelector("Parent Directory:", 0, directory = True)
        dialog.createTextField("String to search for:", 1, 0, defaultText='')
        dialog.createTextField("String to replace with:", 2, 0, defaultText='')

    selections = dialog.selections
    massRename(selections.getIndividualFilePaths()[0], selections.getTextEntries()[0],
               selections.getTextEntries()[1])

if __name__ == "__main__": main()