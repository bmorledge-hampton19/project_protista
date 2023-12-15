# This script takes peaks from one or more fully annotated seCLIP files and combines peaks that are adjacent,
# either directly or due to exon junctions.
import os, math
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.InputParsing.CheckForNumber import checkForNumber
from benbiohelpers.CustomErrors import checkForNumber
from GetExonJunctions import getExonJunctions


def combineAdjacentPeaks(fullAnnotationFilePaths: List[str], exonFilePath,
                         adjacencyThreshold = 1, exonSkipsAllowed = 0):

    exonJunctions = getExonJunctions(exonFilePath, exonSkipsAllowed = exonSkipsAllowed)

    for fullAnnotationFilePath in fullAnnotationFilePaths:
        
        print(f"\nWorking in {os.path.basename(fullAnnotationFilePath)}")
        combinedFilePath = fullAnnotationFilePath.rsplit(".bed",1)[0] + "_combined.bed"

        with open(fullAnnotationFilePath, 'r') as fullAnnotationFile, open(combinedFilePath, 'w') as combinedFile:

            # Initialize the first line.
            lastSplitLine = fullAnnotationFile.readline().strip().split('\t')

            for line in fullAnnotationFile:
                
                splitLine = line.strip().split('\t')

                combined = False

                # Make sure the loci match.
                if splitLine[8] == lastSplitLine[8]:

                    lastLineEnd = int(lastSplitLine[2])
                    thisLineStart = int(splitLine[1]) + 1

                    # First check for directly adjacent peaks.
                    if thisLineStart - lastLineEnd <= adjacencyThreshold:
                        combined = True

                    # Then check for peaks joined by exon boundaries.
                    # NOTE: Because files are not sorted on locus, it's possible that join sites may be missed
                    #       if they are separated in the file. I'm hoping this is a very unlikely case though.
                    #       May revisit later.
                    else:
                        for locus in splitLine[8].split('$'):
                            junctionMap = exonJunctions[locus]
                            if lastLineEnd in junctionMap and thisLineStart in junctionMap[lastLineEnd]:
                                combined = True

                    # Combine the lines if they are adjacent.
                    if combined:
                        lastSplitLine[2] = splitLine[2] # NOTE: Doesn't fully describe exon joining. May need revising.
                        lastSplitLine[10] = '.' # NOTE: Temporary solution. May find something more graceful later.
                        lastSplitLine[11] = '.' # NOTE: Temporary solution. May find something more graceful later.
                    
                # If the lines weren't combined, just write the last line.
                if not combined:
                    combinedFile.write('\t'.join(lastSplitLine) + '\n')
                    lastSplitLine = splitLine


            # Don't forget to clean up the last line!
            if lastSplitLine: combinedFile.write('\t'.join(lastSplitLine) + '\n')


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data"),
                       title = "Combine Adjacent Peaks") as dialog:
        dialog.createMultipleFileSelector("Full annotation Files:", 0, "full_annotation.bed",
                                          ("Bed Files", ".bed"))
        dialog.createFileSelector("Exons File (locus sorted):", 1, ("Bed File", ".bed"))
        dialog.createTextField("Adjacency Threshold", 2, 0, defaultText = '1')
        dialog.createTextField("Exon Skips Allowed", 3, 0, defaultText = '0')

    combineAdjacentPeaks(dialog.selections.getFilePathGroups()[0], dialog.selections.getIndividualFilePaths()[0],
                         checkForNumber(dialog.selections.getTextEntries()[0], True),
                         checkForNumber(dialog.selections.getTextEntries()[1], True))


if __name__ == "__main__": main()