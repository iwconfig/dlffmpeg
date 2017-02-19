#!/usr/bin/env python
from __future__ import print_function
import os, platform
from codecs import open
from tempfile import gettempdir
from sys import stdout, argv, exit, version_info
from subprocess import check_output, call

try:
    from requests import get, Timeout, ConnectionError
    import cursor, atexit
except ImportError:
    pass

system = platform.system().lower()
if not 'linux' in system:
    from zipfile import ZipFile, is_zipfile
    from re import search
    from shutil import copy2
if 'windows' in system:
    try:
        import winreg
    except ImportError:
        import _winreg as winreg
    import win32gui
    import win32con
    try:
        sub_key = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_key, 0, winreg.KEY_ALL_ACCESS) 
    except WindowsError:
        from msvcrt import getch
        print('You need to have admin privileges to register the environment variable.')
        print('Press "enter" to cancel or "space" to continue installation without it. (default: enter)')
        while True:
            choice = getch().lower()
            if choice == b'\r':
                exit()
            elif choice == b' ':
                key = None
                break
            else:
               print("Please press 'enter' or 'space'")

__info__ = """
This module, which also functions as a standalone script, downloads
the latest (static binary) release of FFmpeg from different sources.
These sites are all linked to by the official homepage of FFmpeg.

Supported systems are Linux, OS X and Windows.
Currently armv7 and armv8 architectures are only available for Linux systems.

Sources:
    System (architecture):
        - Linux   (64-/32bit, armv7, armv8)      : https://johnvansickle.com/ffmpeg
        - OS X    (64-/32bit, PPC)               : http://evermeet.cx/ffmpeg
                                                   http://www.ffmpegmac.net
        - Windows (64-/32bit)                    : https://ffmpeg.zeranoe.com


dlffmpeg._run() installs into default path if no argument, else string as path.

getFFmpeg() contains all options, e.g.:
    dl = getFFmpeg()
    dl.path = '/path/to/dir'
    dl.silent = True
    dl.pretty = True
    dl.verbose = False
Execute with dl.run()

Standalone: takes one argument for custom path or no argument for default.
"""
__version__ = '0.6.3'

def info():
    return __info__

def args():
    from argparse import ArgumentParser
    p = ArgumentParser(description='specify installation path. no path equals to default path.')
    p.add_argument('path', nargs='?', const=None)
    p.add_argument('-s', '--silent', action='store_true', dest='silent')
    p.add_argument('-lv', '--less-verbose', action='store_false', dest='verbose')
    p.add_argument('-p', '--pretty', action='store_true', dest='pretty')
    p.add_argument('--version', action='version',
                    version='{}'.format(__version__))
    return p.parse_args()

def arch():
    arches = {'64bit':   ['x86_64','x86-64','amd64', 'x64', '64'],
          '32bit':   ['x86', 'x32', '32', 'i686', 'i386'],
          'armel' :   ['armv4tl', 'armv5l', 'armv6l'],
          'armhf' :   ['armv7l', 'armv8l']}

    for k, v in arches.iteritems() if version_info[0] == 2 else arches.items():
        if [x for x in v if x == platform.machine().lower()]:
            return k

