#A script that reads in fruits and determines how many high maintenence fruits are included.

library(data.table)
dir.create("Results")

fruits = fread("Fruits.csv")
HMFruits = fread("HMFruits.csv")

HMFruitsPresent = intersect(HMFruits[,Fruits],fruits[,Fruits])

print(paste0(length(HMFruitsPresent), " high maintenece fruits are present in your list of ", length(fruits[,Fruits]), " fruits."))
print("Those fruits are:")
print(HMFruitsPresent)

save(HMFruitsPresent,file = "Results/HMFruits.rda")
