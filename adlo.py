from guessit import guessit
from pathlib import Path
from pathlib import PurePath
import argparse
import shutil
import re


def main():
    parser = argparse.ArgumentParser(description='Organize a folder containing TV shows')
    parser.add_argument('dlFolder',
                       help='Path to download folder')
    parser.add_argument('destFolder',
                       help='Path to the directory you want your sorted files to be relocated')
    args = parser.parse_args()

    download_folder = create_path(args.dlFolder)
    destination_folder = create_path(args.destFolder)

    if not download_folder.exists():
        exit("The given download directory does not exists")
    if not destination_folder.exists():
        create_folders_in_path(destination_folder)

    adlo(download_folder, destination_folder)


def adlo(download_folder, destination_folder):

    guessit_keys = ['type', 'title', 'season', 'episode', 'episode_title']
    allowed_formats = ['avi', 'srt', 'mkv', 'mp4', 'mpg', 'mov', 'mpeg', 'flv']

    # Create Movies and Episodes folder one folder up from working directory
    movies_folder = destination_folder / 'Movies'
    episodes_folder = destination_folder / 'Episodes'

    create_folders_in_path(movies_folder)
    create_folders_in_path(episodes_folder)

    # Get list for all files under working directory
    all_files = [x for x in list(download_folder.glob('**/*')) if x.is_file()]

    for f in all_files:
        info = guessit(fix_filename(f.name))
        if 'type' in info.keys():
            if info['type'].lower() == 'movie':
                handle_movie(info)
            elif info['type'].lower() == 'episode':
                handle_episode(info)


def handle_movie(info):
    """ Sort movie."""
    # TODO: Cross reference IMDB for title/alternative_title
    # TODO: Return unprocessed paths (not found in IMDB)

    if 'container' in info.keys() and info['container'].lower() in allowed_formats:
        if 'title' in info.keys() and 'alternative_title' in info.keys():
            copy_file(f, movies_folder / (info['title'] + " " + info['alternative_title']))
        elif 'title' in info.keys():
            copy_file(f, movies_folder / info['title'])
        else:
            print("don't know what the title is!")
            #copy_file(f, movies_folder / f.parent.parts[-1])


def handle_episode(info):
    """ Sort episode."""
    # do stuff


def fix_filename(fname):
    """ Return filename that can be read by guessit."""
    return re.sub('\(|\)|\[|\]|{|}',  '', fname)


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
    """ Returns correct Path object regardless of absolute or relative path."""
        if PurePath(path).is_absolute():
            return Path(path)
        else:
            return Path().resolve() / path

if __name__ == "__main__":
    main()
