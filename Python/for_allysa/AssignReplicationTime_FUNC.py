# This script takes a tsv file of replication timepoints throughout the genome and uses it to assign replication times
# to a bed file of single-nucleotide genome features (e.g. mutations).
# NOTE: Both files must be sorted, first on chromosome, and then on position.
import sys


def getReplicationTimeInfo(replicationTimeLine: str):
    """
    Returns a list containing the chromosome, 1-based position, and replication time for the given replication time line.
    """
    splitReplicationTimeLine = replicationTimeLine.strip().split('\t')
    return([splitReplicationTimeLine[0], int(splitReplicationTimeLine[1]), float(splitReplicationTimeLine[2])])


def getTimelessFeatureInfo(timelessFeatureLine: str):
    """
    Returns a list containing the chromosome and 1-based position for the given timeless feature line.
    """
    splitTimelessFeatureLine = timelessFeatureLine.strip().split('\t')
    return([splitTimelessFeatureLine[0], int(splitTimelessFeatureLine[2])])


def assignReplicationTime(replicationTimesFilePath: str, timelessFeaturesFilePath: str):
    """
    The core function for the AssignReplicationTime script. As input, takes a path to a tsv file containing replication times
    throughout the genome and a path to a bed file containing genomic positions to assign times to. Writes the genomic
    positions along with replication time (or "NA" if no replication timem could be assigned) to a new output file and
    returns its path.
    """

    # Create the output file path as a derivative of the encompassed features file path
    timedFeaturesFilePath = timelessFeaturesFilePath.rsplit(".bed", 1)[0] + "_rep_time.bed"

    with open(replicationTimesFilePath, 'r') as replicationTimesFile, \
         open(timelessFeaturesFilePath, 'r') as timelessFeaturesFile, \
         open(timedFeaturesFilePath, 'w') as timedFeaturesFile:

        # Skip the header in the replication times file.
        replicationTimesFile.readline()

        # Read in the first line for each file.
        repTimeLine = replicationTimesFile.readline()
        timelessFeatureLine = timelessFeaturesFile.readline()

        # As long as the first lines exist (i.e. empty files were not passed), extract their information.
        if repTimeLine and timelessFeatureLine:
            repTimeRangeEndChr, repTimeRangeEndPos, repTimeRangeEndTime = getReplicationTimeInfo(repTimeLine)
            # Also make it clear that there is a not a continuous range in the first chromosome yet.
            repTimeRangeStartChr = "NOT_A_CHROMOSOME"
            timelessFeatureChr, timelessFeaturePos, = getTimelessFeatureInfo(timelessFeatureLine)

        # Iterate through the files in parallel until the end of one is reached.
        while repTimeLine and timelessFeatureLine:

            # Check if chromosomes are unequal, and if they are, advance the data with the earlier chromosome.
            if repTimeRangeEndChr < timelessFeatureChr:
                repTimeRangeStartChr, repTimeRangeStartPos, repTimeRangeStartTime = \
                    repTimeRangeEndChr, repTimeRangeEndPos, repTimeRangeEndTime
                repTimeLine = replicationTimesFile.readline()
                if repTimeLine:
                    repTimeRangeEndChr, repTimeRangeEndPos, repTimeRangeEndTime = getReplicationTimeInfo(repTimeLine)
                
            elif repTimeRangeEndChr > timelessFeatureChr:
                # If we're advancing the timeless feature because of chromosome inconsistencies, it also means that
                # it didn't fall into a valid replication time range and must be recorded as such.
                timedFeaturesFile.write(timelessFeatureLine.strip() + "\tNA\n")
                timelessFeatureLine = timelessFeaturesFile.readline()
                if timelessFeatureLine:
                    timelessFeatureChr, timelessFeaturePos, = getTimelessFeatureInfo(timelessFeatureLine)

            # If the timeless feature is beyond the replication time range, read in the next replication time line.
            elif repTimeRangeEndPos < timelessFeaturePos:
                repTimeRangeStartChr, repTimeRangeStartPos, repTimeRangeStartTime = \
                    repTimeRangeEndChr, repTimeRangeEndPos, repTimeRangeEndTime
                repTimeLine = replicationTimesFile.readline()
                if repTimeLine:
                    repTimeRangeEndChr, repTimeRangeEndPos, repTimeRangeEndTime = getReplicationTimeInfo(repTimeLine)

            # If all the above conditions were false, the timeless feature comes before (or at) the replication time range end,
            # and two things need to be done:
            # 1. Assign a time (or NA if there is no valid replication time range) to the feature and write it.
            # 2. Read in a new timeless feature.
            else:

                if timelessFeaturePos == repTimeRangeEndPos:
                    timedFeaturesFile.write(timelessFeatureLine.strip() + f"\t{repTimeRangeEndTime:.3f}\n")
                elif repTimeRangeStartChr == repTimeRangeEndChr:
                    repTimePosRange = repTimeRangeEndPos - repTimeRangeStartPos
                    repTimeTimeRange = repTimeRangeEndTime - repTimeRangeStartTime
                    relativeFeaturePos = timelessFeaturePos - repTimeRangeStartPos
                    thisRepTime = relativeFeaturePos / repTimePosRange * repTimeTimeRange + repTimeRangeStartTime
                    timedFeaturesFile.write(timelessFeatureLine.strip() + f"\t{thisRepTime:.3f}\n")
                else:
                    timedFeaturesFile.write(timelessFeatureLine.strip() + "\tNA\n")

                timelessFeatureLine = timelessFeaturesFile.readline()
                if timelessFeatureLine:
                    timelessFeatureChr, timelessFeaturePos, = getTimelessFeatureInfo(timelessFeatureLine)

        # If there are any remaining lines in the timeless feature file, write them with a replication time of "NA"
        while timelessFeatureLine:
            timedFeaturesFile.write(timelessFeatureLine.strip() + "\tNA\n")
            timelessFeatureLine = timelessFeaturesFile.readline()

    # Return the output file path.
    return timedFeaturesFilePath

if __name__ == "__main__":
    # Get the input files from the command line. (Replication times first, followed by encompassed features)
    assignReplicationTime(sys.argv[1], sys.argv[2])