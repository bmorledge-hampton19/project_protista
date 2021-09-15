# This script converts super jank pdb files into nice tsv files without entries that are merged for no conceivable reason.
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from typing import List
import os


def pdbParser(pdfFilePaths: List[str]):
    """
    Given one or more pdb file paths, searches for merged columns and un-merges them.
    Outputs the data in tab-delimited format to a new file path.
    """

    for pdfFilePath in pdfFilePaths:

        print("Working in", os.path.basename(pdfFilePath))

        # Create a path for the output file by simpling appending the ".tsv" file extension
        pdfOutputFilePath = pdfFilePath + ".tsv"

        with open(pdfFilePath, 'r') as pdfFile:
            with open(pdfOutputFilePath, 'w') as pdfOutputFile:

                for line in pdfFile:

                    splitLine = line.split()

                    # For lines designated "ATOM" prepare to demerge...
                    if splitLine[0] == "ATOM":

                        # Parse the first 4 values directly from the first 4 columns.
                        outputSplitLine = splitLine[:4]
                        usedValues = 4

                        # The 5th and 6th values may be merged in the 5th column.  Operate on the assumption that
                        # The 5th value will always be one character.
                        if len(splitLine[4]) != 1:
                            outputSplitLine.append(splitLine[4][0])
                            outputSplitLine.append(splitLine[4][1:])
                            usedValues += 1
                        else:
                            outputSplitLine.extend(splitLine[4:6])
                            usedValues += 2

                        # Make sure we didn't overflow into any of the columns with decimal values.
                        for col in outputSplitLine:
                            assert '.' not in col, splitLine

                        # For the remaining values in the split list, search for the decimal points that should each
                        # be indicative of one data point.  In the event that a single value has multiple decimal points,
                        # use the following information to split up the value into multiple values for each decimal point:
                        #   The first three values represent XYZ coordinates and appear to have 3 characters after the decimal.
                        #   The next two values represent B-factor and appear to have 2 characters after the decimal.
                        decimalsFound = 0
                        while decimalsFound < 5: # Use values until we have found all five decimals

                            currentValue = splitLine[usedValues]
                            decimalsInCurrentValue = currentValue.count('.')
                            assert decimalsInCurrentValue > 0, splitLine # Did we actually get a value with a decimal?

                            while decimalsInCurrentValue > 1: # Unmerge until we have one decimal

                                if decimalsFound < 3: lastUnmergedIndex = currentValue.find('.') + 3
                                else: lastUnmergedIndex = currentValue.find('.') + 2

                                unmergedValue = currentValue[:lastUnmergedIndex + 1]

                                assert unmergedValue.count('.') == 1, splitLine # Do we have exactly one decimal?
                                try: float(unmergedValue) # Do we actually have a valid number?
                                except ValueError: print(splitLine)

                                outputSplitLine.append(unmergedValue)
                                currentValue = currentValue[lastUnmergedIndex + 1:]
                                decimalsInCurrentValue -= 1
                                decimalsFound += 1

                            outputSplitLine.append(currentValue)
                            decimalsFound += 1

                            usedValues += 1

                        # Once 5 decimals have been found, there should be exactly one argument remaining.  Append it.
                        assert usedValues + 1 == len(splitLine), splitLine
                        outputSplitLine.append(splitLine[-1])


                    else: outputSplitLine = splitLine

                    pdfOutputFile.write('\t'.join(outputSplitLine) + '\n')



def main():

    #Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=os.path.dirname(__file__))
    dialog.createMultipleFileSelector("pdb Files:", 0, ".pdb", ("pdb Files", ".pdb"))

    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    pdbParser(dialog.selections.getFilePathGroups()[0])

if __name__ == "__main__": main()