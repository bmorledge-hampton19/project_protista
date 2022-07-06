# This script takes one or more bed files and a simple tsv file containing chromosome
# IDs to convert from (1st column) and to (2nd column).
import os, warnings
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog


def convertBedChromosomeIDs(bedFilePaths: List[str], conversionFilePath: str):
    
    conversionDict = dict()
    with open(conversionFilePath, 'r') as conversionFile:
        for line in conversionFile:
            chrFrom, chrTo = line.split()
            conversionDict[chrFrom] = chrTo

    for bedFilePath in bedFilePaths:

        print(f"Working in {os.path.basename(bedFilePath)}")

        outputFilePath = bedFilePath.rsplit('.', 1)[0] + "_converted.bed"

        with open(bedFilePath, 'r') as bedFile:
            with open(outputFilePath, 'w') as outputFile:

                for line in bedFile:
                    splitLine = line.split()
                    if splitLine[0] not in conversionDict:
                        warnings.warn(f"Chromosome ID {splitLine[0]} not found in conversion dictionary. "
                                      "Omitting bed row from output file.")
                        continue
                    splitLine[0] = conversionDict[splitLine[0]]
                    outputFile.write('\t'.join(splitLine) + '\n')


def main():

    with TkinterDialog(workingDirectory=os.path.dirname(__file__)) as dialog:
        dialog.createMultipleFileSelector("Bed Files:", 0, ".bed", ("Bed Files", ".bed"))
        dialog.createFileSelector("Conversion File", 1, ("TSV file", ".tsv"))

    convertBedChromosomeIDs(dialog.selections.getFilePathGroups()[0], dialog.selections.getIndividualFilePaths()[0])

if __name__ == "__main__": main()