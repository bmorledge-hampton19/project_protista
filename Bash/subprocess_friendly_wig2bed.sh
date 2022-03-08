# This script encapsulates the call to wig2bed so that
# the Python subprocess module can be used without redirects.
# 
# wig2bed can be installed via "sudo apt install bedops"

inputFile=$1; shift
outputFile=$1; shift

wig2bed -x < $inputFile > $outputFile