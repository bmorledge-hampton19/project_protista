# This script takes multiple bed files which have been annotated by the AnnotatePeaks script
# to include information on any genomic loci the entries are encompassed by.
# These data are used to count how many files each locus is present it. Then, information
# on the loci, their descriptions, and the number of files they are found in is printed
# to an output tsv file.
import os, subprocess
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog


def findCommonLoci(fullAnnotationFilePaths: List[str], outputFilePath: str):

    numberOfFilesWithLocus = dict()
    functionByLocus = dict()

    for fullAnnotationFilePath in fullAnnotationFilePaths:

        print(f"Finding unique loci in {os.path.basename(fullAnnotationFilePath)}...")

        lociInThisFile = set()

        with open(fullAnnotationFilePath, 'r') as fullAnnotationFile:
            for line in fullAnnotationFile:
                splitLine = line.strip().split('\t')
                locus = splitLine[8]
                if locus not in lociInThisFile:
                    lociInThisFile.add(locus)
                    numberOfFilesWithLocus[locus] = numberOfFilesWithLocus.setdefault(locus, 0) + 1
                    functionByLocus[locus] = splitLine[9]

    print("Writing results...")
    with open(outputFilePath, 'w') as outputFile:
        for locus in numberOfFilesWithLocus:
            outputFile.write('\t'.join((locus, functionByLocus[locus], str(numberOfFilesWithLocus[locus]))) + '\n')

    subprocess.check_call(("sort", "-k3,3nr", "-k1,1", "-t\t",  "-o", outputFilePath, outputFilePath))


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data")) as dialog:
        dialog.createMultipleFileSelector("Full annotation Files:", 0, "full_annotation.bed",
                                          ("Bed Files", ".bed"))
        dialog.createFileSelector("Output File:", 1, ("Tab Separated Values File", ".tsv"), newFile=True)

    selections = dialog.selections

    findCommonLoci(selections.getFilePathGroups()[0], selections.getIndividualFilePaths()[0])


if __name__ == "__main__": main()