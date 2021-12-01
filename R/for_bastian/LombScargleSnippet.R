library(data.table)
library(lomb)

# This will automatically read the file of your choice into a data table structure, 
# separating on commas, tabs, etc. as necessary.
myData = fread(choose.files(multi = FALSE))

# Here, you'll need to pull out the columns corresponding to the counts and timepoints.
# If you don't have headers, the column names will automatically be set to V1, V2, etc.
times = myData$V1
measurements = myData$V2

# Then, feed it into the function!  Use the "from" and "to" values to specify periodicities to test.
# The "ofac" parameter will scan extra periodicities within the range you specified.  (I'm not exactly
# sure how it decides how many extras to scan, tbh, but 100 always seems like a good value to use.)
lombResult = lsp(measurements, times = times, from = 5, to = 25, type = "period", ofac = 100)

# Get the peak periodicity and its associated power.
peakPeriodicity = lombResult$peak.at[1]
peakPeriodicityPower = lombResult$peak

# Calculate SNR as the ratio of the peak periodicity power to the median of the powers of all other
# periodicities not within 0.5 units of the peak periodicity
noiseBooleanVector = (lombResult$scanned < relevantPeriodicity - 0.5
                      | lombResult$scanned > relevantPeriodicity + 0.5)
periodicitySNRs[i] = relevantPower / median(lombResult$power[noiseBooleanVector])