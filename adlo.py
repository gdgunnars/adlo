from guessit import guessit
from pathlib import Path
import shutil


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


def copy_file(file, target_path):
    """ Create target_path if it doesn't exist and copy file to target_path."""
    if not target_path.exists():
        create_folders_in_path(target_path)
    shutil.copy(str(from_path), str(target_path))


def create_folders_in_path(path):
    """ Recursively create folders in path if they don't exist."""
    if not path.exists():
        create_folders_in_path(path.parent)
        path.mkdir()
    return
