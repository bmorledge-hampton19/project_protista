import os, subprocess
from benbiohelpers.CustomErrors import UnsortedInputError
from benbiohelpers.InputParsing.ParseToIterable import parseToIterable
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
from typing import List


def removeDuplicates(inputFilePaths: List[str], keyColumns = [0,1,2,5], checkSorting = True, numericCols = [1,2]):
    """
    Removes duplicates on a sorted input file by comparing consecutive rows.
    The keyColumns parameter should be a list containing the column indices (0-based) used to determine whether two rows are duplicates.
    The numericCols parameter describes which of those columns are expected to be sorted numerically.
    """

    for inputFilePath in inputFilePaths:

        print("\nWorking in",os.path.basename(inputFilePath))

        if checkSorting:

            print("Checking for proper sorting...")

            args = ["sort"]
            for colIndex in keyColumns:
                arg = f"-k{colIndex+1},{colIndex+1}"
                if numericCols is not None and colIndex in numericCols: arg += 'n'
                args.append(arg)

            args += ["-s", "-c", inputFilePath]

            try:
                subprocess.check_output(args)
            except subprocess.CalledProcessError:
                raise UnsortedInputError(inputFilePath,
                                         f"Expected sorting based on the following column indices (0-based): {keyColumns} with "
                                         f"these columns sorted numerically: {numericCols}")

        # Keep track of how many duplicate rows are found and removed.
        rowsRemoved = 0

        # Create a file to output results to.
        noDupsFilePath = inputFilePath.rsplit('.',1)[0] + "_no_dups.bed"

        # Iterate through the sorted reads file, writing each line to the new file but omitting any duplicate entries beyond the first.
        print("Removing duplicates...")
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
    with TkinterDialog(workingDirectory=getDataDirectory(), title = "Remove Duplicates") as dialog:
        dialog.createMultipleFileSelector("Files to remove duplicates from:", 0, "trim_me.bed", 
                                        ("Bed Files", ".bed"), ("TSV Files", ".tsv"))
        dialog.createTextField("Key column indices (0-based):", 1, 0, defaultText = "0, 1, 2, 5")
        with dialog.createDynamicSelector(2, 0) as checkSortDS:
            checkSortDS.initCheckboxController("Check sorting")
            checkSortDS.initDisplay(True, "checkSort").createTextField("Numeric sort columns:", 0, 0, defaultText = "1, 2")

    inputFilePaths = dialog.selections.getFilePathGroups()[0]
    keyColumns = parseToIterable(dialog.selections.getTextEntries()[0], castType = int)
    checkSorting = checkSortDS.getControllerVar()
    if checkSorting: numericCols = parseToIterable(dialog.selections.getTextEntries("checkSort")[0], castType = int)
    else: numericCols = list()

    removeDuplicates(inputFilePaths, keyColumns, checkSorting, numericCols)


if __name__ == "__main__": main()