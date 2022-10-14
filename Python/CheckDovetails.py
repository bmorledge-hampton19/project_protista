# This script checks for dovetailed regions of paired-end alignments.
import os, gzip
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.FileSystemHandling.SamFileIterator import SamFileIterator


def checkDovetails(samFilePaths: List[str]):

    for samFilePath in samFilePaths:
        print(f"Working in {os.path.basename(samFilePath)}\n")

        if samFilePath.endswith(".gz"): openFunction = gzip.open
        else: openFunction = open
        
        lastRead: SamFileIterator.SamRead = None
        with openFunction(samFilePath, "rt") as samFile:
            for samRead in SamFileIterator(samFile, skipUnaligned = True):
                
                # Check for read pairs
                if lastRead is not None and samRead.readName == lastRead.readName:

                    # Check for dovetailing.
                    if samRead.strand == '+':
                        plusRead = samRead
                        minusRead = lastRead
                    else:
                        plusRead = lastRead
                        minusRead = samRead

                    if minusRead.startPos < plusRead.startPos:
                        print(f"Dovetailing for read pair {samRead.readName} at 3' end of minus strand read. "
                              f"({plusRead.startPos - minusRead.startPos} base(s))")
                        print(f"Dovetailing read alignmnent:\n{minusRead.getAlignmentString()}\n")

                    if plusRead.endPos > minusRead.endPos:
                        print(f"Dovetailing for read pair {samRead.readName} at 3' end of plus strand read. "
                              f"({plusRead.endPos - minusRead.endPos} base(s))")
                        print(f"Dovetailing read alignmnent:\n{plusRead.getAlignmentString()}\n")

                lastRead = samRead


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data")) as dialog:
        dialog.createMultipleFileSelector("Sam files:", 0, ".sam", ("Sam Files", (".sam", ".sam.gz")))

    checkDovetails(dialog.selections.getFilePathGroups()[0])


if __name__ == "__main__": main()
