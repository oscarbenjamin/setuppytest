# setup.py

from __future__ import print_function

import os, os.path
import sys
import tarfile
import time
from distutils.sysconfig import get_python_lib
import shutil
import tempfile
from StringIO import StringIO

# Used a lot
join = os.path.join


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

def main(*args):
    if args[0] == 'sdist':
        return sdist(*args[1:])
    elif args[0] == 'egg_info':
        return egg_info(*args[1:])
    elif args[0] == 'install':
        return install(*args[1:])
    else:
        print(args)
        return -1

def sdist():
    # Just like distutils...
    print('running sdist')

    if not os.path.exists('dist'):
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

def _egg_info(egg_dir):

    sources = (
        'PKG-INFO',
        'SOURCES.txt',
        'dependency_links.txt',
        'top_level.txt',
    )

    sourcespaths = tuple(join(egg_dir, s) for s in sources)

    if not os.path.exists(egg_dir):
        os.mkdir(egg_dir)

    with open(join(egg_dir, 'PKG-INFO'), 'w') as pkginfo:
        pkginfo.write(PKG_INFO)

    with open(join(egg_dir, 'SOURCES.txt'), 'w') as sources:
        sources.writelines(MANIFEST + sourcespaths)

    with open(join(egg_dir, 'dependency_links.txt'), 'w') as dep:
        dep.write('\n')

    with open(join(egg_dir, 'top_level.txt'), 'w') as top_level:
        top_level.write('setuppytest\n')


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

    # Okay we now need to know where to put the files.
    site_packages = get_python_lib()

    files_installed = []

    def copy(srcpath, dstname):
        # Find the new destination
        dstpath = join(site_packages, dstname)
        # Create the folder if necessary and remember all created folders
        dstdirtop = os.path.split(dstpath)[0]
        if not os.path.exists(dstdirtop):
            created = []
            dstdir = dstdirtop
            while not os.path.exists(dstdir):
                created.append(dstdir)
                dstdir = os.path.split(dstdir)[0]
            os.makedirs(dstdirtop)
            files_installed.extend(reversed(created))
        # Actually copy the file
        shutil.copyfile(srcpath, dstpath)
        files_installed.append(dstpath)

    # Create the .egg-info directory
    egg_dir = tempfile.mkdtemp()
    _egg_info(egg_dir)

    # What do we call the new .egg-info directory?
    new_egg_dir = '%s-%s-%s.egg-info' % (NAME, VERSION, 'py2.7')

    # Copy .py files to site-packages
    copy('setuppytest.py', 'setuppytest.py')

    # Copy files to the new egg directory
    for fname in os.listdir(egg_dir):
        copy(join(egg_dir, fname), join(new_egg_dir, fname))

    # Copy .egg-info directory
    with open(recordfile, 'w') as record:
        record.writelines(files_installed)

# Be sure to pass on exit code
sys.exit(main(*sys.argv[1:]))
