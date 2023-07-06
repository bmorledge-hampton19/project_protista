#!/bin/bash
# A bash script using awk to stratify and format genes in melanocytes.
# Genes are stratified by high and low expression and formatted as bed entries.
awk '$12 == "High" && $14 == "High" { printf "chr"$3"\t"$4"\t"$5"\t.\t.\t"; if($6 == 1){print "+"} else{print "-"} }' \
    keratinocyte_melanocyte_expression_roadmap_Gencodev10_hg19.txt > high_expressed_melanocyte_genes.bed
sort -k1,1 -k2,2n -k3,3n high_expressed_melanocyte_genes.bed -s -o high_expressed_melanocyte_genes.bed

awk '$12 == "Low" && $14 == "Low" { printf "chr"$3"\t"$4"\t"$5"\t.\t.\t"; if($6 == 1){print "+"} else{print "-"} }' \
    keratinocyte_melanocyte_expression_roadmap_Gencodev10_hg19.txt > low_expressed_melanocyte_genes.bed
sort -k1,1 -k2,2n -k3,3n low_expressed_melanocyte_genes.bed -s -o low_expressed_melanocyte_genes.bed

awk '{ printf "chr"$3"\t"$4"\t"$5"\t.\t.\t"; if($6 == 1){print "+"} else{print "-"} }' \
    keratinocyte_melanocyte_expression_roadmap_Gencodev10_hg19.txt > hg19_genic_regions.bed
sort -k1,1 -k2,2n -k3,3n hg19_genic_regions.bed -s -o hg19_genic_regions.bed