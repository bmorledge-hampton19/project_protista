# This script passes a bigwig file through several other python scripts to convert it to a format suitable for mutperiod.
from typing import List
from BigWigToWig import bigWigToWig
from WigToBed import wigToBed
from WigBedToCustomBed import wigBedToCustomBed
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
import os


def bigWigToCustomBed(bigWigFilePaths: List[str]):

    wigFilePaths = bigWigToWig(bigWigFilePaths)
    print()
    wigBedFilePaths = wigToBed(wigFilePaths)
    print()
    wigBedToCustomBed(wigBedFilePaths)


def main():

    # Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=os.path.dirname(__file__))
    dialog.createMultipleFileSelector("bigwig Files:", 0, ".bigwig", ("bigwig files", (".bw",".bigwig")), additionalFileEndings = (".bw"))

    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    bigWigToCustomBed(dialog.selections.getFilePathGroups()[0])

if __name__ == "__main__": main()