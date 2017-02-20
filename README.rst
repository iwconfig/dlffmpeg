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

Quick run!
----------
In a hurry or feeling lazy? Run one of these oneliners to download and execute the latest binary release. No python needed.

| Linux and OS X:

::

    # Using cURL
    curl https://git.io/vDdvo | sudo bash

    # Using wget (not installed by default on OSX)
    wget -O - https://git.io/vDdvo | sudo bash

| Windows:

At the moment windows users are stuck with downloading and running `the latest binary file <https://github.com/iwconfig/dlffmpeg/releases/download/v0.6.3/dlffmpeg-0.6.3-windows-64bit.exe>`_ manually (as admin). But not for long!

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

| ``getFFmpeg()`` contains all options, e.g.:

::

    from dlffmpeg import getFFmpeg
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
- Use logging module instead
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