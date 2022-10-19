# This script serves as an interface for moving projects into their
# own directory and then packaging and pushing the contents to launchpad.
# (For some reason, debuild has trouble working in Windows drives.)
import os, shutil, subprocess
from benbiohelpers.TkWrappers.TkinterDialog import TkinterDialog
from benbiohelpers.FileSystemHandling.DirectoryHandling import checkDirs
from benbiohelpers.CustomErrors import InvalidPathError


# This function prepares a directory for packaging, then passes it to the packaging bash script.
def packagingPipeline(projectDirectory, keyID, launchpadAddress, overwrite = False):

    # Get the packaging directory and make sure it exists.
    packagingDirectory = os.path.join(os.getenv("HOME"), "packaging")
    checkDirs(packagingDirectory)

    # Find the changelog file and create a name for the build with the format [package name]_[version]
    changelogFilePath = os.path.join(projectDirectory, "debian", "changelog")
    if not os.path.exists(changelogFilePath):
        raise InvalidPathError(changelogFilePath, "Expected changelog file at the following path, but it does not exist")
    with open(changelogFilePath, 'r') as changelogFile:
        projectName, versionUntrimmed = changelogFile.readline().split(" (", 1)
        version = versionUntrimmed.split(") ", 1)[0]

    # Create the project-specific packaging directory path.
    projectPackagingDir = os.path.join(packagingDirectory, '_'.join((projectName,version)))

    # Copy the contents of the project directory into the project packaging directory.
    print("\nCreating project packaging directory...")
    try:
        shutil.copytree(projectDirectory, projectPackagingDir, dirs_exist_ok=overwrite)
    except FileExistsError:
        print("Project packagining directory already exists and will not be overwritten. Aborting.")
        quit()

    # Call the packaging command as a subprocess.
    print("\nBuilding package...")
    subprocess.check_call(("debuild", "-k"+keyID, "-S"), cwd = projectPackagingDir)

    # Recreate the name for the source.changes file that was just made.
    sourceChangesFilePath = os.path.join(packagingDirectory, os.path.basename(projectPackagingDir)+"_source.changes")

    # Push the changes to the ppa.
    print("\nPushing package to ppa...")
    subprocess.check_call(("dput", "ppa:"+launchpadAddress, sourceChangesFilePath))


def main():

    # Create a simple dialog for selecting the relevant files.
    with TkinterDialog(workingDirectory=os.path.abspath(os.path.join(__file__,"..","..",".."))) as dialog:

        dialog.createFileSelector("Project Directory (containing debian directory):", 0,
                                  directory = True)
        dialog.createTextField("Key ID:", 1, 0, defaultText = "b.morledge-hampton@wsu.edu", width = 40)
        dialog.createTextField("PPA Address:", 2, 0, defaultText = "ben-morledge-hampton/mutperiod", width = 40)
        dialog.createCheckbox("Overwrite existing packaging files", 3, 0, 2)
        
    packagingPipeline(dialog.selections.getIndividualFilePaths()[0], dialog.selections.getTextEntries()[0],
                      dialog.selections.getTextEntries()[1], dialog.selections.getToggleStates()[0])


if __name__ == "__main__": main()
