# This script converts from paired-end MNase data in bed format to a format suitable for paired end input in iNPS.
# This is accomplished by using each concordant pair in the input bed file to determine the original fragment ends.
# As a result, input MUST contain only concordant pairs, and all entries must be adjacent to their companion.
import os
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.CustomErrors import UserInputError

# Given a list of bed files with paired entries, convert each to a bed file of full fragments derived from
# each pair. Input bed files MUST contain only concordant pairs, and all entries must be adjacent to their companions.
# If set to true, the validateConcordantPairs parameter will run a check on the 4th (index 3) column of every
# pair of lines to make sure the above conditions are met. Returns a list of the generated output bed file paths.
def bedMNasePEToBediNPSFullFragments(bedFilePaths: List[str], validateConcordantPairs = True):

    fullFragmentsBedFilePaths = list()

    for bedFilePath in bedFilePaths:

        print(f"Working with {os.path.basename(bedFilePath)}")

        # Create the path to the output files.
        basename = os.path.basename(bedFilePath).rsplit('.',1)[0]
        fullFragmentsBedFilePath = os.path.join(os.path.dirname(bedFilePath), basename+"_iNPS_PE_full_fragments.bed")

        
        # Get the nucleosome mid points (estimated) from the paired end reads.
        if validateConcordantPairs: print("Converting to full fragments bed file while validating pairs...")
        else: print("Converting to full fragments bed file without validating pairs...")
        with open(bedFilePath, 'r') as bedFile:
            with open(fullFragmentsBedFilePath, 'w') as fullFragmentsBedFile:
                for companion1 in bedFile:
                    companion1 = companion1.strip().split('\t')
                    companion2 = bedFile.readline().strip().split('\t')

                    if validateConcordantPairs:
                        if (not companion1[3].endswith('1') or not companion2[3].endswith('2') or
                            companion1[3][:-1] != companion2[3][:-1]):
                            raise UserInputError(f"Found adjacent reads that are not ordered, "
                                                 f"concordant pairs:\n{companion1}\n{companion2}")

                    if companion1[5] == '+':
                        fullFragmentStart = companion1[1]
                        fullFragmentEnd = companion2[2]
                    elif companion2[5] == '+':
                        fullFragmentStart = companion2[1]
                        fullFragmentEnd = companion1[2]
                    else:
                        raise UserInputError("Neither entry in the following concordant pair is on the \'+\' strand.\n"
                                             f"{companion1}\n{companion2}")

                    fullFragmentsBedFile.write('\t'.join((companion1[0], fullFragmentStart, fullFragmentEnd)) + '\n')

        fullFragmentsBedFilePaths.append(fullFragmentsBedFilePath)

    return fullFragmentsBedFilePaths


def main():
    
    # Get the working directory from mutperiod if possible. Otherwise, just use this script's directory.
    try:
        from mutperiodpy.helper_scripts.UsefulFileSystemFunctions import getDataDirectory
        workingDirectory = getDataDirectory()
    except ImportError:
        workingDirectory = os.path.dirname(__file__)

    with TkinterDialog(workingDirectory = workingDirectory) as dialog:
        dialog.createMultipleFileSelector("MNase PE Bed Files:", 0, ".bed", ("Bed Files", ".bed"))
        dialog.createCheckbox("Validate concordant pairs", 1, 0)

    bedMNasePEToBediNPSFullFragments(dialog.selections.getFilePathGroups()[0], dialog.selections.getToggleStates()[0])


if __name__ == "__main__": main()