dlffmpeg
========

| Simple python module/standalone script to download and install the latest (static binary) release of FFmpeg from different sources. You can find the links to these sources on the official homepage of FFmpeg.
| 
| Supported systems are Linux, OS X and Windows. Currently armv7 and armv8 architectures are only available for Linux systems.
| 

+-----------------------------------+----------------------------------------------------------+
| System (architecture)             | Source                                                   |
+===================================+==========================================================+
| Linux (64-/32bit, armv7, armv8)   | https://johnvansickle.com/ffmpeg                         |
+-----------------------------------+----------------------------------------------------------+
| OS X (64-/32bit, PPC)             | http://evermeet.cx/ffmpeg and http://www.ffmpegmac.net   |
+-----------------------------------+----------------------------------------------------------+
| Windows (64-/32bit)               | https://ffmpeg.zeranoe.com                               |
+-----------------------------------+----------------------------------------------------------+

Installation
------------

Using pip: ``sudo pip install -U dlffmpeg``

or pip with git:
``sudo pip install git+https://github.com/iwconfig/dlffmpeg.git``

| From source code:

::

    git clone https://github.com/iwconfig/dlffmpeg.git
    cd dlffmpeg
    sudo python setup.py install

Usage
-----

``dlffmpeg._run()`` installs into default path if no argument, else
string as path.

``getFFmpeg()`` contains all options, e.g.:

::

    dl = getFFmpeg()
    dl.path = '/path/to/dir'
    dl.silent = True
    dl.pretty = True
    dl.verbose = False

Execute with ``dl.run()``

| Standalone takes one argument for custom path or no argument for default.

::

    ~/ $ dlffmpeg --help
    usage: dlffmpeg.py [-h] [-s] [-lv] [-p] [--version] [path]

    specify installation path. no path equals to default path.

    positional arguments:
      path

    optional arguments:
      -h, --help           show this help message and exit
      -s, --silent
      -lv, --less-verbose
      -p, --pretty
      --version            show program's version number and exit

--------------

Todo
~~~~
- Ability to compile and install from source, cross-platform
- Better module support

Contribute
''''''''''
I am certain my code needs better perspective and from what this script
represent i'm currently not capable of comprehending better principles.
Please feel free to fork and improve. :)

License
*******
This project is licensed under the terms of `the MIT
license <https://github.com/iwconfig/dlffmpeg/blob/master/LICENSE>`_.