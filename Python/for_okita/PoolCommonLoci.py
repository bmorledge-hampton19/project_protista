# This script takes multiple "common loci" files outputted from FindCommonLoci.py and
# pools them together into one file, which keeps track of which data sets contained which loci.
# A minimum required number of replicates can be specified to only pool loci that appear a certain
# number of times in their respective cohort. (e.g., Only include loci from data sets where that locus is present
# in at least 3 replicates.)

import os
from typing import List
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.CustomErrors import checkForNumber


def poolCommonLoci(commonLociFilePaths: List[str], outputFilePath: str, minimumReplicates: int):

    dataSetsByLocus = dict()
    functionByLocus = dict()

    for commonLociFilePath in commonLociFilePaths:

        if commonLociFilePath.endswith("_common_loci.tsv"):
            dataSetName = os.path.basename(commonLociFilePath).rsplit("_common_loci.tsv",1)[0]
        else: dataSetName = os.path.basename(commonLociFilePath).rsplit('.',1)[0]

        print(f"Documenting loci in {dataSetName}...")

        with open(commonLociFilePath, 'r') as commonLociFile:
            for line in commonLociFile:
                locus, function, replicates = line.strip().split('\t')
                if int(replicates) >= minimumReplicates:
                    if locus not in dataSetsByLocus:
                        dataSetsByLocus[locus] = [dataSetName]
                        functionByLocus[locus] = function
                    else: dataSetsByLocus[locus].append(dataSetName)

    print("Writing results...")
    with open(outputFilePath, 'w') as outputFile:
        for locus in sorted(dataSetsByLocus):
            outputFile.write('\t'.join((locus, functionByLocus[locus], ','.join(dataSetsByLocus[locus]))) + '\n')


def main():

    with TkinterDialog(workingDirectory = os.path.join(os.path.dirname(__file__),"..","..","data"),
                       title = "Seclip Pool Common Loci") as dialog:
        dialog.createMultipleFileSelector("Common Loci Files:", 0, "common_loci.tsv",
                                          ("tsv Files", ".tsv"))
        dialog.createTextField("Minimum common replicates:", 1, 0, defaultText="3")
        dialog.createFileSelector("Output File:", 2, ("Tab Separated Values File", ".tsv"), newFile=True)

    selections = dialog.selections

    poolCommonLoci(selections.getFilePathGroups()[0], selections.getIndividualFilePaths()[0],
                   checkForNumber(selections.getTextEntries()[0], enforceInt=True))


if __name__ == "__main__": main()