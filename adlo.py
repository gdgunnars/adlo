from guessit import guessit
from pathlib import Path
from pathlib import PurePath
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description='Organize a folder containing TV shows')
    parser.add_argument('dlFolder',
                       help='Path to download folder')
    parser.add_argument('destFolder',
                       help='Path to the directory you want your sorted files to be relocated')
    args = parser.parse_args()

    oldDir = create_path(args.dlFolder)
    newDir = create_path(args.destFolder)

    if not oldDir.exists():
        exit("The given download directory does not exists")
    if not newDir.exists():
        create_folders_in_path(newDir)

def adlo():

    guessit_keys = ['title', 'season', 'episode', 'episode_title', 'type']

    # Path is hardcoded to begin with
    working_dir = Path().resolve() / 'downloads'
    print(working_dir)

    # Create Movies and Episodes folder one folder up from working directory
    create_folders_in_path(working_dir / '../Movies')
    create_folders_in_path(working_dir / '../Episodes')

    # Get list for all files under working directory
    all_files = [x for x in list(working_dir.glob('**/*')) if x.is_file()]

    #print(len(all_files))
    # Testing function:
    #create_folders_in_path(working_dir / '../Episodes/South Park/Season 4')
"""
    for file in all_files:
        info = guessit(file.name)
        if 'title' in info.keys():
            print(info['title'])
        else:
            print('NO TITLE, MOVE ALONG NOTHING TO SEE HERE')"""


def copy_file(f, target_path):
    """ Create target_path if it doesn't exist and copy file to target_path."""
    if not target_path.exists():
        create_folders_in_path(target_path)
    shutil.copy(str(f), str(target_path))


def create_folders_in_path(path):
    """ Recursively create folders in path if they don't exist."""
    if not path.exists():
        create_folders_in_path(path.parent)
        path.mkdir()
    return

def create_path(path):
        if PurePath(path).is_absolute():
            return Path(path)
        else:
            return Path().resolve() / path

if __name__ == "__main__":
    main()
