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
                loci = splitLine[8].split('$')
                functions = splitLine[9].split('$')
                
                # NOTE: The following if/assert statements are a band-aid on a larger problem that stems from
                # duplicate functions being removed to prevent redundancy from isoforms. It SHOULD be fine as long
                # as there are no peaks that have been annonated with multiple functions as well. In this case,
                # there is ambiguity that can't be resolved... Hopefully that doesn't happen though!
                #
                # Future Ben, if you're reading this because the assert statment tripped, I'm sorry...
                # Remember that the supplementary info handler that outputs loci and function information
                # in AnnotatePeaks.py can be changed to preserve duplicates!
                if len(loci) != len(functions):
                    assert len(functions) == 1, "Ambiguous functions for multiple loci"
                    functions*=len(loci)

                for i,locus in enumerate(loci):
                    if locus not in lociInThisFile:
                        lociInThisFile.add(locus)
                        numberOfFilesWithLocus[locus] = numberOfFilesWithLocus.setdefault(locus, 0) + 1
                        functionByLocus[locus] = functions[i]

    print("Writing results...")
    with open(outputFilePath, 'w') as outputFile:
        for locus in numberOfFilesWithLocus:
            outputFile.write('\t'.join((locus, functionByLocus[locus], str(numberOfFilesWithLocus[locus]))) + '\n')

    subprocess.check_call(("sort", "-k3,3nr", "-k1,1", "-t\t",  "-o", outputFilePath, outputFilePath))


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data"),
                       title = "Seclip Find Common Loci") as dialog:
        dialog.createMultipleFileSelector("Full annotation Files:", 0, "full_annotation.bed",
                                          ("Bed Files", ".bed"))
        dialog.createFileSelector("Output File:", 1, ("Tab Separated Values File", ".tsv"), newFile=True)

    selections = dialog.selections

    findCommonLoci(selections.getFilePathGroups()[0], selections.getIndividualFilePaths()[0])


if __name__ == "__main__": main()