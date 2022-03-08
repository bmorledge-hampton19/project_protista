# Convert bigwig files to wig format using the bigWigToWig program from:
# http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/
import subprocess, os
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.FileSystemHandling.DirectoryHandling import checkDirs
from typing import List

def bigWigToWig(inputFilePaths: List[str], outputToIntermediateDirectory = False):

    outputFilePaths = list()

    for inputFilePath in inputFilePaths:
        print("Converting",os.path.basename(inputFilePath),"from bigwig to wig.")

        # Create the output file path, making sure the outputToIntermediateDirectory parameter is satisfied.
        outputFileName = os.path.basename(inputFilePath.rsplit('.',1)[0] + ".wig")
        if outputToIntermediateDirectory and not os.path.dirname(inputFilePath).endswith("intermediate_files"):
            checkDirs(os.path.join(os.path.dirname(inputFilePath), "intermediate_files"))
            outputFilePath = os.path.join(os.path.dirname(inputFilePath), "intermediate_files", outputFileName)
        elif outputToIntermediateDirectory or not os.path.dirname(inputFilePath).endswith("intermediate_files"):
            outputFilePath = os.path.join(os.path.dirname(inputFilePath), outputFileName)
        else:
            outputFilePath = os.path.join(os.path.dirname(os.path.dirname(inputFilePath)), outputFileName)
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