# This script takes a directory and blinds all the files in it by copying and renaming them while retaining a key.
import os, shutil, random

def blindFiles(directory: str, expectedFileEnding = ".TIF"):

    filePathsToBlind = list()

    # Make sure the necessary directories exist.
    blindedDirectory = os.path.join(directory, "_blinded")
    if not os.path.exists(blindedDirectory): os.mkdir(blindedDirectory)
    blindedKeyDirectory = os.path.join(blindedDirectory, "_key")
    if not os.path.exists(blindedKeyDirectory): os.mkdir(blindedKeyDirectory)

    # Create the path the key file.
    blindedKeyFilePath = os.path.join(blindedKeyDirectory, "key.tsv")

    # Find files to blind.
    for dirPath, _, fileNames in os.walk(directory):

        isolatedDirName = dirPath.rsplit(os.sep, 1)[1]
        if isolatedDirName == "_blinded" or isolatedDirName == "_key": continue

        for fileName in fileNames:

            if not fileName.endswith(expectedFileEnding):
                print(f"Uh-oh! Found file with unexpected ending: {os.path.join(dirPath,fileName)}")
            
            else:
                filePathsToBlind.append(os.path.join(dirPath, fileName))

    # Randomly assign an ID to each file.
    randomIDs = list(range(1,len(filePathsToBlind) + 1))
    random.shuffle(randomIDs)
    filePathToBlindID = dict()
    for filePathToBlind, randomID in zip(filePathsToBlind, randomIDs):
        filePathToBlindID[filePathToBlind] = randomID
        
    # Copy the file paths to blind to the blinded directory, renaming based on their random ID.
    for filePathToBlind in filePathToBlindID:
        blindFilePath = os.path.join(blindedDirectory, str(filePathToBlindID[filePathToBlind]) + expectedFileEnding)
        shutil.copyfile(filePathToBlind, blindFilePath)

    # Create the key for the blinded files.
    with open(blindedKeyFilePath, 'w') as blindedKeyFile:
        for filePathToBlind in filePathToBlindID:
            blindedKeyFile.write(filePathToBlind + '\t' + str(filePathToBlindID[filePathToBlind]) + '\n')
