# This script takes a bed file that is the result of the wig2bed operation and converts it to the bed format expected by mutperiod.
from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import DataTypeStr, getDataDirectory
from mutperiodpy.Tkinter_scripts.TkinterDialog import TkinterDialog
from typing import List
import os


def wigBedToCustomBed(wigBedFilePaths: List[str]):

    for wigBedFilePath in wigBedFilePaths:

        print("Working in",os.path.basename(wigBedFilePath))

        customBedFilePath = wigBedFilePath.rsplit('.',1)[0] + '_'
        if customBedFilePath.endswith("from_wig_"): customBedFilePath = customBedFilePath.rsplit("from_wig_",1)[0]
        customBedFilePath += DataTypeStr.customInput + ".bed"

        # Read out of the first file and write to the second to convert to the custom bed file.
        with open(wigBedFilePath, 'r') as wigBedFile:
            with open(customBedFilePath, 'w') as customBedFile:

                for line in wigBedFile:

                    chromosome, startPos, endPos, _, counts = line.split()
                    # Add the line "counts" number of times.
                    counts = int(float(counts))
                    for _ in range(counts):
                        customBedFile.write('\t'.join((chromosome, startPos, endPos, '.', "OTHER", '.')) + '\n')


def main():

    #Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=getDataDirectory())
    dialog.createMultipleFileSelector("Bed Files (From wig2bed):",0, "from_wig.bed",("Bed Files",".bed"))

    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    wigBedToCustomBed(dialog.selections.getFilePathGroups()[0])

if __name__ == "__main__": main()