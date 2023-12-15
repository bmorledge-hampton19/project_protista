# This script takes a file of exon regions and finds points within genes where introns are spanned.
# This input file must be sorted, first on locus (4th column), then on chromosome (1st column),
# then start position (2nd column, numerically), then end position (3rd column, numerically).
import os, subprocess
from typing import Dict, List, Set
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.CustomErrors import UnsortedInputError

class Exon:

    def __init__(self, start: int, end: int, locus: str):
        """
        Start and end should be one-based.
        Start should represent the lowest position (not necessarily the 5' position).
        """
        self.start = start
        self.end = end
        self.locus = locus

    def __getKeyComponents(self):
        return (self.start, self.end, self.locus)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__getKeyComponents() == other.__getKeyComponents()
        else: return False

    def __hash__(self):
        return hash(self.__getKeyComponents())


def getExonJunctions(exonFilePath: str, checkSorting = True, exonSkipsAllowed = 0):
    """
    Takes a file path of exon regions and returns a nested dictionary of stop-start positions for each locus
    which can be used to join exons together over the introns.
    The keys of the nested dictionary are the locus name followed by the exon stop positions,
    and the values are sets of potential exon join positions (strand-agnostic, always joined from lower to higher positions).
    """

    print(f"Generating exon junction map for {os.path.basename(exonFilePath)} with {exonSkipsAllowed} skips allowed.")

    if checkSorting:

        print("Checking for proper sorting...")

        try:
            subprocess.check_output(("sort", "-k4,4", "-k1,1", "-k2,2n", "-k3,3n", "-c", exonFilePath))
        except subprocess.CalledProcessError:
            raise UnsortedInputError(exonFilePath,
                                     "Expected sorting based locus (4th column), then on chromosome (1st column), then "
                                     "start position (2nd column, numerically), then end position (3rd column, numerically).")

    exonJunctions: Dict[str,Dict[int,Set[int]]] = dict()

    with open(exonFilePath, 'r') as exonFile:

        # Return the exon as a list with the positions standardized to base-1 format.
        def getNextExon():
            bedLine = exonFile.readline()
            if not bedLine: return None
            splitBedLine = bedLine.strip().split('\t')
            return Exon(int(splitBedLine[1]) + 1, int(splitBedLine[2]), splitBedLine[3])
            

        # Preprocess first exon.
        nextExon = getNextExon()

        # Continue until no exons remain.
        while nextExon is not None:

            currentLocus = nextExon.locus
            exonConnections: Dict[Exon,Set[Exon]] = dict()
            currentLocusExons: List[Exon] = list()
            currentLocusExons.append(nextExon)
            nextExon = getNextExon()

            # Collect all the entries for the current locus.
            while nextExon is not None and nextExon.locus == currentLocus:
                currentLocusExons.append(nextExon)
                nextExon = getNextExon()

            ### Process this locus

            # Iterate through every locus, building a dictionary of connections with no skipping.
            for i, currentLocusExon in enumerate(currentLocusExons):
                joinableExons: Set[Exon] = set()
                compareExonIndex = i + 1
                foundFutureJoin = False

                # Iterate through the other loci until we encounter one that should be joined
                # with another locus after this one (i.e., a future join).
                while compareExonIndex < len(currentLocusExons) and not foundFutureJoin:
                    compareExon = currentLocusExons[compareExonIndex]

                    # Check for future joins.
                    for joinableExon in joinableExons:
                        if compareExon.start > joinableExon.end:
                            foundFutureJoin = True
                    # Check for a join with the current exon.
                    if not foundFutureJoin and compareExon.start > currentLocusExon.end:
                        joinableExons.add(compareExon)

                    compareExonIndex += 1

                # Add on to the dictionary with the current set.
                exonConnections[currentLocusExon] = joinableExons
            
            # Convert exon connections to the junction positions, accounting for exon skipping. 
            exonJunctions[currentLocus] = dict()
            for startingExon in exonConnections:
                exonJunctions[currentLocus][startingExon.end] = set()
                nextExons = exonConnections[startingExon]
                for _ in range(exonSkipsAllowed + 1):
                    connectingExons = nextExons
                    nextExons = set()
                    for connectingExon in connectingExons:
                        exonJunctions[currentLocus][startingExon.end].add(connectingExon.start)
                        nextExons.update(exonConnections[connectingExon])

    return exonJunctions


def main():
    with TkinterDialog(workingDirectory=os.path.dirname(__file__), title = "Get Exon Junctions") as dialog:
        dialog.createFileSelector("Exons file", 0, ("Bed file", ".bed"))
        dialog.createTextField("Allowed Exon Skips", 1, 0, defaultText = "0")

    exonJunctions = getExonJunctions(dialog.selections.getIndividualFilePaths()[0],
                                     exonSkipsAllowed = int(dialog.selections.getTextEntries()[0]))

    for locus in exonJunctions:
        print(f"{locus}:")
        for exonEnd in exonJunctions[locus]:
            print(f"  {exonEnd}:")
            for exonStart in exonJunctions[locus][exonEnd]:
                print(f"    {exonStart}")

if __name__ == "__main__": main()