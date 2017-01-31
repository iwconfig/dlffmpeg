# dlffmpeg.py #

Simple python module/standalone script to download and install the latest (static binary) release of FFmpeg from different sources. You can find the links to these sources on the official homepage of FFmpeg.

Supported systems are Linux, OS X and Windows.
Currently armv7 and armv8 architectures are only available for Linux systems.


System (architecture)             | Source
----------------------------------|-------------------------------------------------------
Linux   (64-/32bit, armv7, armv8) | https://johnvansickle.com/ffmpeg
OS X    (64-/32bit, PPC)          | http://evermeet.cx/ffmpeg and http://www.ffmpegmac.net
Windows (64-/32bit)               | https://ffmpeg.zeranoe.com



`dlffmpeg._run()` installs into default path if no argument, else string as path.


`getFFmpeg()` contains all options, e.g.:

    dl = getFFmpeg()
    dl.path = '/path/to/dir'
    dl.silent = True
    dl.pretty = True
    dl.verbose = False

Execute with `dl.run()`

Standalone takes one argument for custom path or no argument for default.