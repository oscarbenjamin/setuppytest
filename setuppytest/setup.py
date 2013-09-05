# setup.py

from __future__ import print_function

import os
from os.path import exists, split, join
import sys
import tarfile
import time
from distutils.sysconfig import get_python_lib
import shutil
import tempfile
from StringIO import StringIO


# :::::::::::::::::
#   Distribution data
# :::::::::::::::::

# Metadata to go in PKG-INFO
NAME = 'setuppytest'
VERSION = '0.1'

# The content of the PKG-INFO file.
PKG_INFO = '''\
Metadata-Version: 1.0
Name: %(Name)s
Version: %(Version)s
Summary: UNKNOWN
Home-page: http://example.com
Author: John Cleese
Author-email: john.cleese@example.com
License: UNKNOWN
Description: UNKNOWN
Platform: UNKNOWN\
''' % {'Name': NAME, 'Version': VERSION}

SDIST_NAME = '%s-%s' % (NAME, VERSION)

# Files to be included in sdist.
# PKG-INFO is generated automatically.
MANIFEST = (
    'setup.py',
    'setuppytest.py',
    'README',
)

# :::::::::::::::::
#   Commands
# :::::::::::::::::

def main(*args):
    if not args or args[0] not in COMMANDS:
        print(args)
        return -1
    # Delegate to the appropriate subcommand
    return COMMANDS[args[0]](*args[1:])

def sdist():
    # Just like distutils...
    print('running sdist')

    if not exists('dist'):
        os.mkdir('dist')

    archivepath = join('dist', SDIST_NAME + '.tar.gz')

    with tarfile.open(archivepath, 'w:gz') as archive:
        # Add each file from MANIFEST
        for filename in MANIFEST:
            filepath = join(SDIST_NAME, filename)
            archive.add(filename, filepath)
        # Create and add PKG-INFO
        info = tarfile.TarInfo(join(SDIST_NAME, 'PKG-INFO'))
        info.mtime = time.time()
        archive.addfile(info, StringIO(PKG_INFO))
    
    return 0

def egg_info(*args):
    print('running egg_info')

    # We will only accept precisely this invocation until otherwise required
    assert len(args) == 2 and args[0] == '--egg-base'
    egg_base = args[1]

    egg_dir = join(egg_base, NAME + '.egg-info')

    _egg_info(egg_dir)

    return 0

def install(*args):
    print('running install')

    # We will only accept precisely these invocations until otherwise required
    recordfile = args[1]
    first3, rest = args[:3], args[3:]
    assert first3 == (
            '--record', recordfile, '--single-version-externally-managed')

    # For a virtualenv we may get the '--install-headers' arg
    if rest:
        assert len(rest) == 2
        headers = rest[1]
        assert rest == ('--install-headers', headers)

    # We need to know where to put the files.
    # FIXME -- won't work for --user
    site_packages = get_python_lib()

    # Keep track of all files created for the record file
    files_installed = []

    # Create the .egg-info directory
    egg_dir = tempfile.mkdtemp()

    # Populate temporary directory with egg-info data
    _egg_info(egg_dir)

    # What do we call the new .egg-info directory?
    new_egg_dir = '%s-%s-%s.egg-info' % (NAME, VERSION, 'py2.7')
    new_egg_path = join(site_packages, new_egg_dir)

    # Copy .py files to site-packages
    _copy('setuppytest.py', join(site_packages, 'setuppytest.py'), files_installed)

    # Copy files to the new egg directory
    for fname in os.listdir(egg_dir):
        src = join(egg_dir, fname)
        dst = join(new_egg_path, fname)
        _copy(src, dst, files_installed)

    # Write installed files to the record file
    with open(recordfile, 'w') as record:
        record.write('\n'.join(files_installed))

def bdist_wheel(*args):
    pass

COMMANDS = {
    'sdist': sdist,
    'egg_info': egg_info,
    'install': install,
    'bdist_wheel': bdist_wheel,
}

# :::::::::::::::::
#   Utilities
# :::::::::::::::::

def _egg_info(egg_dir):
    '''Populate directory egg_dir with egg-style metadata.'''

    sources = (
        'PKG-INFO',
        'SOURCES.txt',
        'dependency_links.txt',
        'top_level.txt',
    )

    sourcespaths = tuple(join(egg_dir, s) for s in sources)

    if not exists(egg_dir):
        os.mkdir(egg_dir)

    with open(join(egg_dir, 'PKG-INFO'), 'w') as pkginfo:
        pkginfo.write(PKG_INFO)

    with open(join(egg_dir, 'SOURCES.txt'), 'w') as sources:
        sources.write('\n'.join(MANIFEST + sourcespaths))

    with open(join(egg_dir, 'dependency_links.txt'), 'w') as dep:
        dep.write('\n')

    with open(join(egg_dir, 'top_level.txt'), 'w') as top_level:
        top_level.write('setuppytest\n')


def _copy(srcpath, dstpath, files_installed):
    '''Copy file from srcpath to dstpath.

    Parent directories of dstpath are created if necessary.
    Created directories and the installed file are appended to
    files_installed.
    '''
    dstdirtop = split(dstpath)[0]
    if not exists(dstdirtop):
        created = []
        dstdir = dstdirtop
        while not exists(dstdir):
            assert dstdir, 'no such directory: %r' % srcpath
            created.append(dstdir)
            dstdir = split(dstdir)[0]
        os.makedirs(dstdirtop)
        files_installed.extend(reversed(created))
    # Actually copy the file
    shutil.copyfile(srcpath, dstpath)
    files_installed.append(dstpath)


# Be sure to pass on exit code
if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
