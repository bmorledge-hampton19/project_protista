# This script converts from paired-end MNase data in bed format to a format highlighting proposed dyad centers.
# This is accomplished by first converting the paired-end bed data to unpaired nucleosome
# midpoints, which are assumed to be 73 bp 3' from the 5' end of each entry.
# Next, the resulting data is sorted and optionally converted to fixed-step wig, or a wig-like bed format. (for
# use in the BBG pipeline)
import os, subprocess
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.FileSystemHandling.DirectoryHandling import checkDirs

SIMPLE_BED = "Simple bed"
FIXED_STEP_WIG = "Fixed-step wig"
WIG_LIKE_BED = "Wig-like bed"
STRANDED_WIG_LIKE_BED = "Stranded wig-like bed"

# Given a list of bed files with paired entries, convert each to a fixed step wig file containing
# counts for nucleosome midpoints. Note that this requires a chrom.sizes file as well.
# Output format can be either fixed-step wig or a wig-like bed, containing bed entries with counts in
# the fourth (index 3) column
# Returns a list of the generated nucleosome file paths.
def bedMNasePEToNucleosomeMids(bedFilePaths: List[str], chromSizesFilePath, outputFormat):

    nucleosomeMidsOutputFilePaths = list()

    for bedFilePath in bedFilePaths:

        print(f"\nWorking with {os.path.basename(bedFilePath)}")

        # Create paths to output files.
        tempDir = os.path.join(os.path.dirname(bedFilePath), ".tmp")
        checkDirs(tempDir)
        basename = os.path.basename(bedFilePath).rsplit('.',1)[0]
        if outputFormat == SIMPLE_BED:
            bedNucleosomeMidsFilePath = os.path.join(os.path.dirname(bedFilePath), basename+"_nucleosome_mids.bed")
        else:
            bedNucleosomeMidsFilePath = os.path.join(tempDir, basename+"_nucleosome_mids.bed")
        wigNucleosomeMidsFilePath = os.path.join(os.path.dirname(bedFilePath), basename+"_nucleosome_mids.wig")
        wigLikeNucleosomeMidsFilePath = os.path.join(os.path.dirname(bedFilePath), basename+"_wig-like_nucleosome_mids.bed")
        strandedWigLikeNucleosomeMidsFilePath = os.path.join(os.path.dirname(bedFilePath), basename+"_wig-like_nucleosome_mids_stranded.bed")

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

                    if midpointStart < 73: continue

                    bedNucleosomeMidsFile.write('\t'.join((splitLine[0], str(midpointStart), str(midpointEnd),
                                                           '.', splitLine[4], splitLine[5])) + '\n')

        # Sort the nucleosome mids bed file in place.
        print("Sorting midpoints...")
        subprocess.check_call(("sort","-k1,1","-k2,2n", "-k6,6", "-s", "-o", bedNucleosomeMidsFilePath, bedNucleosomeMidsFilePath))

        # If "Fixed-step wig" output was selected, convert the file to a fixed step (1) wig file using the chrom.sizes dictionary.
        if outputFormat == FIXED_STEP_WIG:

            print("Parsing chrom.sizes file...")
            chromSizes = dict()
            with open(chromSizesFilePath, 'r') as chromSizesFile:
                for line in chromSizesFile:
                    chromosome, size = line.strip().split('\t')
                    chromSizes[chromosome] = int(size)

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
                        while bedEntryPos > currentPos:
                            wigNucleosomeMidsFile.write(str(currentCount) + '\n')
                            currentCount = 0
                            currentPos += 1
                        assert bedEntryPos == currentPos, f"Bed entry: {splitLine}\nCurrent position: {currentPos}"
                        currentCount += 1

                    # Make sure to finish the current chromosome in the wig file after iterating through the bed file.
                    if currentChrom is not None:
                        wigNucleosomeMidsFile.write(str(currentCount) + '\n')
                        currentPos += 1
                        while currentPos <= maxPos:
                            wigNucleosomeMidsFile.write("0\n")
                            currentPos += 1

            nucleosomeMidsOutputFilePaths.append(wigNucleosomeMidsFilePath)

        # If "Wig-like bed" output was selected, count/merge bed entries to create the wig-like bed output.
        elif outputFormat == WIG_LIKE_BED:

            print("Converting to wig-like bed file...")
            with open(bedNucleosomeMidsFilePath, 'r') as bedNucleosomeMidsFile:
                with open(wigLikeNucleosomeMidsFilePath, 'w') as wigLikeNucleosomeMidsFile:

                    lastEntry = None
                    currentCount = 0
                    for line in bedNucleosomeMidsFile:
                        splitLine = line.strip().split('\t')

                        # Compare this entry with the last. If it matches, just iterate the count.
                        # If it doesn't, write the last Entry and its count and reset both.
                        if lastEntry is not None and lastEntry[:2] == splitLine[:2]: currentCount += 1
                        else:
                            if lastEntry is not None: wigLikeNucleosomeMidsFile.write('\t'.join(lastEntry[:3] + [str(currentCount)]) + '\n')
                            lastEntry = splitLine
                            currentCount = 1
                    
                    # Make sure to finish the current entry after iterating through the bed file.
                    if lastEntry is not None: wigLikeNucleosomeMidsFile.write('\t'.join(lastEntry[:3] + [str(currentCount)]) + '\n')
                        
            nucleosomeMidsOutputFilePaths.append(wigLikeNucleosomeMidsFilePath)

        # If "Stranded wig-like bed" output was selected, count/merge bed entries to create the wig-like bed output preserving strand information.
        elif outputFormat == STRANDED_WIG_LIKE_BED:

            print("Converting to wig-like bed file with strand information...")
            with open(bedNucleosomeMidsFilePath, 'r') as bedNucleosomeMidsFile:
                with open(strandedWigLikeNucleosomeMidsFilePath, 'w') as strandedWigLikeNucleosomeMidsFile:

                    lastEntry = None
                    currentCount = 0
                    for line in bedNucleosomeMidsFile:
                        splitLine = line.strip().split('\t')

                        # Compare this entry with the last. If it matches, just iterate the count.
                        # If it doesn't, write the last Entry and its count and reset both.
                        if lastEntry is not None and lastEntry[:2] + [lastEntry[5]] == splitLine[:2] + [splitLine[5]]: currentCount += 1
                        else:
                            if lastEntry is not None:
                                strandedWigLikeNucleosomeMidsFile.write('\t'.join(lastEntry[:3] + [str(currentCount), '.', lastEntry[5]]) + '\n')
                            lastEntry = splitLine
                            currentCount = 1
                    
                    # Make sure to finish the current entry after iterating through the bed file.
                    if lastEntry is not None:
                        strandedWigLikeNucleosomeMidsFile.write('\t'.join(lastEntry[:3] + [str(currentCount), '.', lastEntry[5]]) + '\n')
                        
            nucleosomeMidsOutputFilePaths.append(wigLikeNucleosomeMidsFilePath)


    return nucleosomeMidsOutputFilePaths

