# This script takes 4 inputs: A narrow peaks file (with headers removed), a genome fasta file,
# a tsv file of annotated genes (with headers remaining), and a bed file of exon locations.
# Given these inputs, the script determines which peaks are within which genic regions,
# whether they are in an exon or intron, and what the sequence of the peak is.
# This information is outputted to a new tsv file.
# NOTE: Make sure that no '$' characters are present in the gene annotations file. (These are
# used as separators for peaks that span multiple loci)

import os
from typing import List
from benbiohelpers.CountThisInThat.Counter import ThisInThatCounter, CounterOutputDataHandler
from benbiohelpers.CountThisInThat.CounterOutputDataHandler import OutputDataWriter
from benbiohelpers.CountThisInThat.InputDataStructures import EncompassingData, ENCOMPASSED_DATA, ENCOMPASSING_DATA
from benbiohelpers.CountThisInThat.OutputDataStratifiers import AmbiguityHandling
from benbiohelpers.CountThisInThat.SupplementalInformation import SimpleColumnSupInfoHandler
from benbiohelpers.FileSystemHandling.BedToFasta import bedToFasta
from benbiohelpers.FileSystemHandling.FastaFileIterator import FastaFileIterator
from benbiohelpers.FileSystemHandling.DirectoryHandling import checkDirs, filterTempFiles
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog

class GeneAnnotationData(EncompassingData):

    def setLocationData(self, acceptableChromosomes):
        
        self.chromosome = self.choppedUpLine[0] # The chromosome that houses the feature.
        self.startPos = float(self.choppedUpLine[3]) # The start position of the feature in its chromosome. (0 base)
        self.endPos = float(self.choppedUpLine[4]) - 1 # The end position of the feature in its chromosome. (0 base)
        self.center = (self.startPos + self.endPos) / 2 # The average (center) of the start and end positions.  (Still 0 base)
        self.strand = self.choppedUpLine[5] # Either '+' or '-' depending on which strand houses the mutation.

        # Make sure the mutation is in a valid chromosome.
        if acceptableChromosomes is not None and self.chromosome not in acceptableChromosomes:
            raise ValueError(self.chromosome + " is not a valid chromosome for this genome.")


class GeneDataAnnotator(ThisInThatCounter):

    def initOutputDataHandler(self):
        """
        Use this function to create the instance of the CounterOutputDataHandler object.
        Default behavior creates the output data handler and passes in the counter's "writeIncrementally" value.
        """
        self.outputDataHandler = CounterOutputDataHandler(self.writeIncrementally, trackAllEncompassed = True)


    def setupOutputDataStratifiers(self):
        """
        Use this function to set up any output data stratifiers for the output data handler.
        Default behavior sets up no stratifiers.
        """
        self.outputDataHandler.addEncompassedFeatureStratifier()
        self.outputDataHandler.addPlaceholderStratifier()
        self.outputDataHandler.addCustomSupplementalInformationHandler(SimpleColumnSupInfoHandler(
            outputName = "Gene_Locus", relevantData = ENCOMPASSING_DATA, dataCol = 1, separator = '$'
        ))
        self.outputDataHandler.addCustomSupplementalInformationHandler(SimpleColumnSupInfoHandler(
            outputName = "Gene_Annotation", relevantData = ENCOMPASSING_DATA, dataCol = 9, separator = '$'
        ))


    def setupOutputDataWriter(self):
        """
        Use this funciton to set up the output data writer.
        Default behavior creates the output data writer with the counter's "outputFilePath" value
        """
        self.outputDataHandler.createOutputDataWriter(self.outputFilePath,
                                                      oDSSubs = [None, 8, 9], omitFinalStratificationCounts = True)


    def constructEncompassingFeature(self, line) -> GeneAnnotationData:
        return GeneAnnotationData(line, self.acceptableChromosomes)


class ExonChecker(ThisInThatCounter):

    def getCountDerivatives(outputDataWriter: OutputDataWriter, getHeaders):
        if getHeaders: return ["Exon_Or_Intron"]
        else:
            if outputDataWriter.outputDataStructure[outputDataWriter.previousKeys[0]][None]: return ["Exon"]
            else: return ["Intron"]

    def initOutputDataHandler(self):
        """
        Use this function to create the instance of the CounterOutputDataHandler object.
        Default behavior creates the output data handler and passes in the counter's "writeIncrementally" value.
        """
        self.outputDataHandler = CounterOutputDataHandler(self.writeIncrementally, trackAllEncompassed = True)


    def setupOutputDataStratifiers(self):
        """
        Use this function to set up any output data stratifiers for the output data handler.
        Default behavior sets up no stratifiers.
        """
        self.outputDataHandler.addEncompassedFeatureStratifier()
        self.outputDataHandler.addPlaceholderStratifier()


    def setupOutputDataWriter(self):
        """
        Use this funciton to set up the output data writer.
        Default behavior creates the output data writer with the counter's "outputFilePath" value
        """
        self.outputDataHandler.createOutputDataWriter(self.outputFilePath, getCountDerivatives=ExonChecker.getCountDerivatives,
                                                      oDSSubs = [None, 10], omitFinalStratificationCounts = True)


