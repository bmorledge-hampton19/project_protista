from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
from typing import List
import os


def trimDuplicates(inputFilePaths: List[str], keyColumns = [0,1,2]):

    for inputFilePath in inputFilePaths:

        print("\nWorking in",os.path.basename(inputFilePath))

        # Keep track of how many duplicate rows are found and removed.
        rowsRemoved = 0

        # Create a file to output results to.
        noDupsFilePath = inputFilePath.rsplit('.',1)[0] + "_no_dups.bed"

        # Iterate through the sorted reads file, writing each line to the new file but omitting any duplicate entries beyond the first.
        print("Removing excess duplicates...")
        with open(inputFilePath, 'r') as inputFile:
            with open(noDupsFilePath, 'w') as noDupsFile:

                lastRowKey = None

                for line in inputFile:

                    thisRowKey = [line.split()[column] for column in keyColumns]

                    # Write this read only if it does not match the previous read.
                    if lastRowKey is None or lastRowKey != thisRowKey:

                        noDupsFile.write(line)

                        lastRowKey = thisRowKey

                    else: rowsRemoved += 1

        print("Removed", rowsRemoved, "rows.")


def main():

    # Create a simple dialog for selecting the gene designation files.
    dialog = TkinterDialog(workingDirectory=getDataDirectory())
    dialog.createMultipleFileSelector("Delimited Files To Be Trimmed:", 0, "trim_me.bed", 
                                      ("Bed Files", ".bed"), ("TSV Files", ".tsv"))

    dialog.mainloop()

    if dialog.selections is None: quit()

    trimDuplicates(dialog.selections.getFilePathGroups()[0])

if __name__ == "__main__": main()