# Convert bigwig files to wig format using the bigWigToWig program from:
# http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/
import subprocess, os
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from typing import List

def bigWigToWig(inputFilePaths: List[str]):

    outputFilePaths = list()

    for inputFilePath in inputFilePaths:
        print("Converting",os.path.basename(inputFilePath),"from bigwig to wig.")

        outputFilePath = inputFilePath.rsplit('.',1)[0] + ".wig"
        outputFilePaths.append(outputFilePath)
        subprocess.check_call(("bigWigToWig", inputFilePath, outputFilePath))

    return outputFilePaths


def main():

    # Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=os.path.dirname(__file__))
    dialog.createMultipleFileSelector("bigwig Files:", 0, ".bigwig", ("bigwig files", (".bw",".bigwig")), additionalFileEndings = (".bw"))

    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    bigWigToWig(dialog.selections.getFilePathGroups()[0])

if __name__ == "__main__": main()