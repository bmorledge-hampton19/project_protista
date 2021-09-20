library(data.table)
library(ggplot2)

# A helper function for when I want to quickly get lomb results with SNR.
getPeakPeriodicityAndSNR = function(counts, lombFrom, lombTo, plot = FALSE) {
  
  # Calculate the periodicity of the data using a Lomb-Scargle periodiagram.
  lombResult = lomb::lsp(counts, type = "period", from = lombFrom, to = lombTo,
                         ofac = 100, plot = plot)
  
  # Get the peak periodicity and its associated SNR
  peakPeriodicity = lombResult$peak.at[1]
  noiseBooleanVector = (lombResult$scanned < peakPeriodicity - 0.5
                        | lombResult$scanned > peakPeriodicity + 0.5)
  SNR = lombResult$peak / median(lombResult$power[noiseBooleanVector])
  
  return(c(peakPeriodicity,SNR))
  
}


# Creates a scatter plot for minor-in, minor-out, and intermediate values, based on the given data and
# rotational positions.  The data should have a "position" column and the relevant counts should be in the second column.
# If an output file path is provided, writes the position data to that file.
inVsOutPlotter = function(positionData, minorInPositions, minorOutPositions, plotIntermediate = TRUE,
                          title = "", yAxisLabel = "Normalized Counts", xAxisLabel = "Rotational Position", ylim = NULL,
                          positionDataOutputFilePath = NULL) {
  
  # Characterize each position based on the given positions.
  positionData = copy(positionData)
  positionData = positionData[Position >= -73 & Position <= 73]
  positionData[,Rotational_Pos := "Intermediate"]
  positionData[Position %in% minorInPositions | Position %in% -minorInPositions, Rotational_Pos := "Minor_In"]
  positionData[Position %in% minorOutPositions | Position %in% -minorOutPositions, Rotational_Pos := "Minor_Out"]
  
  # Remove intermediate positions if they're not being plotted.
  if (!plotIntermediate) positionData = positionData[Rotational_Pos != "Intermediate"]
  
  # Write the data if an output file path was given.
  if (!is.null(positionDataOutputFilePath)) fwrite(positionData, positionDataOutputFilePath, sep = '\t')
  
  # Create the scatter plot!
  ggplot(positionData, aes_string("Rotational_Pos", paste0('`',colnames(positionData)[2],'`'), 
                                  color = "Rotational_Pos")) + 
    geom_jitter(width = 0.2, height = 0, shape = 1, size = 2) + 
    scale_color_manual(guide = NULL, values = c("Minor_In" = "forestgreen", "Minor_Out" = "Blue", 
                                                "Intermediate" = "Black")) +
    stat_summary(fun = median, geom = "crossbar", 
                 width = 0.5, fatten = 2, colour = "red") +
    labs(title = title, y = yAxisLabel, x = xAxisLabel) +
    coord_cartesian(ylim = ylim) +
    theme(plot.title = element_text(size = 20, hjust = 0.5), axis.title = element_text(size = 15),
          axis.text.y = element_text(size = 14))
  
}


# Separates out minor-in, minor-out, and intermediate positions, 
# and writes them and any data in column 2 to the given file path.
# NOTE: Currently doesn't work as expected...
separateRotationalPosData = function(positionData, minorInPositions, minorOutPositions, outputFilePath) {
  
  positionData = copy(positionData)
  positionData = positionData[Position >= -73 & Position <= 73]
  positionData[,Rotational_Pos := "Intermediate"]
  positionData[Position %in% minorInPositions | Position %in% -minorInPositions, Rotational_Pos := "Minor_In"]
  positionData[Position %in% minorOutPositions | Position %in% -minorOutPositions, Rotational_Pos := "Minor_Out"]
  
  minorInTable = data.table(Minor_In_Positions = positionData[Rotational_Pos == "Minor_In", Position],
                            Minor_In_Data = positionData[Rotational_Pos == "Minor_In"][[2]])
  minorOutTable = data.table(Minor_Out_Positions = positionData[Rotational_Pos == "Minor_Out", Position],
                             Minor_Out_Data = positionData[Rotational_Pos == "Minor_Out"][[2]])
  intermediateTable = data.table(Intermediate_Positions = positionData[Rotational_Pos == "Intermediate", Position],
                                 Intermediate_Data = positionData[Rotational_Pos == "Intermediate"][[2]])
  
  
}


# Performs a Chi-squared test for the given data, comparing minor-in and minor-out data
# to the expected counts in each region.  The counts data should be the second column, and the expected counts
# should be the third column
rotationalPosChiSquared = function(positionData, minorInPositions, minorOutPositions) {

  # Characterize each position based on the given positions.
  positionData = copy(positionData)
  positionData[,Rotational_Pos := "Intermediate"]
  positionData[Position %in% minorInPositions | Position %in% -minorInPositions, Rotational_Pos := "Minor_In"]
  positionData[Position %in% minorOutPositions | Position %in% -minorOutPositions, Rotational_Pos := "Minor_Out"]
  
  # Get the actual and expected counts for each rotational setting.
  actualCounts = c(sum(positionData[Rotational_Pos == "Minor_In",2]), 
                   sum(positionData[Rotational_Pos == "Minor_Out",2]))
  expectedCounts = c(sum(positionData[Rotational_Pos == "Minor_In",3]), 
                     sum(positionData[Rotational_Pos == "Minor_Out",3]))
 
  # Compute and return the chi-squared statistics
  return(chisq.test(actualCounts, p = expectedCounts, rescale.p = TRUE))
     
}

