from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory, getAcceptableChromosomes
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from typing import List
import os


# Takes a bed file and a genome file path and removes all entries with invalid chromosomes.
def removeInvalidChromosomes(inputBedFilePaths: List[str], genomeFilePath, replaceOriginalFile):

    # Get the acceptable chromosomes
    acceptableChromosomes = getAcceptableChromosomes(genomeFilePath)

    for inputBedFilePath in inputBedFilePaths:

        # Keep track of removed chromosomes to output this information to the user
        invalidChromsomes = set()

        print("Working in",os.path.basename(inputBedFilePath))

        intermediateFilePath = inputBedFilePath.rsplit('.',1)[0] + "_valid_chromosomes.bed"

        # Loop through the input file, copying every line with an acceptable chromosome to the new file.
        # The first time an invalid chromosome is found, output it's name to the user.
        with open(inputBedFilePath, 'r') as inputBedFile:
            with open(intermediateFilePath, 'w') as intermediateFile:

                for line in inputBedFile:

                    chromosome = line.split()[0]

                    if chromosome in acceptableChromosomes:
                        intermediateFile.write(line)

                    elif chromosome not in invalidChromsomes:
                        invalidChromsomes.add(chromosome)
                        print("Found invalid chromosome ", chromosome, ".  All associated entries will be removed.", sep = '')

        # If requested, replace the original file.
        if replaceOriginalFile:
            print("Rewriting original file...")
            os.replace(intermediateFilePath, inputBedFilePath)


def main():

    #Create the Tkinter UI
    with TkinterDialog(workingDirectory=getDataDirectory(), title = "Remove Invalid Chromosomes") as dialog:
        dialog.createMultipleFileSelector("Bed Files:",0, "from_wig.bed",("Bed Files",".bed"))
        dialog.createFileSelector("Genome File Path:", 1, ("Fasta File",".fa"))
        dialog.createCheckbox("Replace Original File", 2, 0)

    removeInvalidChromosomes(dialog.selections.getFilePathGroups()[0], dialog.selections.getIndividualFilePaths()[0],
                             dialog.selections.getToggleStates()[0])

if __name__ == "__main__": main()