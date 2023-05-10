# This script takes a tsv file of replication timepoints throughout the genome and uses it to assign replication times
# to a bed file of single-nucleotide genome features (e.g. mutations).
# NOTE: Both files must be sorted, first on chromosome, and then on position.
import sys


class TimelessFeature:
    """
    A genomic feature (e.g. mutation) without replication timing associated with it.
    """

    def __init__(self, bedLine: str):
        splitBedLine = bedLine.strip().split('\t')
        self.chromosome = splitBedLine[0]
        self.pos = int(splitBedLine[2])


class ReplicationTimeRange:
    """
    A range of two genomic positions with associated replication times.
    """

    def __init__(self):
        self.startChr = None; self.endChr = None
        self.startPos = None; self.endPos = None
        self.startTime = None; self.endTime = None

    def shiftRange(self, repTimeLine: str):
        """
        Uses a given line from a replication timing file to shift the range, using the new line as the new endpoint
        and moving the previous endpoint to the starting point.
        """
        splitRepTimeLine = repTimeLine.strip().split('\t')
        self.startChr = self.endChr; self.startPos = self.endPos; self.startTime = self.endTime
        self.endChr = splitRepTimeLine[0]
        self.endPos = int(splitRepTimeLine[1])
        self.endTime = float(splitRepTimeLine[2])

    def isValidRange(self):
        """
        Determines if the current ReplicationTimeRange is valid. (The range is invalid if uninitialized or spanning chromosomes.)
        """
        return self.startChr is not None and self.startChr == self.endChr

    def getRepTimeWithinRange(self, timelessFeature: TimelessFeature):
        """
        Extrapolates a replication time for a given timeless feature.
        NOTE: It is assumed that the range is valid and the position falls within the range. Further extrapolation is unreliable.
        """
        posRange = self.endPos - self.startPos
        timeRange = self.endTime - self.startTime
        relativeTimelessPos = timelessFeature.pos - self.startPos
        return relativeTimelessPos / posRange * timeRange + self.startTime

class ReplicationTimeAssigner:
    """
    The core object for the AssignReplicationTime script. The constructor takes a path to a tsv file containing replication
    times throughout the genome and a path to a bed file containing "timeless" genomic positions to assign times to.
    The main function "AssignReplicationTimes" extrapolates replicatiton times for the "timeless" genomic positions
    and writes the bed lines with these times (or "NA" if no replication timem could be assigned) to a new output file.
    """

    def __init__(self, replicationTimesFilePath: str, timelessFeaturesFilePath: str):

        self.timelessFeaturesFile = open(timelessFeaturesFilePath, 'r')
        self.replicationTimesFile = open(replicationTimesFilePath, 'r')

        # Create the output file path as a derivative of the encompassed features file path
        self.timedFeaturesFilePath = timelessFeaturesFilePath.rsplit(".bed", 1)[0] + "_rep_time.bed"
        self.timedFeaturesFile = open(self.timedFeaturesFilePath, 'w')

        # Skip the header in the replication times file.
        self.replicationTimesFile.readline()

        # Initialize the first timeless feature and the first replication time range endpoint.
        self.timelessFeaturesEOF = False
        self.replicationTimesEOF = False
        self.timelessFeature = None
        self.getNextTimelessFeature()
        self.replicationTimeRange = ReplicationTimeRange()
        self.shiftReplicationTimeRange()


    def __del__(self):
        """
        Clean up (close) open files.
        """
        self.replicationTimesFile.close()
        self.timelessFeaturesFile.close()
        self.timedFeaturesFile.close()

    def getNextTimelessFeature(self):
        """
        Read a line from the timeless features file and as long EOF hasn't been reached, 
        update the timeless feature using that line.
        """
        self.timelessFeatureLine = self.timelessFeaturesFile.readline()
        if self.timelessFeatureLine: self.timelessFeature = TimelessFeature(self.timelessFeatureLine)
        else: self.timelessFeaturesEOF = True

    def shiftReplicationTimeRange(self):
        """
        Read a line from the replication timing file and as long EOF hasn't been reached, 
        shift the replication time range using that line.
        """
        replicationTimeLine = self.replicationTimesFile.readline()
        if replicationTimeLine: self.replicationTimeRange.shiftRange(replicationTimeLine)
        else: self.replicationTimesEOF = True

    def assignReplicationTime(self):
        """
        The core function for this object. Iterates through both input files, assigning replication time
        values as appropriate and writing the results to a new file.
        """
        while not self.timelessFeaturesEOF and not self.replicationTimesEOF:

            # If the replication time range is on an earlier chromosome, shift the replication time range.
            if self.replicationTimeRange.endChr < self.timelessFeature.chromosome: self.shiftReplicationTimeRange()
                
            # If the timeless feature is on an earlier chromosome, record it without a valid replication time and
            # get the next timeless feature.
            elif self.replicationTimeRange.endChr > self.timelessFeature.chromosome:
                self.timedFeaturesFile.write(self.timelessFeatureLine.strip() + "\tNA\n")
                self.getNextTimelessFeature()

            # If the timeless feature is beyond the replication time range, shift the replication time range.
            elif self.replicationTimeRange.endPos < self.timelessFeature.pos: self.shiftReplicationTimeRange()

            # If all the above conditions were false, the timeless feature comes before (or at) the replication time range end,
            # and two things need to be done:
            # 1. Assign a time (or NA if there is no valid replication time range) to the feature and write it.
            # 2. Read in a new timeless feature.
            else:

                if self.timelessFeature.pos == self.replicationTimeRange.endPos:
                    self.timedFeaturesFile.write(self.timelessFeatureLine.strip() +
                                                 f"\t{self.replicationTimeRange.endTime:.3f}\n")
                elif self.replicationTimeRange.isValidRange():
                    thisRepTime = self.replicationTimeRange.getRepTimeWithinRange(self.timelessFeature)
                    self.timedFeaturesFile.write(self.timelessFeatureLine.strip() + f"\t{thisRepTime:.3f}\n")
                else:
                    self.timedFeaturesFile.write(self.timelessFeatureLine.strip() + "\tNA\n")

                self.getNextTimelessFeature()

        # If there are any remaining lines in the timeless feature file, write them with a replication time of "NA"
        while not self.timelessFeaturesEOF:
            self.timedFeaturesFile.write(self.timelessFeatureLine.strip() + "\tNA\n")
            self.getNextTimelessFeature()


if __name__ == "__main__":
    # Get the input files from the command line. (Replication times first, followed by encompassed features)
    ReplicationTimeAssigner(sys.argv[1], sys.argv[2]).assignReplicationTime()