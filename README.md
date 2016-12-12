adlo
=======

adlo (Amazing Download Organizer) is a script that helps you sort your episodes and movies in your download folder.


Get started
-------

To use this script you will have to install the guessit module and the progressbar2 module which can be done in the following way:

    $ pip install guessit
    $ pip install progressbar2

Usage
-------

adlo can be used from the command line:

    $ python3 adlo.py -h
    usage: adlo.py [-h] [-l --Log] [-m] dlFolder destFolder

    Organize a folder containing TV shows

    positional arguments:
      dlFolder    Path to download folder
      destFolder  Path to the directory you want your sorted files to be relocated

    optional arguments:
      -h, --help  show this help message and exit
      -l --Log    Path to a location where you want to store unsorted items
      -m          If this flag is set Movies will also be sorted out of the given
                  directory

Running the script without any flags will only sort the episodes in your download folder, adding the -m flag will also sort movies.

Example Usage
-------

You can use relative and absolute paths when running the script. Running the script withouth

    $ python3 adlo.py 'downloads' '/home/user/path_to_folder'
    sorted: 590
    unsorted: 40
    duplicates: 11

Known Issues
-------

Windows users might not be able able sort files where the length of the path is more than 255 characters long. The script will output those paths if that happens.
