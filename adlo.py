from guessit import guessit
from pathlib import Path
from pathlib import PurePath
import platform
import argparse
import shutil
import re
import time
import progressbar

allowed_formats = ['avi', 'srt', 'mkv', 'mp4', 'mpg', 'mov', 'mpeg', 'flv', 'rm', 'mpg2', 'mpeg-ts', 'mts', 'ts', 'rtf']
unsorted = []
sorted_episodes = []
duplicates = []
failures = []


def main():
    parser = argparse.ArgumentParser(description='Organize a folder containing TV shows')
    parser.add_argument('dlFolder',
                       help='Path to download folder')
    parser.add_argument('destFolder',
                       help='Path to the directory you want your sorted files to be relocated')
    parser.add_argument('-l', metavar='--Log', dest='log',
                        help='Path to a location where you want to store unsorted items')
    parser.add_argument('-m', action='store_true',
                        help='If this flag is set Movies will also be sorted out of the given directory')
    parser.add_argument('--soft', action='store_false',
                        help='If soft argument is given, the script will run only once through the directory')
    args = parser.parse_args()

    download_folder = create_path(args.dlFolder)
    destination_folder = create_path(args.destFolder)


    if not download_folder.exists():
        exit("The given download directory does not exists")
    if not destination_folder.exists():
        create_folders_in_path(destination_folder)


    print("Please wait while we start the sorting process")
    bar = progressbar.ProgressBar(widgets=[
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        '  (', progressbar.ETA(), ') ',
    ])
    time.sleep(0.1)
    bar.update(2)
    unsorted = adlo(download_folder, destination_folder, args.m)
    if args.soft:
        totalTime = len(unsorted)
        newTime = 0
        while sorted_episodes:
            elapsedTime = int((1-(newTime/totalTime))*100)
            if elapsedTime >= 100 or elapsedTime < 0:
                elapsedTime = 10
            bar.update(elapsedTime)
            unsorted = adlo(download_folder, destination_folder, args.m)
            newTime = len(unsorted)
    bar.update(100)

    print_results()

    if args.log:
        logPath = create_path(args.log)
        for i in unsorted:
            logPath.write_text("\n".join([str(x) for x in (['\t--Unsorted--\n']+unsorted+
                                                           ['\n\t--Duplicates--\n']+duplicates+
                                                           ['\n\t--Failures--\n']+failures)]))


def adlo(download_folder, destination_folder, sort_movies):
    """ Main function for script."""

    clear_lists()

    # Create Movies and Episodes folder one folder up from working directory
    movies_folder = destination_folder / 'Movies'
    episodes_folder = destination_folder / 'Episodes'

    create_folders_in_path(movies_folder)
    create_folders_in_path(episodes_folder)

    # Get list for all files under working directory
    subfiles = [x for x in list(download_folder.glob('./*')) if x.is_file()]
    subfolders = [x for x in list(download_folder.glob('./*')) if x.is_dir()]


    for f in subfolders:
        if f not in failures and is_season(f):
            handle_episode(f, episodes_folder)
        else:
            unsorted.append(f)

    for f in subfiles:
        if f not in failures:
            process_single_file(f, episodes_folder)

    if sort_movies:
        handle_movies(movies_folder)
    clean_empty_folders(download_folder)

    return unsorted


def handle_movies(movies_folder):
    """ Sort movie."""
    # TODO: Cross reference IMDB for title/alternative_title
    # TODO: Return unprocessed paths (not found in IMDB)
    for item in unsorted:
        if item not in failures:
            info = guessit(fix_filename(item.name))
            if 'type' in info.keys() and info['type'].lower() == 'movie':
                if 'alternative_title' in info.keys():
                    target_folder = movies_folder / (info['title'].title() + info['alternative_title'].title())
                else:
                    target_folder = movies_folder / (info['title'].title())
                create_folders_in_path(target_folder)
                if item.is_dir():
                    clean_folder(item)
                    if not move_items_in_folder(item, target_folder):
                        duplicates.append(item)
                else:
                    if not move_item(item, target_folder):
                        duplicates.append(item)
                unsorted.remove(item)


def handle_episode(path, episodes_folder):
    """ Sort episode."""
    info = guessit(fix_filename(path.name))

    if foldername_has_single_season(path):
        single_season(path, episodes_folder)
    else:
        multiple_seasons(path, episodes_folder)


def process_single_file(f, episodes_folder):
    """ Sort a single file."""
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
    """ Sort folders that contain only one season."""
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
        duplicates.append(path)


def multiple_seasons(path, episodes_folder):
    """ Sort folders that contain multiple seasons."""
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
        duplicates.append(path)


def clean_folder(path):
    """ Recursively move through folders and delete files that are not allowed"""
    try:
        if path.is_dir():
            if re.search("[Ss][Cc][Rr][Ee][Ee][Nn]|[Ss][Aa][Mm][Pp][Ll][Ee]", path.name):
                if platform.system() == 'Windows':
                    shutil.rmtree("\\\\?\\" + str(path))
                else:
                    shutil.rmtree(str(path))
            else:
                for item in list(path.glob('./*')):
                    clean_folder(item)
        elif path not in failures:
            if not path.name.split('.')[-1].lower() in allowed_formats:
                path.unlink()
            elif re.search("[Ss][Cc][Rr][Ee][Ee][Nn]|[Ss][Aa][Mm][Pp][Ll][Ee]", path.name):
                path.unlink()
    except FileNotFoundError:
        if path in unsorted:
            unsorted.remove(path)
        if path not in failures:
            failures.append(path)


def clean_empty_folders(folder):
    """ Recursively remove empty folders."""
    try:
        directoryList = list(folder.glob('./*'))
        if not directoryList:
            shutil.rmtree(str(folder))
        else:
            for item in directoryList:
                if item.is_dir():
                    clean_empty_folders(item)
    except FileNotFoundError:
        if path in unsorted:
            unsorted.remove(path)
        if path not in failures:
            failures.append(path)


def move_items_in_folder(folder, target):
    """ Move every item in folder to target folder."""
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
    """ Move f item to target folder."""
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
    """ Regex check if folder/filename contains a single season."""
    if not re.search('\d+[ ]*-[ ]*\d+', path.name):
        info = guessit(fix_filename(path.name))
        if 'season' in info.keys():
            return True
    return False


def foldername_has_multiple_seasons(path):
    """ Regex check if folder/filename contains multiple seasons."""
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


def clear_lists():
    """ Clears all the lists."""
    sorted_episodes.clear()
    unsorted.clear()
    duplicates.clear()


def print_results():
    """ Print program results."""
    print("\n---------------------------------------------")
    print('sorted in last iteration:',len(sorted_episodes))
    print('unsorted:',len(unsorted))
    print('duplicates:',len(duplicates))
    print('failures:',len(failures))


if __name__ == "__main__":
    main()
