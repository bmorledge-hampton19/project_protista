# DEPRECATED - The functionality provided by this script is now built into formatReadSequencesForSTREME.py
# Curates fasta files by removing duplicates and enforcing a minimum bp length on sequences.
import os
from typing import List
from benbiohelpers.FileSystemHandling.FastaFileIterator import FastaFileIterator
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog


def curateFastaFiles(fastaFilePaths: List[str], minLength = 3):

    for inputFastaFilePath in fastaFilePaths:

        print(f"\nWorking with {os.path.basename(inputFastaFilePath)}")

        outputFastaFilePath = inputFastaFilePath.rsplit('.',1)[0] + f"_no_dups_{minLength}bp_min.fa"

        with open(inputFastaFilePath, 'r') as inputFastaFile:
            with open(outputFastaFilePath, 'w') as outputFastaFile:
                observedEntries = set()
                for fastaEntry in FastaFileIterator(inputFastaFile, False):

                    # Check for duplicate entries.
                    if fastaEntry.sequenceName in observedEntries:
                        print(f"Skipping entry with duplicated name: {fastaEntry.sequenceName}")
                        continue
                    else: observedEntries.add(fastaEntry.sequenceName)

                    # Check for the minimum size threshold.
                    if len(fastaEntry.sequence) < minLength:
                        print(f"Skipping entry with below-minimum sequence length: {fastaEntry.sequence}")
                        continue

                    # If we got this far, write the fasta entry to the new file!
                    outputFastaFile.write(fastaEntry.formatForWriting())


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data"),
                       title = "Curate Seclip Fasta Files") as dialog:
        dialog.createMultipleFileSelector("Fasta Files:", 0, ".fasta", ("Fasta Files", ".fa"))

    selections = dialog.selections

    curateFastaFiles(selections.getFilePathGroups()[0])


if __name__ == "__main__": main()
