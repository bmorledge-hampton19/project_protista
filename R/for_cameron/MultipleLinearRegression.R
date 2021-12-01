library(data.table)

mutationData = fread(choose.files(multi = FALSE))

xDataNames = colnames(mutationData[,-c("context", "frequency")])

fit = lm(frequency ~. - context - frequency - fivePrimeC - threePrimeC, mutationData)
summary = summary(fit)

print(summary)

