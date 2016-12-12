from guessit import guessit
from pathlib import Path
from pathlib import PurePath
import platform
import argparse
import shutil
import re
allowed_formats = ['avi', 'srt', 'mkv', 'mp4', 'mpg', 'mov', 'mpeg', 'flv', 'rm', 'mpg2', 'mpeg-ts', 'mts', 'ts', 'rtf']
unsorted = []
sorted_episodes = []


def main():
    parser = argparse.ArgumentParser(description='Organize a folder containing TV shows')
    parser.add_argument('dlFolder',
                       help='Path to download folder')
    parser.add_argument('destFolder',
                       help='Path to the directory you want your sorted files to be relocated')
    parser.add_argument('-l', metavar='--Log', dest='log',
                        help='Path to a location where you want to store unsorted items')
    args = parser.parse_args()

    download_folder = create_path(args.dlFolder)
    destination_folder = create_path(args.destFolder)

    if not download_folder.exists():
        exit("The given download directory does not exists")
    if not destination_folder.exists():
        create_folders_in_path(destination_folder)

    unsorted = adlo(download_folder, destination_folder)
    if args.log:
        logPath = create_path(args.log)
        for i in unsorted:
            logPath.write_text("\n".join([str(x) for x in unsorted]))


def adlo(download_folder, destination_folder):

    guessit_keys = ['type', 'title', 'season', 'episode', 'episode_title']


    # Create Movies and Episodes folder one folder up from working directory
    movies_folder = destination_folder / 'Movies'
    episodes_folder = destination_folder / 'Episodes'

    create_folders_in_path(movies_folder)
    create_folders_in_path(episodes_folder)

    # Get list for all files under working directory
    subfiles = [x for x in list(download_folder.glob('./*')) if x.is_file()]
    subfolders = [x for x in list(download_folder.glob('./*')) if x.is_dir()]


    for f in subfolders:
        if is_season(f):
            handle_episode(f, episodes_folder)
        else:
            unsorted.append(f)

    for f in subfiles:
        process_single_file(f, episodes_folder)

    print('sorted',len(sorted_episodes))
    print('unsorted',len(unsorted))
    clean_empty_folders(download_folder)

    return unsorted


def handle_movie(info):
    """ Sort movie."""
    # TODO: Cross reference IMDB for title/alternative_title
    # TODO: Return unprocessed paths (not found in IMDB)
"""
    if 'container' in info.keys() and info['container'].lower() in allowed_formats:
        if 'title' in info.keys() and 'alternative_title' in info.keys():
            copy_file(f, movies_folder / (info['title'] + " " + info['alternative_title']))
        elif 'title' in info.keys():
            copy_file(f, movies_folder / info['title'])
        else:
            print("don't know what the title is!")
            #copy_file(f, movies_folder / f.parent.parts[-1])"""


def handle_episode(path, episodes_folder):
    """ Sort episode."""
    info = guessit(fix_filename(path.name))

    if foldername_has_single_season(path):
        single_season(path, episodes_folder)
    else:
        multiple_seasons(path, episodes_folder)


def process_single_file(f, episodes_folder):
    info = guessit(fix_filename(f.name))
    if 'title' in info.keys() and 'season' in info.keys():
        target_folder = episodes_folder / (info['title'].title() + "/Season " + str(info['season']))
    elif 'title' in info.keys():
        target_folder = episodes_folder / (info['title'].title())
    else:
        unsorted.append(f)
        return
    create_folders_in_path(target_folder)
    if move_item(f, target_folder):
        sorted_episodes.append(f)
    else:
        unsorted.append(f)


def single_season(path, episodes_folder):
    clean_folder(path)
    info = guessit(fix_filename(path.name))
    # create Title folder and Season folder
    #print(str(path))
    if 'title' in info.keys():
        target_folder = episodes_folder / (info['title'].title() + "/Season " + str(info['season']))
    else:
        unsorted.append(path)
        return
        # TODO: read filenames for title/season

    create_folders_in_path(target_folder)
    if move_items_in_folder(path, target_folder):
        sorted_episodes.append(path)
    else:
        unsorted.append(path)


def clean_folder(path):
    """ Recursively move through folders and delete files that are not allowed"""

    if path.is_dir():
        if re.search("[Ss][Cc][Rr][Ee][Ee][Nn]|[Ss][Aa][Mm][Pp][Ll][Ee]", path.name):
            if platform.system() == 'Windows':
                shutil.rmtree("\\\\?\\" + str(path))
            else:
                shutil.rmtree(str(path))
        else:
            for item in list(path.glob('./*')):
                clean_folder(item)
    else:
        if not path.name.split('.')[-1].lower() in allowed_formats:
            path.unlink()
        elif re.search("[Ss][Cc][Rr][Ee][Ee][Nn]|[Ss][Aa][Mm][Pp][Ll][Ee]", path.name):
            path.unlink()


def clean_empty_folders(folder):
    directoryList = list(folder.glob('./*'))
    if not directoryList:
        shutil.rmtree(str(folder))
    else:
        for item in directoryList:
            if item.is_dir():
                clean_empty_folders(item)


def multiple_seasons(path, episodes_folder):
    clean_folder(path)
    info = guessit(fix_filename(path.name))
    # create Title folder and Season folder
    if 'title' in info.keys():
        target_folder = episodes_folder / (info['title'].title())
    else:
        unsorted.append(path)
        return

    create_folders_in_path(target_folder)
    if move_items_in_folder(path, target_folder):
        sorted_episodes.append(path)
    else:
        unsorted.append(path)


def move_items_in_folder(folder, target):
    for item in list(folder.glob('./*')):
        if not (target / item.name).exists():
            if platform.system() == 'Windows':
                shutil.move("\\\\?\\" + str(item), str(target))
            else:
                shutil.move(str(item), str(target))
            return True
        else:
            # Garbage
            return False


def move_item(f, target):
    if not (target / f.name).exists():
        if platform.system() == 'Windows':
            shutil.move("\\\\?\\" + str(f), str(target))
        else:
            shutil.move(str(f), str(target))
        return True
    else:
        # Garbage
        return False


def is_season(path):
    """ Recursively check if any file or folder contains info about season."""
    if re.search('[Ss]eason|[Ss][ ]*\d+[ ]*[Ee][ ]*\d+', path.name):
        return True
    elif path.is_dir():
        for child in list(path.iterdir()):
            if is_season(child):
                return True
    return False


def foldername_has_single_season(path):
    if not re.search('\d+[ ]*-[ ]*\d+', path.name):
        info = guessit(fix_filename(path.name))
        if 'season' in info.keys():
            return True
    return False


def foldername_has_multiple_seasons(path):
    if re.search('\d+[ ]*-[ ]*\d+', path.name):
        info = guessit(fix_filename(path.name))
        if 'season' in info.keys():
            return True
    return False


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
