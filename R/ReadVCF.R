library(vcfR)

vcf_file = choose.files()
vcf <- read.vcfR( vcf_file, verbose = FALSE )
