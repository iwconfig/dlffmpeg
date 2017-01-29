"""
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

run() uses default path.
run('/path') installs ffmpeg into custom '/path'.
As standalone: takes 0 or 1 argument. Either default or custom path.
"""
import os, platform
from requests import get, Timeout, ConnectionError
from tempfile import gettempdir
from sys import stdout, argv, exit
from subprocess import check_output, call

system = platform.system().lower()
# system = 'darwin'
if any(x in system for x in ['darwin', 'windows']):
    from zipfile import ZipFile, is_zipfile
    from re import sub, findall
    from pkg_resources import parse_version
    from shutil import copy2


def run(topath = None, silent = False, pretty=False, verbose=True):
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
            t = ''; k += ' '

        if k and v == None:
            k = '{}'.format(k)

        if v:
            if '{}' in k:
                k = k.format(v)
            else:
                k = k+t+v
        stdout.write('{}{}{}{}'.format('\n'*beforeString, '\t'*indent, k, '\n'*afterString))
        stdout.flush()
        
    def arch():
        arches = {'64bit':   ['x86_64','x86-64','amd64', 'x64', '64'],
              '32bit':   ['x86', 'x32', '32', 'i686', 'i386'],
              'armel' :   ['armv4tl', 'armv5l', 'armv6l'],
              'armhf' :   ['armv7l', 'armv8l']}
        
        for k, v in arches.iteritems():
            if [x for x in v if x == platform.machine().lower()]:
                return k

    def path(path = None):
        if path == None:
            if 'linux' in system:
                path = '/usr/local/bin/'
            if 'darwin' in system:
                ##### ---> path = '/tmp/mac'
                path = '/tmp/mac'
            if 'windows' in system:
                if arch == '64bit':
                    path = 'C:\\Program Files\\ffmpeg\\'
                    path = '/tmp/blahej/ffmpeg/'
                if arch == '32bit':
                    path = 'C:\\Program Files (x86)\\ffmpeg\\'
                    path = '/tmp/blahej/ffmpeg/'
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
            return path
        else:
            return False    

    def check_md5(file_name, md5_file):
        if os.path.isfile(md5_file) == False or os.path.isfile(file_name) == False:
            return False
        else:
            from hashlib import md5
            if verbose:
                info('checksum:')
            with open(md5_file) as md5_to_verify:
                original_md5 = md5_to_verify.read().split(' ')[0]
            with open(file_name) as file_to_check:
                data = file_to_check.read()    
                md5_returned = md5(data).hexdigest()
            if original_md5 == md5_returned:
                if verbose:
                    info('verified', afterString=1)
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
            info('downloading:', file)
        else:
            if file.endswith('.md5'):
                info('downloading md5 sum',afterString=1, verbose=False)
            info('downloading ffmpeg',afterString=1, verbose=False)
            
        while True:
            for x in range(5):
                r = get(url + file)
                print r.text
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
                    print 'hello'
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
            if os.path.exists(path + os.sep + 'ffmpeg'):
                if verbose:
                    info('old ffmpeg:', beforeString=2)
                    
                for p, d, f in os.walk(path, topdown=False):
                    if 'linux' in system:
                        for n in ['ffmpeg', 'ffmpeg-10bit', 'ffprobe', 'ffserver']:
                            os.remove(os.path.join(p, n))
                    else:
                        for n in f:
                            os.remove(os.path.join(p, n))
                        for n in d:
                            os.rmdir(os.path.join(p, n))
                if verbose:
                    info('removed', afterString=2)
        except:
            info('error', afterString=1)
            if os.getuid != 0:
                print 'you need root access for this.'
                exit(1)
                
        else:
            try:
                if verbose:
                    info('install path:', '{}{}'.format(path, ' (default)' if not args.path else ''))
                    info('installing:', beforeString=1)
                if 'linux' in system:
                    check_output(['tar', '-tf', tmp]).splitlines()[0]
                    call(['sudo', 'tar', '-xJf', tmp, '--strip-components=1', '--overwrite', '-C', path, '--wildcards', '*/ffmpeg', '*/ffmpeg-10bit', '*/ffprobe', '*/ffserver'])
                if 'darwin' in system:
                    if arch == '64bit':
                        call(['hdiutil', 'attach', tmp])
                        info('copying:', 'ffmpeg -> '+path)
                        copy2('/Volumes/FF*/ffmpeg', path)
                    if arch == '32bit' or platform.mac_ver()[0].rsplit('.', 1)[0] in ('10.5', '10.6'):
                        zf = ZipFile(tmp, 'r')
                        zf.extractall(path)
                        zf.close()
                if 'windows' in system:
                    zf = ZipFile(tmp, 'r')
                    for i in zf.namelist():
                        if i == zf.namelist()[0]:
                            continue
                        f = i.split('/')
                        f.pop(0)
                        d = path + os.sep.join(f[0:-1])
                        if not os.path.exists(d):
                            os.makedirs(d)
                            continue
                        data = zf.read(i, tmp)
                        file = d + os.sep + f[-1]
                        f = open(file,'wb+')
                        f.write(data)
                        f.close()
                    zf.close()
                    call(['setx', '/M', 'PATH', path + 'ffmpeg\\bin;%PATH%'], shell=False)
    
            except:
                print '\nerror\n'
                import traceback
                print traceback.print_exc(file=stdout)
            else:
                if verbose:
                    info('INSTALLED', afterString=1)
                else:
                    info('ffmpeg is now up to date', afterString=1, verbose=False)
    
                os.remove(tmp)
                if 'linux' in system:
                    os.remove(tmp_md5)
                if verbose:
                    info('ffmpeg is now istalled and temporary files are deleted. good bye.', beforeString=2, afterString=1, indent=False)


    arch = arch()
    tmp = gettempdir() + os.sep
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
            info('source:', url.rsplit('/rel', 1)[0], afterString=2)
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
            r = get(url)
            latest = findall(r'ffmpeg.+(?=.dmg">)', str(r.text))
            latest = '.'.join(findall('\d', max(latest, key=parse_version)))
            info('{} static (latest release)', latest, afterString=1)
            if verbose:
                info('source:', url.replace('/pub','').rsplit('/', 1)[0], afterString=2)
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
                info('source:', url.rsplit('/', 2)[0], afterString=2)
            dl(url, file, tmp)
            install(path)
        if '10.6' in platform.mac_ver()[0]:
            url = 'http://www.ffmpegmac.net/resources/'
            file = 'SnowLeopard_Lion_Mountain_Lion_Mavericks_Yosemite_El-Captain_28.11.2016.zip'
            tmp += file
            info('3.2.1 static', afterString=1)
            if verbose:
                info('info:', 'for snow leopard (10.6.*)', afterString=1)
                info('source:', url.rsplit('/', 2)[0], afterString=2)
            dl(url, file, tmp)
            install(path)
    
    if 'windows' in system:
        r = get('http://ffmpeg.org/releases/')
        latest = findall(r'ffmpeg.+(?=.tar.+">)', str(r.text))
        latest = '.'.join(findall('\d', max(latest, key=parse_version)))
        if arch == '64bit':
            arch = 'win64'
        if arch == '32bit':
            arch = 'win32'
        url = 'https://ffmpeg.zeranoe.com/builds/{}/static/'.format(arch)
        file = 'ffmpeg-{1}-{0}-static.zip'.format(arch, latest)
        tmp += file
        info('{} static (latest release)', latest, afterString=2)
        if verbose:
            info('source:', url.rsplit('/', 4)[0], afterString=2)
        if is_zipfile(tmp) is False:
            dl(url, file, tmp)
        install(path)

h = """
dlffmpeg
    

usage:
  dlffmpeg.py (default path)
  dlffmpeg.py (options) <path>
  
  pass 1 argument to specify install path or 0 argument for default install path.
  
  
options:
  -h --help     show this screen.
  -v --version     show version.
  -q --quiet    be quiet.
"""
if __name__ == '__main__':
    __version__ = '0.3'
    from argparse import ArgumentParser
    p = ArgumentParser(description='pass 1 argument to specify install path or 0 argument for default install path')
    p.add_argument('path', nargs='?', const=None)
    p.add_argument('-s', '--silent', action='store_true', dest='silent')
    p.add_argument('-lv', '--less-verbose', action='store_false', dest='verbose')
    p.add_argument('-p', '--pretty', action='store_false', dest='pretty')
    p.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))

    args = p.parse_args()
    print args
    len(argv)
    if len(argv) == 1:
        print 'path empty'
    try:
        run(args.path, args.silent, args.pretty, args.verbose)
    except KeyboardInterrupt:
        print '\n\nctrl-C: exit'