def main():
    
    # Get the working directory from mutperiod if possible. Otherwise, just use this script's directory.
    try:
        from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
        workingDirectory = getDataDirectory()
    except ImportError:
        workingDirectory = os.path.dirname(__file__)

    with TkinterDialog(workingDirectory = workingDirectory) as dialog:
        dialog.createMultipleFileSelector("MNase PE Bed Files:", 0, ".bed", ("Bed Files", ".bed"))
        with dialog.createDynamicSelector(1, 0) as outputFormatDynSel:
            outputFormatDynSel.initDropdownController("Output format:", (SIMPLE_BED, FIXED_STEP_WIG, WIG_LIKE_BED, STRANDED_WIG_LIKE_BED))
            outputFormatDynSel.initDisplay(FIXED_STEP_WIG, FIXED_STEP_WIG).createFileSelector(
                "chrom.sizes File:", 0, ("chrom.sizes File", ".chrom.sizes")
            )

    if outputFormatDynSel.getControllerVar() != FIXED_STEP_WIG: chromSizesFilePath = None
    else: chromSizesFilePath = dialog.selections.getIndividualFilePaths(FIXED_STEP_WIG)[0]
    bedMNasePEToNucleosomeMids(dialog.selections.getFilePathGroups()[0],
                                  chromSizesFilePath, outputFormatDynSel.getControllerVar())


if __name__ == "__main__": main()