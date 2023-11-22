# This script takes sequences from one or more fully annotated seCLIP peaks file and converts them to fasta format
# for use in STREME.
# Can filter using a common loci file along with a minimum number of files that a locus must be present in.
# Can also filter on sequence length or expand smaller sequences to hit a minimum sequence length.
import os, math
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.CustomErrors import checkForNumber
from benbiohelpers.FileSystemHandling.DirectoryHandling import getTempDir
from benbiohelpers.FileSystemHandling.BedToFasta import bedToFasta
from benbiohelpers.CustomErrors import InvalidPathError


def formatReadSequencesForSTREME(fullAnnotationFilePaths: List[str], outputFilePath: str, genomeFastaFilePath: str,
                                 commonLociFilePath = None, minCommonLociFiles = None,
                                 maxSequenceLength: int = None, minSequenceLength: int = 3):

    if not outputFilePath.endswith(".fa"):
        raise InvalidPathError(outputFilePath, "Given output path does not appear to be a fasta file.")

    if commonLociFilePath is not None:
        print("Filtering requested. Finding valid loci...")
        validLoci = set()
        with open(commonLociFilePath, 'r') as commonLociFile:
            for line in commonLociFile:
                splitLine = line.strip().split('\t')
                if int(splitLine[2]) >= minCommonLociFiles: validLoci.add(splitLine[0])
        print(f"Found {len(validLoci)} valid loci.")

    writtenSequences = 0
    
    intermediatePositionsFilePath = os.path.join(getTempDir(outputFilePath),
                                                 os.path.basename(outputFilePath).rsplit(".fa",1)[0]+".bed")

    with open(intermediatePositionsFilePath, 'w') as intermediatePositionsFile:
        
        observedPositions = set()

        for fullAnnotationFilePath in fullAnnotationFilePaths:

            print(f"Writing positions from {os.path.basename(fullAnnotationFilePath)} to intermediate bed file...")

            with open(fullAnnotationFilePath, 'r') as fullAnnotationFile:

                for line in fullAnnotationFile:
                    splitLine = line.strip().split('\t')

                    if commonLociFilePath is not None and splitLine[8] not in validLoci: continue
                    if maxSequenceLength is not None or minSequenceLength is not None:
                        startPos = int(splitLine[1])
                        endPos = int(splitLine[2])
                        length = endPos-startPos
                        if maxSequenceLength is not None and length > maxSequenceLength: continue
                        if minSequenceLength is not None and length < minSequenceLength:
                            additionalRadius = math.ceil((minSequenceLength - length)/2)
                            splitLine[1] = str(startPos-additionalRadius)
                            splitLine[2] = str(endPos+additionalRadius)
                    position = f"{splitLine[0]}:{splitLine[1]}-{splitLine[2]}"
                    if position in observedPositions: continue
                    else: observedPositions.add(position)

                    intermediatePositionsFile.write('\t'.join((splitLine[0],splitLine[1],splitLine[2],
                                                                   '.','.',splitLine[5]))+'\n')
                    writtenSequences += 1

    bedToFasta(intermediatePositionsFilePath, genomeFastaFilePath, outputFilePath)

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