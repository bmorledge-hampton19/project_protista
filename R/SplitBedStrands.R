library(data.table)

bedFilePath = choose.files()
dataGroupName = strsplit(basename(bedFilePath),'.', fixed = TRUE)[[1]][1]

fullBedTable = fread(file = bedFilePath)

plusBedTable = fullBedTable[V6 == '+', c(1:3)]
plusBedTable[, c("Name") := 0]
plusBedTable[, c("Score") := 0]

minusBedTable = fullBedTable[V6 == '-', c(1:3)]
minusBedTable[, c("Name") := 0]
minusBedTable[, c("Score") := 0]

fwrite(plusBedTable, file = file.path(dirname(bedFilePath), paste0(dataGroupName,"_plus.bed")), 
       sep = '\t', col.names = F)
fwrite(minusBedTable, file = file.path(dirname(bedFilePath), paste0(dataGroupName,"_minus.bed")), 
       sep = '\t', col.names = F)