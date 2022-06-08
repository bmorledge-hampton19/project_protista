# This script takes a genome fasta file and one or more sequences and determines their frequency throughout the genome.
import os
from typing import List
from benbiohelpers.FileSystemHandling.FastaFileIterator import FastaFileIterator
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.InputParsing.ParseToIterable import parseToIterable
from benbiohelpers.CustomErrors import UserInputError


def getGenomicSequenceFrequency(genomeFastaFilePath, sequences: List[str]):
    
    # Do we have multiple sequences?
    if len(sequences) == 0: raise UserInputError("No sequences given.")

    # Make sure all given sequences are of the same length, otherwise things get messy.
    sequenceLength = len(sequences[0])
    if not all(len(sequence) == sequenceLength for sequence in sequences):
        raise UserInputError("Not all sequences are of a uniform length.")

    # Conver the sequences to upper case.
    sequences = [sequence.upper() for sequence in sequences]

    print(f"\nGiven sequences: {sequences}")

    # Create a dictionary of counts for each sequence and an integer for counts of sequences not in the dictionary. 
    sequenceCounts = dict()
    for sequence in sequences: sequenceCounts[sequence] = 0
    totalCounts = 0

    # Iterate through the fasta file, counting sequences as you go.
    print("\nCounting sequences throughout the genome...")
    with open(genomeFastaFilePath, 'r') as genomeFastaFile:
        for fastaEntry in FastaFileIterator(genomeFastaFile, False):
            print(f"\tCounting in {fastaEntry.sequenceName}...")
            for i in range(len(fastaEntry.sequence)-sequenceLength+1):
                sequence = fastaEntry.sequence[i:i+sequenceLength].upper()
                if sequence in sequenceCounts: sequenceCounts[sequence] += 1
                totalCounts += 1

    # Print the results:
    print("Results:")
    for sequence in sequenceCounts:
        print(f"\t{sequence} counts: {sequenceCounts[sequence]} ({sequenceCounts[sequence]/totalCounts*100}%)")
    if len(sequenceCounts) > 1:
        totalCounts = sum(count for count in sequenceCounts.values())
        print(f"\tTotal sequence counts: {totalCounts} ({totalCounts/totalCounts*100}%)")


def main():
    
    # Get the working directory from mutperiod if possible. Otherwise, just use this script's directory.
    try:
        from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
        workingDirectory = getDataDirectory()
    except ImportError:
        workingDirectory = os.path.dirname(__file__)

    # Get user input from a tkinter dialog.
    with TkinterDialog(workingDirectory = workingDirectory) as dialog:
        dialog.createFileSelector("Genome Fasta File:", 0, ("Fasta File", ".fa"))
        dialog.createTextField("Sequence(s) to count:", 1, 0, defaultText = "CC, CT, TC, TT")

    genomeFastaFilePath = dialog.selections.getIndividualFilePaths()[0]
    sequences = parseToIterable(dialog.selections.getTextEntries()[0], castValuesToInt = False)

    getGenomicSequenceFrequency(genomeFastaFilePath, sequences)


if __name__ == "__main__": main()