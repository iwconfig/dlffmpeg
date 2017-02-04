from __future__ import print_function
from setuptools import setup
from dlffmpeg import __version__

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
    print('converted README.md into RST format')
except (ImportError, OSError):
    from sys import argv, exit
    if not 'install' in argv[1:]:
        print('try running `pip install -U pypandoc`')
        print('you might need to install pandoc manually. consult the instructions at https://github.com/bebraw/pypandoc#installing-pandoc-manually')
        exit(1)
    print('pypandoc not found. using original markdown for long description instead')
    long_description = open('README.md').read()
    

setup(
    name = 'dlffmpeg',
    version = __version__,
    description = 'Download and install ffmpeg, cross-platform.',
    long_description = long_description,
    author = 'iwconfig',
    author_email = 'snelhingst@gmail.com',
    url = 'https://github.com/iwconfig/dlffmpeg', 
    py_modules=['dlffmpeg'],
    install_requires=[
        'cursor>=1.1.0',
        'requests>=2.0.0'
    ],
    scripts = ['bin/dlffmpeg'],

    license = 'MIT',
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Operating System :: POSIX',
                 'Operating System :: Unix',
                 'Operating System :: MacOS',
                 'Operating System :: Microsoft :: Windows',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python',
                 'Topic :: Internet :: WWW/HTTP',
                 'Topic :: Multimedia :: Sound/Audio',
                 'Topic :: Multimedia :: Video',
                 'Topic :: System :: Installation/Setup',
                 'Topic :: Utilities']

)