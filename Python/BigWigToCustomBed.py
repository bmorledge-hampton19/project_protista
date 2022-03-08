# This script passes a bigwig file through several other python scripts to convert it to a format suitable for mutperiod.
from typing import List
from BigWigToWig import bigWigToWig
from WigToBed import wigToBed
from WigBedToCustomBed import wigBedToCustomBed
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
import os


def bigWigToCustomBed(bigWigFilePaths: List[str], strandDesignation = '.'):

    wigFilePaths = bigWigToWig(bigWigFilePaths, True)
    print()
    wigBedFilePaths = wigToBed(wigFilePaths, True)
    print()
    wigBedToCustomBed(wigBedFilePaths, strandDesignation = strandDesignation)


def main():

    # Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=os.path.dirname(__file__))
    dialog.createMultipleFileSelector("bigwig Files:", 0, ".bigwig", ("bigwig files", (".bw",".bigwig")), 
                                      additionalFileEndings = (".bw"))
    dialog.createDropdown("Strand Designation", 1, 0, ("Ambiguous '.'", "Plus Strand '+'", "Minus Strand '-'"))


    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    strandDesignation = dialog.selections.getDropdownSelections()[0].rsplit('\'',2)[1]

    bigWigToCustomBed(dialog.selections.getFilePathGroups()[0], strandDesignation)

if __name__ == "__main__": main()