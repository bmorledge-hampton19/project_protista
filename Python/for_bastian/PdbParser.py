# This script converts super jank pdb files into nice tsv files without entries that are merged for no conceivable reason.
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from typing import List
import os


def pdbParserBySplit(pdbFilePaths: List[str]):
    """
    Given one or more pdb file paths, splits on whitespace and searches for merged columns to un-merge.
    Outputs the data in tab-delimited format to a new file path.
    """

    for pdbFilePath in pdbFilePaths:

        print("Parsing by splitting and un-merging in", os.path.basename(pdbFilePath))

        # Create a path for the output file by simpling appending the ".tsv" file extension
        pdbOutputFilePath = pdbFilePath + ".tsv"

        with open(pdbFilePath, 'r') as pdbFile:
            with open(pdbOutputFilePath, 'w') as pdbOutputFile:

                for line in pdbFile:

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

                    pdbOutputFile.write('\t'.join(outputSplitLine) + '\n')


def pdbParserByIndex(pdbFilePaths: List[str]):
    """
    Given one or more pdb file paths, retrieve relevant columns based on character positions (indices).
    Outputs the data in tab-delimited format to a new file path.
    """

    for pdbFilePath in pdbFilePaths:

        print("Parsing by index in", os.path.basename(pdbFilePath))

        # Create a path for the output file by simpling appending the ".tsv" file extension
        pdbOutputFilePath = pdbFilePath + ".tsv"

        with open(pdbFilePath, 'r') as pdbFile:
            with open(pdbOutputFilePath, 'w') as pdbOutputFile:

                # For every line in the file, parse out the relevant information by index.
                for line in pdbFile:

                    # Make sure we're looking at an ATOM line.
                    if line[0:6].strip() != "ATOM": continue

                    name = line[12:16].strip()
                    residueName = line[17:20].strip()
                    chainID = line[21].strip()
                    resSeqNum = line[22:26].strip()
                    xPos = line[30:38].strip()
                    yPos = line[38:46].strip()
                    zPos = line[46:54].strip()
                    tempFactor = line[60:66].strip()

                    # Wrapt the relevant data and make sure there are values for each one.
                    relevantData = (name, residueName, chainID, resSeqNum, xPos, yPos, zPos, tempFactor)
                    for data in relevantData: assert data, "Data point missing: " + '\n\t' + str(relevantData) + '\n\t' + line

                    # Write the new line with the relevant information.
                    pdbOutputFile.write('\t'.join(relevantData) + '\n')


def main():

    #Create the Tkinter UI
    dialog = TkinterDialog(workingDirectory=os.path.dirname(__file__))
    dialog.createMultipleFileSelector("pdb Files:", 0, ".pdb", ("pdb Files", ".pdb"))
    dialog.createDropdown("Parse Method", 1, 0, ("By Split", "By Index"))

    # Run the UI
    dialog.mainloop()

    # If no input was received (i.e. the UI was terminated prematurely), then quit!
    if dialog.selections is None: quit()

    if dialog.selections.getDropdownSelections()[0] == "By Split":
        pdbParserBySplit(dialog.selections.getFilePathGroups()[0])
    elif dialog.selections.getDropdownSelections()[0] == "By Index":
        pdbParserByIndex(dialog.selections.getFilePathGroups()[0])

if __name__ == "__main__": main()