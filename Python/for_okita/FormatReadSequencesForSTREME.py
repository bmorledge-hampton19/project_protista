# This script takes sequences from a fully annotated seCLIP peaks file and converts them to fasta format for use in STREME.
# Optionally, can filter using a common loci file along with a minimum number of files that a locus must be present in.
import os
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.CustomErrors import checkForNumber


def formatReadSequencesForSTREME(fullAnnotationFilePaths: List[str], outputFilePath: str,
                                 commonLociFilePath = None, minCommonLociFiles = None):

    if commonLociFilePath is not None:
        print("Filtering requested. Finding valid loci...")
        validLoci = set()
        with open(commonLociFilePath, 'r') as commonLociFile:
            for line in commonLociFile:
                splitLine = line.strip().split('\t')
                if int(splitLine[2]) >= minCommonLociFiles: validLoci.add(splitLine[0])
        print(f"Found {len(validLoci)} valid loci.")

    writtenSequences = 0
    with open(outputFilePath, 'w') as outputFile:
        for fullAnnotationFilePath in fullAnnotationFilePaths:

            print(f"Writing sequences from {os.path.basename(fullAnnotationFilePath)}...")

            with open(fullAnnotationFilePath, 'r') as fullAnnotationFile:
                for line in fullAnnotationFile:
                    splitLine = line.strip().split('\t')
                    if commonLociFilePath is not None and splitLine[8] not in validLoci: continue
                    outputFile.write(f">{writtenSequences}\n")
                    outputFile.write(splitLine[11] + '\n')
                    writtenSequences += 1

    print(f"Finished writitng {writtenSequences} sequences!")


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data"),
                       title = "Format Read Sequences for STREME") as dialog:
        dialog.createMultipleFileSelector("Full annotation Files:", 0, "full_annotation.bed",
                                          ("Bed Files", ".bed"))
        with dialog.createDynamicSelector(1, 0) as filterDynSel:
            filterDynSel.initCheckboxController("Filter on common loci")
            filterDisplay = filterDynSel.initDisplay(True, "filterDisplay")
            filterDisplay.createFileSelector("Common loci file:", 0, ("Tab Separated Values File", ".tsv"))
            filterDisplay.createTextField("Minimum common files:", 2, 0, defaultText="2")
        dialog.createFileSelector("Output File:", 2, ("Fasta File", ".fa"), newFile=True)

    selections = dialog.selections

    if filterDynSel.getControllerVar():
        commonLociFilePath = selections.getIndividualFilePaths("filterDisplay")[0]
        minCommonLociFiles = checkForNumber(selections.getTextEntries("filterDisplay")[0], True, lambda x: x > 0)
    else:
        commonLociFilePath = None
        minCommonLociFiles = None


    formatReadSequencesForSTREME(selections.getFilePathGroups()[0], selections.getIndividualFilePaths()[0],
                                 commonLociFilePath, minCommonLociFiles)


if __name__ == "__main__": main()