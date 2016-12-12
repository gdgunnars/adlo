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
    usage: adlo.py [-h] [-l --Log] [-m] [--soft] dlFolder destFolder

    Organize a folder containing TV shows

    positional arguments:
      dlFolder    Path to download folder
      destFolder  Path to the directory you want your sorted files to be relocated

    optional arguments:
      -h, --help  show this help message and exit
      -l --Log    Path to a location where you want to store unsorted items
      -m          If this flag is set Movies will also be sorted out of the given
                  directory
      --soft      If soft argument is given, the script will run only once through
                  the directory

Running the script without any flags will only sort the episodes in your download folder until it can't find anything more to sort. Adding the -l flag with a file location will output log info into that file, the file will be created if it doesn't already exist. Adding the -m flag will also sort movies. Adding the --soft flag will only run one iteration of the sort (it will most likely not finish sorting everything).

Example Usage
-------

You can use relative and absolute paths when running the script.

Running the script without any flags:

    $ python3 adlo.py downloads /home/user/path_to_folder
    Please wait while we start the sorting process
    [Elapsed Time: 0:00:33] |#########################################################################|  (ETA:  0:00:00)
    ---------------------------------------------
    sorted in last iteration: 0
    unsorted: 79
    duplicates: 4

Running the script with flags:

    $ python3 adlo.py downloads /home/user/path_to_folder -m -l log
    Please wait while we start the sorting process
    [Elapsed Time: 0:00:34] |#########################################################################|  (ETA:  0:00:00)
    ---------------------------------------------
    sorted in last iteration: 0
    unsorted: 5
    duplicates: 4

Known Issues
-------

Windows users might not be able able to sort files where the length of the path is more than 255 characters long. The script will output those paths to the log file (if specified) if that happens.