def _run(topath = None, silent = False, pretty=False, verbose=True, arch=arch(), tmp=gettempdir()+os.sep):
    cursor.hide()
    atexit.register(cursor.show)

    def info(k, v = None, beforeString = 0, afterString = 0, indent = True, verbose=True): ## this is a mess
        if silent:
            return
        if not verbose:
            t = ''
        if pretty:
            if any(x in k for x in ['temp', 'downloading', 'install path']):
                t = '\t'
            else:
                t = '\t\t'
        else:
            indent = False
            t = ''
            k += ' '

        if k and v == None:
            k = '{}'.format(k)

        if v:
            if '{}' in k:
                k = k.format(v)
            else:
                k = k+t+v
        stdout.write('{}{}{}{}'.format('\n'*beforeString, '\t'*indent, k, '\n'*afterString))
        stdout.flush()

    def check_permission(x): ### fixa detta
        if not os.access(x, os.W_OK):
            info('-'*60, beforeString=1, afterString=1)
            if os.path.isfile(x):
                info("'{}' already exist but \nyou need root privilege.".format(x))
            else:
                info("you need write permission to '{}'.".format(x))
            info('run as root.', beforeString=2, afterString=1)
            info('-'*60, afterString=1)
            exit(1)
            
    def which(program):
        if 'windows' in system:
            program = "{0}.exe".format(program)
            
        for path in os.environ["PATH"].split(os.pathsep):
            if os.path.exists(os.path.join(path, program)):
                    return os.path.join(path, program)
        return None

    def path(path = None):
        if path == None:
            ffmpeg = which('ffmpeg')
            if ffmpeg:
                path = os.path.dirname(ffmpeg) if not 'windows' in system else os.path.dirname(ffmpeg).rsplit(os.sep, 2)[0]
            else:
                if 'linux' in system:
                    path = '/usr/local/bin'
                if 'darwin' in system:
                    path = '/usr/local/bin'
                if 'windows' in system:
                    path = 'C:\\Program Files'
        else:
            if os.path.isfile(path) and not path.endswith('ffmpeg'):
                path = os.path.dirname(path)
            if not path.endswith(os.sep):
                path += os.sep
            if 'windows' in system:
                path += 'ffmpeg' + os.sep
            if not os.path.exists(path):
                os.makedirs(path)
                
        if os.path.isdir(path):
            check_permission(path)
        return path

    def check_md5(file_name, md5_file):
        if os.path.isfile(md5_file) == False or os.path.isfile(file_name) == False:
            return False
        else:
            from hashlib import md5
            if verbose:
                info('checksum:', beforeString=1)
            with open(md5_file, encoding='ascii') as md5_to_verify:
                original_md5 = md5_to_verify.read().split(' ')[0]
            with open(file_name, 'rb') as file_to_check:
                data = file_to_check.read()
                md5_returned = md5(data).hexdigest()
            if original_md5 == md5_returned:
                if verbose:
                    info('verified')
                else:
                    info('checksum verified', afterString=1, verbose=False)
                return True
            else:
                if verbose:
                    info('invalid! lets download again shall we', afterString=1)
                else:
                    info('checksum invalid, trying again', afterString=1, verbose=False)
                return False
    
    def dl(url, file, tmp):
        if verbose:
            info('downloading:', file, beforeString=1)
        else:
            if file.endswith('.md5'):
                info('downloading md5 sum',afterString=1, verbose=False)
            info('downloading ffmpeg',afterString=1, verbose=False)
        if os.path.exists(tmp):
            check_permission(tmp)
        while True:
            for x in range(5):
                r = get(url + file)
                if r.status_code != 200:
                    from time import sleep
                    if verbose:
                        info('error:', 'something wrong with connection, retry #{}/5'.format(x+1), beforeString=1)
                    else:
                        info("connection error. retry #{}/5".format(x+1), afterString=1, verbose=False)
                    sleep(2)
                    if x == 4:
                        info('bad connection, sorry. try again later or check if the url below is correct and if not you can report it', beforeString=2, afterString=1, verbose=False, indent=False)
                        exit(1)
                    continue
    
                if r.status_code == 200:
                    break
            break

        with open(tmp, 'wb') as f:
            if tmp.endswith('.md5'):
                f.write(r.content)
            else:
                for chunk in r.iter_content():
                    f.write(chunk)
    
    def install(path):
        try:
            if os.path.exists(os.path.join(path, 'ffmpeg')):
                if verbose:
                    info('old ffmpeg:', beforeString=2)
                    
                for p, d, f in os.walk(path, topdown=False):
                    if system in ('linux', 'darwin'):
                
                        if 'darwin' in system and arch == '64bit':
                            exelist = ['ffmpeg']
                        else:
                            exelist = ['ffmpeg', 'ffprobe', 'ffserver']
                        if 'linux' in system:
                            exelist.append('ffmpeg-10bit')
                            
                        for n in exelist:
                            try:
                                os.remove(os.path.join(p, n))
                            except: pass
                    else:
                        for n in f:
                            os.remove(os.path.join(p, n))
                        for n in d:
                            os.rmdir(os.path.join(p, n))
                if verbose:
                    info('removed')
        except:
            info('something went wrong', beforeString=3, afterString=2) 
            import traceback
            print('-'*60)
            traceback.print_exc(file=stdout)
            print('-'*60)
        else:
            try:
                if verbose:
                    info('install path:', '{}{}'.format(path, ' (default)' if not topath else ''), beforeString=1)
                    info('installing:', beforeString=1)
                if 'linux' in system:
                    check_output(['tar', '-tf', tmp]).splitlines()[0]
                    call(['tar', '-xJf', tmp, '--strip-components=1', '--overwrite', '-C', path, '--wildcards', '*/ffmpeg', '*/ffmpeg-10bit', '*/ffprobe', '*/ffserver'])
                if 'darwin' in system:
                    if arch == '64bit':
                        from glob import glob
                        call(['hdiutil', 'attach', tmp], stdout=open(os.devnull, 'wb'))
                        file = glob(r'/Volumes/FFmpeg*/ffmpeg')[0]
                        copy2(file, path)
                        call(['hdiutil', 'unmount', os.path.dirname(file)], stdout=open(os.devnull, 'wb'))
                    if arch == '32bit' or platform.mac_ver()[0].rsplit('.', 1)[0] in ('10.5', '10.6'):
                        zf = ZipFile(tmp, 'r')
                        zf.extractall(path)
                        zf.close()
                if 'windows' in system:
                    path = os.path.join(path, 'ffmpeg')
                    zf = ZipFile(tmp, 'r')
                    for i in zf.namelist():
                        if i == zf.namelist()[0]:
                            continue
                        f = i.split('/')
                        f.pop(0)
                        d = os.path.join(path, os.sep.join(f[0:-1]))
                        if not os.path.exists(d):
                            os.makedirs(d)
                            continue
                        data = zf.read(i)
                        file = os.sep.join([d, f[-1]])
                        f = open(file,'wb+')
                        f.write(data)
                        f.close()
                    zf.close()
                    
                    if key:
                        try:
                            value, _ = winreg.QueryValueEx(key, 'PATH')
                        except WindowsError:
                            value = ''
                        v = os.path.join(path, 'bin')
                        if not v in value:
                            value += ';' + v if ';' in value else v
                        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, value)
                        winreg.CloseKey(key)
                        # notify the system about the changes
                        win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, sub_key)


            except:
                print('\nerror\n')
                import traceback
                print(traceback.print_exc(file=stdout))
            else:
                if verbose:
                    info('INSTALLED', afterString=1)
                else:
                    info('ffmpeg is now up to date', afterString=1, verbose=False)

                try:
                    f = tmp
                    os.remove(f)
                    if 'linux' in system:
                        f = tmp_md5
                        os.remove(f)
                except OSError:
                    info('error:', 'tried to remove temporary files', beforeString=2, afterString=1)
                    check_permission(f)
                else:
                    if verbose:
                        info('ffmpeg is now istalled and temporary files are deleted. good bye.', beforeString=2, afterString=1, indent=False)


    if not os.path.exists(tmp):
        os.mkdir(tmp)
    path = path(topath)
    if verbose:
        info('arch:', arch, beforeString=1, afterString=1)
        info('system:', '{}{}'.format(system, ' (OS X)' if 'darwin' in system else ''), afterString=1)
        info('temp folder:', tmp, afterString=1)
        info('version:')

    if 'linux' in system:
        url = 'https://johnvansickle.com/ffmpeg/releases/'
        r = get(url.rsplit('rel', 1)[0]).text.split('\n')
        latest = [x.strip(' ') for x in r if 'release:' in x][0].split(': ')[1]
        info('{} static (latest release)', latest, afterString=1)
        if verbose:
            info('source:', url.rsplit('/rel', 1)[0], afterString=1)
        if arch in ('armel', 'armhf'):
    	    arch = '{}-32bit'.format(arch)
        file = 'ffmpeg-release-{}-static.tar.xz'.format(arch)
        tmp += file
        tmp_md5 = tmp + '.md5'
        while not check_md5(tmp,tmp_md5):
            dl(url, file, tmp)
            dl(url, file + '.md5', tmp_md5)
        install(path)
    
    if 'darwin' in system:
        if arch == '64bit':
            url = 'http://evermeet.cx/pub/ffmpeg/'
            latest = search('([\d\.]+)(?=.dmg">)', str(get(url).text)).group()
            info('{} static (latest release)', latest, afterString=1)
            if verbose:
                info('source:', url.replace('/pub','').rsplit('/', 1)[0], afterString=1)
            file = 'ffmpeg-{}.dmg'.format(latest)
            tmp += file
            dl(url, file, tmp)
            install(path)
        if arch == "32bit" or '10.5' in platform.mac_ver()[0]:
            url = 'http://www.ffmpegmac.net/resources/'
            file = 'Leopard_29.09.2015.zip'
            tmp += file
            info('2.8 static', afterString=1)
            if verbose:
                info('info:', 'for os x leopard (10.5.*) or 32-bit architecture', afterString=1)
                info('source:', url.rsplit('/', 2)[0], afterString=1)
            dl(url, file, tmp)
            install(path)
        if '10.6' in platform.mac_ver()[0]:
            url = 'http://www.ffmpegmac.net/resources/'
            file = 'SnowLeopard_Lion_Mountain_Lion_Mavericks_Yosemite_El-Captain_28.11.2016.zip'
            tmp += file
            info('3.2.1 static', afterString=1)
            if verbose:
                info('info:', 'for snow leopard (10.6.*)', afterString=1)
                info('source:', url.rsplit('/', 2)[0], afterString=1)
            dl(url, file, tmp)
            install(path)
    
    if 'windows' in system:
        if arch == '64bit':
            arch = 'win64'
        if arch == '32bit':
            arch = 'win32'

        url = 'https://ffmpeg.zeranoe.com/builds/{}/static/'.format(arch)
        latest = search('-([\d\.]+)(?=-{}.+">)'.format(arch), str(get(url).text)).group()[1:]
        file = 'ffmpeg-{1}-{0}-static.zip'.format(arch, latest)
        tmp += file
        info('{} static (latest release)', latest, afterString=1)
        if verbose:
            info('source:', url.rsplit('/', 4)[0], afterString=1)

        if is_zipfile(tmp) is False:
            dl(url, file, tmp)
        install(path)


if __name__ == '__main__':
        arg = args()
        try:
            _run(arg.path, arg.silent, arg.pretty, arg.verbose)
        except KeyboardInterrupt:
            print('\n\nctrl-C: exit')
else:
    class getFFmpeg:
        """
        For module usage, call this class to set wanted options.
        """
        def __init__(self):
            self.path = None
            self.silent = False
            self.pretty = False
            self.verbose = True

        def run(self):
            """
            Execute with custom options. Equivalent to dlffmpeg._run() if options not set.
            """
            _run(self.path, self.silent, self.pretty, self.verbose)