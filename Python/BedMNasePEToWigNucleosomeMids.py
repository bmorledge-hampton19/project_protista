# This script converts from paired-end MNase data in bed format to a format suitable for the BBG lab's nucleoosme
# calling pipeline. This is accomplished by first converting the paired-end bed data to unpaired nucleosome
# midpoints, which are assumed to be 73 bp 3' from the 5' end of each entry. Next, the resulting data is
# sorted and converted to fixed-step wig format.
import os, subprocess
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.FileSystemHandling.DirectoryHandling import checkDirs

# Given a list of bed files with paired entries, convert each to a fixed step wig file containing
# counts for nucleosome midpoints. Note that this requires a chrom.sizes file as well.
# Returns a list of the generated nucleosome mids wig file paths.
def bedMNasePEToWigNucleosomeMids(bedFilePaths: List[str], chromSizesFilePath):

    wigNucleosomeMidsFilePaths = list()

    # Parse the chrom.sizes file into a dictionary.
    print("Parsing chrom.sizes file...")
    chromSizes = dict()
    with open(chromSizesFilePath, 'r') as chromSizesFile:
        for line in chromSizesFile:
            chromosome, size = line.strip().split('\t')
            chromSizes[chromosome] = int(size)

    for bedFilePath in bedFilePaths:

        print(f"Working with {os.path.basename(bedFilePath)}")

        # Create paths to output files.
        tempDir = os.path.join(os.path.dirname(bedFilePath), ".tmp")
        checkDirs(tempDir)
        basename = os.path.basename(bedFilePath).rsplit('.',1)[0]
        bedNucleosomeMidsFilePath = os.path.join(tempDir, basename+"_nucleosome_mids.bed")
        wigNucleosomeMidsFilePath = os.path.join(os.path.dirname(bedFilePath), basename+"_nucleosome_mids.wig")

        
        # Get the nucleosome mid points (estimated) from the paired end reads.
        print("Retrieving midpoints from paired reads...")
        with open(bedFilePath, 'r') as bedFile:
            with open(bedNucleosomeMidsFilePath, 'w') as bedNucleosomeMidsFile:
                for line in bedFile:
                    splitLine = line.strip().split('\t')

                    if splitLine[5] == '+':
                        midpointStart = int(splitLine[1]) + 73
                        midpointEnd = midpointStart + 1
                    elif splitLine[5] == '-':
                        midpointEnd = int(splitLine[2]) - 73
                        midpointStart = midpointEnd - 1

                    bedNucleosomeMidsFile.write('\t'.join((splitLine[0], str(midpointStart), str(midpointEnd),
                                                           '.', splitLine[4], '.')) + '\n')
        
        # Sort the nucleosome mids bed file in place.
        print("Sorting midpoints...")
        subprocess.check_call(("sort","-k1,1","-k2,2n", "-k3,3n", "-s", "-o", bedNucleosomeMidsFilePath, bedNucleosomeMidsFilePath))

        # Convert the file to a fixed step (1) wig file using the chrom.sizes dictionary.
        print("Converting to fixed step wig file...")
        with open(bedNucleosomeMidsFilePath, 'r') as bedNucleosomeMidsFile:
            with open(wigNucleosomeMidsFilePath, 'w') as wigNucleosomeMidsFile:

                currentChrom = None
                for line in bedNucleosomeMidsFile:
                    splitLine = line.strip().split('\t')

                    # Check for a new (or the first) chromsoome.
                    if currentChrom is None or splitLine[0] != currentChrom:
                        # Make sure to finish the last chromosome.
                        if currentChrom is not None:
                            wigNucleosomeMidsFile.write(str(currentCount) + '\n')
                            currentPos += 1
                            while currentPos <= maxPos:
                                wigNucleosomeMidsFile.write("0\n")
                                currentPos += 1

                        currentChrom = splitLine[0]
                        print(f"Creating fixed step entry for {currentChrom}")
                        maxPos = chromSizes[currentChrom]
                        currentPos = 1
                        currentCount = 0
                        wigNucleosomeMidsFile.write(f"fixedStep chrom={splitLine[0]} start=1 step=1\n")

                    # For each bed entry, see if we've reached it in the wig file. Once we have, increment current count.
                    # Otherwise, step through the wig file until we reach the bed entry, writing counts as we go.
                    bedEntryPos = int(splitLine[2])
                    while bedEntryPos != currentPos:
                        wigNucleosomeMidsFile.write(str(currentCount) + '\n')
                        currentCount = 0
                        currentPos += 1
                    currentCount += 1
                
                # Make sure to finish the current chromosome in the wig file after iterating through the bed file.
                if currentChrom is not None:
                    wigNucleosomeMidsFile.write(str(currentCount) + '\n')
                    currentPos += 1
                    while currentPos <= maxPos:
                        wigNucleosomeMidsFile.write("0\n")
                        currentPos += 1

        wigNucleosomeMidsFilePaths.append(wigNucleosomeMidsFilePath)

    return wigNucleosomeMidsFilePaths

def main():
    
    # Get the working directory from mutperiod if possible. Otherwise, just use this script's directory.
    try:
        from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
        workingDirectory = getDataDirectory()
    except ImportError:
        workingDirectory = os.path.dirname(__file__)

    with TkinterDialog(workingDirectory = workingDirectory) as dialog:
        dialog.createMultipleFileSelector("MNase PE Bed Files:", 0, ".bed", ("Bed Files", ".bed"))
        dialog.createFileSelector("chrom.sizes File:", 1, ("chrom.sizes File", ".chrom.sizes"))

    bedMNasePEToWigNucleosomeMids(dialog.selections.getFilePathGroups()[0], dialog.selections.getIndividualFilePaths()[0])


if __name__ == "__main__": main()