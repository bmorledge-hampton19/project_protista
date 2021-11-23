# Made to mirror Cameron's script which assigns domains to mutations.
import os
from benbiohelpers.CountThisInThat.OutputDataStratifiers import AmbiguityHandling
from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
from benbiohelpers.CountThisInThat.InputDataStructures import ENCOMPASSED_DATA
from benbiohelpers.CountThisInThat.Counter import ThisInThatCounter
from benbiohelpers.CountThisInThat.CounterOutputDataHandler import CounterOutputDataHandler
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.FileSystemHandling.DirectoryHandling import checkDirs
from typing import List


class DomainDesignationCounter(ThisInThatCounter):

    def initOutputDataHandler(self):
        self.outputDataHandler = CounterOutputDataHandler(self.writeIncrementally, trackAllEncompassed = True,
                                                          countNonCountedEncompassedAsNegative = True)

    def setupOutputDataWriter(self):
        self.outputDataHandler.createOutputDataWriter(self.outputFilePath, omitZeroRows = True, 
                                                      customStratifyingNames = (None,{None:"Overlapping_Domains"},None))

    def setupOutputDataStratifiers(self):
        self.outputDataHandler.addEncompassedFeatureStratifier()
        self.outputDataHandler.addSimpleEncompassingColStratifier(AmbiguityHandling.record, colIndex=3)
        self.outputDataHandler.addPlaceholderStratifier()


def designateDomains(genomeFeaturesFilePaths: List[str], domainDesignationsFilePath):

    for genomeFeaturesFilePath in genomeFeaturesFilePaths:

        print('\n' + "Working in",os.path.basename(genomeFeaturesFilePath))

        # First, count the number of times that each feature is found within a gene.
        print("Assigning domains to features...")
        intermediateDirectory = os.path.join(os.path.dirname(genomeFeaturesFilePath),"intermediate_files")
        checkDirs(intermediateDirectory)

        domainCountsOutputFilePath = os.path.join(intermediateDirectory,
                                                  os.path.basename(genomeFeaturesFilePath).rsplit('.',1)[0] + "_domain_counts.bed")
        outputWithDesignationsFilePath = genomeFeaturesFilePath.rsplit('.',1)[0] + "_with_domains.bed"
        
        counter = DomainDesignationCounter(genomeFeaturesFilePath, domainDesignationsFilePath, domainCountsOutputFilePath,
                                           writeIncrementally = ENCOMPASSED_DATA)
        counter.count()


        # Next, split up the bed entries into the genic and intergenic files based on whether or not they had any counts.
        print("Rewriting results to preserve original format with added domain designations...")
        with open(domainCountsOutputFilePath, 'r') as domainCountsOutputFile:
            with open(outputWithDesignationsFilePath, 'w') as outputWithDesignationsFile:

                for line in domainCountsOutputFile:

                    choppedUpLine = line.strip().split('\t')
                    counts = int(choppedUpLine[-1])
                    if counts > 0:
                        for _ in range(counts):
                            outputWithDesignationsFile.write('\t'.join(choppedUpLine[:-1]) + '\n')
                    elif counts < 0:
                        for _ in range(-counts):
                            outputWithDesignationsFile.write('\t'.join(choppedUpLine[:-2] + ["No_Domain_Found"]) + '\n')


def main():

    # Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=getDataDirectory())
    dialog.createMultipleFileSelector("Genome Feature Positions Files:",0,"context_mutations.bed",("Bed Files",".bed"))    
    dialog.createFileSelector("Domain Designations:",1,("Bed Files",".bed"))

    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    designateDomains(dialog.selections.getFilePathGroups()[0], dialog.selections.getIndividualFilePaths()[0])


if __name__ == "__main__": main()