import os
from typing import List
from benbiohelpers.FileSystemHandling.BedToFasta import bedToFasta
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog

# Given a list of bed files, simply uses the bedToFasta command to convert them to fasta files.
def bedsToFastas(bedFilePaths: List[str], genomeFilePath):
    
    for bedFilePath in bedFilePaths:
        print("Converting",os.path.basename(bedFilePath))
        bedToFasta(bedFilePath, genomeFilePath, bedFilePath.rsplit('.',1)[0]+".fa")


def main():
    
    # Get the working directory from mutperiod if possible. Otherwise, just use this script's directory.
    try:
        from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
        workingDirectory = getDataDirectory()
    except ImportError:
        workingDirectory = os.path.dirname(__file__)

    with TkinterDialog(workingDirectory = workingDirectory) as dialog:
        dialog.createMultipleFileSelector("Bed Files:", 0, ".bed", ("Bed Files", ".bed"))
        dialog.createFileSelector("Genome Fasta File:", 1, ("Fasta File", ".fa"))

    bedsToFastas(dialog.selections.getFilePathGroups()[0], dialog.selections.getIndividualFilePaths()[0])


if __name__ == "__main__": main()