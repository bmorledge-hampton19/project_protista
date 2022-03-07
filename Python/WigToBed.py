# Convert bigwig files to wig format using the bigWigToWig program from:
# http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/
import subprocess, os
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from typing import List
friendlyWig2BedPath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "Bash","subprocess_friendly_wig2bed.sh")

def wigToBed(inputFilePaths: List[str]):

    outputFilePaths = list()

    for inputFilePath in inputFilePaths:
        print("Converting",os.path.basename(inputFilePath),"from wig to bed.")

        outputFilePath = inputFilePath.rsplit('.',1)[0] + ".bed"
        outputFilePaths.append(outputFilePath)
        subprocess.check_call((friendlyWig2BedPath, inputFilePath, outputFilePath))

    return outputFilePaths


def main():

    # Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=os.path.dirname(__file__))
    dialog.createMultipleFileSelector("wig Files:", 0, ".wig", ("wig files", ".wig"))

    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    wigToBed(dialog.selections.getFilePathGroups()[0])

if __name__ == "__main__": main()