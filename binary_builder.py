#!/usr/bin/env python
from __future__ import print_function
from platform import system
import os, shutil, argparse

__version__ = '0.1'

def main(args):
    path = os.getcwd()
    while not args.file:
        def dirlist(path = path):
            ls = [x for x in os.listdir(path) if x.endswith(('.spec', '.py')) and not x in ('setup.py', os.path.basename(__file__))]
            ls.sort(key=lambda f: os.path.splitext(f)[1], reverse=True)
            default = 'build.spec'
            if not default in ls:
                default = [x for x in ls if x.endswith('.spec')][0]
            ls.insert(0, ls.pop(ls.index(default)))
            if not ls:
                return False
            else: return ls

        def nlist(ls, num = {}):
            for n, d in enumerate(ls, 1):
                print('{0}) {1}'.format(n, d))
                num[n] = d
                if d == ls[-1]:
                    print('{0}) {1}'.format(n+1, '::CHOOSE ANOTHER DIRECTORY::'))
                    num[n+1] = None
            return num
    
        ls = dirlist(path)
        if ls:
            num = nlist(ls)
        print('Select file (default: {}) [number/enter]:'.format(ls[0]), end=' ')
        while True:
            n = raw_input()
            if not n:
                n = '1'
            if n.isdigit():
                n = int(n)
                if n in num.keys():
                    break
            print('\nEnter valid number [{0}-{1}]:'.format(num.keys()[0], num.keys()[-1]), end=' ')
    
        if n == num.keys()[-1]:
            while True:
                print('\nEnter path to look for files:', end=' ')
                path = raw_input()
                if not os.path.isdir(path):
                    print('Not a valid path. Try again.')
                if not dirlist(path):
                    print('No *.spec or *.py found. Enter another path.')
                else:
                    os.chdir(path)
                    break
        else:
            args.file = os.path.abspath(num[n])
    
    
    if not os.path.isfile(os.path.abspath(args.file)):
        print('not a real file')
        os._exit(1)
    else:
        dirname = os.path.dirname(args.file)
        shutil.rmtree('{}/__pycache__'.format(dirname), ignore_errors=True)
        shutil.rmtree('{}/build/'.format(dirname), ignore_errors=True)
        shutil.rmtree('{}/dist/'.format(dirname), ignore_errors=True)
        pyc = '{}/dlffmpeg.pyc'.format(dirname)
        os.path.exists(pyc) and os.remove(pyc)
    
    
    def choose(message = None):
                print(message, end=' ')
                yes = set(['yes','y', 'ye', ''])
                no = set(['no','n'])
                choice = raw_input().lower()
                if choice in yes:
                    return True
                elif choice in no:
                    return False
                else:
                   print("Please respond with 'yes' or 'no'")
    
    def which(program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
        return None
    
    
    if args.unix:
        if which('pyinstaller'):
            os.system('pyinstaller --onefile {}'.format(args.file))
    
    if args.windows:
        if not 'windows' in system:
            try:
                prefix = os.environ['WINEPREFIX']
                print('running under wine')
            except KeyError:
                choice = choose("Can't find wine path. Is Wine installed? [y/n]")
                if choice == True:
                    print("Please specify the wine path below. Press 'enter' for default (~/.wine):", end=' ')
                    prefix = raw_input()
                    if prefix == '':
                        prefix = os.path.expanduser('~/.wine')
                    if prefix.startswith('~'):
                        prefix = os.path.expanduser(prefix)
                    choice = choose("Is {} correct? [y/n]".format(prefix))
                    prefix = os.environ['WINEPREFIX'] = prefix
                    with open(os.path.expanduser('~/.bashrc'), 'a') as bashrc:
                        bashrc.write("\nexport WINEPREFIX={}\n".format(prefix))
                        print('Wrote env. variable WINEPREFIX={} to ~/.bashrc'.format(prefix))
                else:
                    print('Please install Wine and Python (under Wine).')
                    print('\n# Follow theese instructions:')
                    print('# Install Wine with apt-get')
                    print('sudo dpkg --add i386 # If you want 32bit support')
                    print('sudo apt-get install wine')
                    print('\n# Downloading python version 3.4.4 (latest available with MSI installer) ...')
                    try:
                        from urllib.request import urlretrieve as dl
                    except ImportError:
                        from urllib import urlretrieve as dl
                    f = dl('https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi', '/tmp/python-3.4.4.msi')[0]
                    print('# Done. Now install Python using the following:')
                    print('wine msiexec /i {} /L*v log.txt'.format(f))
                    print('wine C:/Python34/python.exe C:/Python34/Scripts/pip.exe install -U pip')
                    print('wine C:/Python34/python.exe C:/Python34/Scripts/pip.exe install -U pyinstaller')
                    print('\n# Alright, do this and come back ok. Bye.')
                    os._exit(0)
            if prefix:
                os.system('DISPLAY=:0.0 WINEDEBUG=fixme-all wine {prefix}/drive_c/Python34/Scripts/pyinstaller.exe --onefile {file}'.format(prefix=prefix, file=args.file))

if __name__ == '__main__':
        system = system().lower()
        if 'windows' in system:
            print('*nix only at the moment, sorry.')
            os._exit(0)
        
        p = argparse.ArgumentParser(description="Compile script to binary executable")
        p.add_argument('file', nargs='?', const=None, help=".spec or .py file")
        p.add_argument('-u', '--unix', action='store_true', dest='unix', help="Compile single *nix binary executable")
        p.add_argument('-w', '--windows', action='store_true', dest='windows', help="Compile single Windows binary executable (*.exe)")
        p.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
        
        args = p.parse_args()
        if not any([args.unix, args.windows]):
            print('need at least one option')
            os._exit(1)
            
        try:
            main(args)
        except KeyboardInterrupt:
            print('\n\nctrl-C: exit')