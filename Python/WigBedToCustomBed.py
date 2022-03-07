# This script takes a bed file that is the result of the wig2bed operation and converts it to the bed format expected by mutperiod.
import math, os
from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import DataTypeStr, getDataDirectory
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from typing import List


def wigBedToCustomBed(wigBedFilePaths: List[str]):

    for wigBedFilePath in wigBedFilePaths:

        print("Converting",os.path.basename(wigBedFilePath),"to custom bed format.")

        customBedFilePath = wigBedFilePath.rsplit('.',1)[0] + '_'
        if customBedFilePath.endswith("from_wig_"): customBedFilePath = customBedFilePath.rsplit("from_wig_",1)[0]
        customBedFilePath += DataTypeStr.customInput + ".bed"

        # The counts column may be a non-integer value.  Find out what the base (minimum) value is to
        # divide all other values by.
        minCount = math.inf
        with open(wigBedFilePath, 'r') as wigBedFile:
            for line in wigBedFile:
                counts = float(line.split()[4])
                if counts < minCount: minCount = counts

        # Read out of the first file and write to the second to convert to the custom bed file.
        with open(wigBedFilePath, 'r') as wigBedFile:
            with open(customBedFilePath, 'w') as customBedFile:

                for line in wigBedFile:

                    chromosome, startPos, endPos, _, counts = line.split()

                    # Add the line "counts" number of times, taking into account the "base" value
                    # and ensuring that the resulting value is actually a whole number (or close to it). 
                    adjustedCounts = float(counts)/minCount
                    if abs(adjustedCounts - round(adjustedCounts)) > 0.05:
                        raise ValueError(f"Counts value {counts} is not a derivative of base counts value {minCount}.")

                    for _ in range(round(adjustedCounts)):
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