def annotatePeaks(narrowPeakFilePaths: List[str], annotatedGenesFilePath: str,
                  exonsFilePath: str, genomeFastaFilePath: str, filterInsignificantPeaks):

    for narrowPeakFilePath in narrowPeakFilePaths:

        print(f"\nWorking with {os.path.basename(narrowPeakFilePath)}")

        mainDirectory = os.path.dirname(narrowPeakFilePath)
        tempDirectory = os.path.join(mainDirectory, ".tmp")
        checkDirs(tempDirectory)
        basename = os.path.basename(narrowPeakFilePath).rsplit('.', 1)[0]

        geneAnnotatedOutputFilePath = os.path.join(tempDirectory, basename + "_gene_annotation.bed")
        exonAnnotatedFilePath = os.path.join(tempDirectory, basename + "_gene_and_exon_annotated.bed")
        peakSequencesFilePath = os.path.join(tempDirectory, basename + "_peak_sequences.fa")
        finalAnnotatedFilePath = os.path.join(mainDirectory, basename + "_full_annotation.bed")

        if filterInsignificantPeaks:
            filteredNarrowPeakFilePath = os.path.join(tempDirectory, basename + "_significance_filtered.narrowPeak")
            with open(narrowPeakFilePath, 'r') as narrowPeakFile:
                with open(filteredNarrowPeakFilePath, 'w') as filteredNarrowPeakFile:
                    for line in narrowPeakFile:
                        if line.strip().split('\t')[4] == "1000": filteredNarrowPeakFile.write(line)
            narrowPeakFilePath = filteredNarrowPeakFilePath

        print("Checking for encompassing genes...")
        annotator = GeneDataAnnotator(narrowPeakFilePath, annotatedGenesFilePath, geneAnnotatedOutputFilePath,
                                      headersInEncompassingFeatures = True, checkForSortedFiles=(True,False),
                                      writeIncrementally = ENCOMPASSED_DATA, sortOutputOnExit=True)
        annotator.count()

        print("Checking for encompassing exons...")
        exonChecker = ExonChecker(geneAnnotatedOutputFilePath, exonsFilePath, exonAnnotatedFilePath,
                                      writeIncrementally = ENCOMPASSED_DATA, sortOutputOnExit=True)
        exonChecker.count()

        print("Adding peak sequences...")
        bedToFasta(narrowPeakFilePath, genomeFastaFilePath, peakSequencesFilePath)
        with open(peakSequencesFilePath, 'r') as peakSequencesFile:
            with open(exonAnnotatedFilePath, 'r') as exonAnnotatedFile:
                with open(finalAnnotatedFilePath, 'w') as finalAnnotatedFile:
                    for fastaEntry in FastaFileIterator(peakSequencesFile):
                        choppedUpLine = exonAnnotatedFile.readline().strip().split('\t')
                        # Adjust the exon indicator if this is not actually a genic region.
                        if choppedUpLine[8] == "NONE" and choppedUpLine[9] == "NONE":
                            choppedUpLine[10] = "NA"
                        choppedUpLine.append(fastaEntry.sequence)
                        finalAnnotatedFile.write('\t'.join(choppedUpLine) + '\n')


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data"),
                       title = "Annotate Seclip Peaks") as dialog:
        dialog.createMultipleFileSelector("Narrow Peaks Files:", 0, ".narrowPeak", ("Narrow Peak Files", ".narrowPeak"))
        dialog.createFileSelector("Gene Annotation File", 1, ("TSV Files", ".tsv"))
        dialog.createFileSelector("Exons File:", 2, ("Bed Files", ".bed"))
        dialog.createFileSelector("Genome Fasta File:", 3, ("Fasta Files", ".fa"))
        dialog.createCheckbox("Filter out insignificant peaks", 4, 0)

    selections = dialog.selections

    annotatePeaks(filterTempFiles(selections.getFilePathGroups()[0]), selections.getIndividualFilePaths()[0],
                  selections.getIndividualFilePaths()[1], selections.getIndividualFilePaths()[2],
                  selections.getToggleStates()[0])


if __name__ == "__main__": main()