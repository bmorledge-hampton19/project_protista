# Given a file and two integer values, n and m, randomly shuffles the file and 
# writes the first n and last m values 100 times.
# For now, output paths are hardcoded in.

inputFile=$1; shift
headSize=$1; shift
tailSize=$1; shift

tempShuffledFile="${inputFile%.*}_shuffled.${inputFile##*.}"

for i in {1..100}; do 
    shuf -o "$tempShuffledFile" "$inputFile"
    mkdir "MSS_size_subsets/ESAD-UK-28_MSS_size_subset_${i}"
    mkdir "MSI_size_subsets/ESAD-UK-28_MSI_size_subset_${i}"
    head -n $headSize "$tempShuffledFile" > \
        "MSS_size_subsets/ESAD-UK-28_MSS_size_subset_${i}/ESAD-UK-28_MSS_size_subset_${i}_custom_input.bed"
    tail -n $tailSize "$tempShuffledFile" > \
        "MSI_size_subsets/ESAD-UK-28_MSI_size_subset_${i}/ESAD-UK-28_MSI_size_subset_${i}_custom_input.bed"
done
