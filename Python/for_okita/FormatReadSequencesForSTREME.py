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
                                 maxSequenceLength: int = None, minSequenceLength: int = 3,
                                 callFromThreePrimeEnd = True, fivePrimeExtension = 0, threePrimeExtension = 0):

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
                    startPos = int(splitLine[1])
                    endPos = int(splitLine[2])
                    strand = splitLine[5]

                    # Format the entry and determine if it is valid based on given parameters.
                    if commonLociFilePath is not None and splitLine[8] not in validLoci: continue
                    if callFromThreePrimeEnd:
                        if strand == '+': startPos = endPos-1
                        elif strand == '-': endPos = startPos+1
                    if strand == '+':
                        startPos -= fivePrimeExtension
                        endPos += threePrimeExtension
                    elif strand == '-':
                        startPos -= threePrimeExtension
                        endPos += fivePrimeExtension
                    if maxSequenceLength is not None or minSequenceLength is not None:
                        length = endPos-startPos
                        if maxSequenceLength is not None and length > maxSequenceLength: continue
                        if minSequenceLength is not None and length < minSequenceLength:
                            additionalRadius = math.ceil((minSequenceLength - length)/2)
                            startPos -= additionalRadius
                            endPos += additionalRadius
                            splitLine[1] = str(startPos-additionalRadius)
                            splitLine[2] = str(endPos+additionalRadius)
                    position = (splitLine[0], startPos, endPos)
                    if position in observedPositions: continue
                    else: observedPositions.add(position)

                    intermediatePositionsFile.write('\t'.join((splitLine[0],str(startPos),str(endPos),
                                                                   '.','.',splitLine[5]))+'\n')
                    writtenSequences += 1

    bedToFasta(intermediatePositionsFilePath, genomeFastaFilePath, outputFilePath)

    print(f"Finished writitng {writtenSequences} sequences!")


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data"),
                       title = "Format Read Sequences for STREME") as dialog:
        dialog.createMultipleFileSelector("Full annotation files:", 0, "full_annotation.bed",
                                          ("Bed Files", ".bed"))
        dialog.createFileSelector("Genome fasta file:", 1, ("Fasta file", ".fa")),
        dialog.createFileSelector("Output file path:", 2, ("Fasta file", ".fa"), newFile=True)
        with dialog.createDynamicSelector(3, 0, 2) as filterDynSel:
            filterDynSel.initCheckboxController("Filter on common loci")
            filterDisplay = filterDynSel.initDisplay(True, "filterDisplay")
            filterDisplay.createFileSelector("Common loci file:", 0, ("Tab Separated Values File", ".tsv"))
            filterDisplay.createTextField("Minimum common files:", 2, 0, defaultText="2")
        dialog.createCheckbox("Call from three prime end:", 4, 0, 1)
        dialog.createTextField("Five prime extension:", 5, 0, 1, "0", 10)
        dialog.createTextField("Three prime extension:", 5, 1, 1, "0", 10)
        with dialog.createDynamicSelector(6, 0, 2) as maxLengthDS:
            maxLengthDS.initCheckboxController("Enforce max length")
            maxLengthDS.initDisplay(True, "maxLength", 0, 1).createTextField("Max length:", 0, 0, 2, "50")
        with dialog.createDynamicSelector(7, 0, 2) as minLengthDS:
            minLengthDS.initCheckboxController("Enforce min length")
            minLengthDS.initDisplay(True, "minLength", 0, 1).createTextField("Min length:", 0, 0, 2, "3")

    selections = dialog.selections

    fullAnnotationFilePaths = selections.getFilePathGroups()[0]
    genomeFastaFilePath = selections.getIndividualFilePaths()[0]
    outputFilePath = selections.getIndividualFilePaths()[1]

    if filterDynSel.getControllerVar():
        commonLociFilePath = selections.getIndividualFilePaths("filterDisplay")[0]
        minCommonLociFiles = checkForNumber(selections.getTextEntries("filterDisplay")[0], True, lambda x: x > 0)
    else:
        commonLociFilePath = None
        minCommonLociFiles = None

    callFromThreePrimeEnd = selections.getToggleStates()[0]
    fivePrimeExtension = checkForNumber(selections.getTextEntries()[0], True, lambda x: x >= 0)
    threePrimeExtension = checkForNumber(selections.getTextEntries()[1], True, lambda x: x >= 0)

    if maxLengthDS.getControllerVar():
        maxSequenceLength = checkForNumber(selections.getTextEntries("maxLength")[0], True, lambda x: x >= 0)
    else: maxSequenceLength = None
    if minLengthDS.getControllerVar():
        minSequenceLength = checkForNumber(selections.getTextEntries("minLength")[0], True, lambda x: x >= 0)
    else: minSequenceLength = None

    formatReadSequencesForSTREME(fullAnnotationFilePaths, outputFilePath, genomeFastaFilePath,
                                 commonLociFilePath, minCommonLociFiles,
                                 maxSequenceLength, minSequenceLength,
                                 callFromThreePrimeEnd, fivePrimeExtension, threePrimeExtension)


if __name__ == "__main__": main()