# setup.py

from __future__ import print_function

import os
from os.path import exists, split, join
import sys
import tarfile
import zipfile
import time
from distutils.sysconfig import get_python_lib
import shutil
import tempfile
import json
import hashlib
from StringIO import StringIO


# :::::::::::::::::
#   Distribution data
# :::::::::::::::::

# Metadata to go in PKG-INFO
NAME = 'setuppytest'
VERSION = '0.1'
URL = 'https://github.com/oscarbenjamin/setuppytest'
AUTHOR = 'Oscar Benjamin'
EMAIL = 'oscar.j.benjamin@gmail.com'

# The content of the PKG-INFO file.
METADATA2 = '''\
Metadata-Version: 2.0
Name: %(Name)s
Version: %(Version)s
Summary: UNKNOWN
Home-page: %(Home-page)s
Author: %(Author)s
Author-email: %(Author-email)s
License: UNKNOWN
Description: UNKNOWN
Platform: UNKNOWN\

UNKOWN


''' % {
    'Name': NAME,
    'Version': VERSION,
    'Home-page': URL,
    'Author': AUTHOR,
    'Author-email': EMAIL,
}

METADATA_VERSION = "2.0"

# Naming conventions
PYVERSION = sys.version_info[:2]
# The name of any generated sdist archive.
SDIST_NAME = '%s-%s' % (NAME, VERSION)
# The name of the directory where .egg-info is installed in site-packages.
EGG_INFO_NAME = '%s-%s-py%s.%s.egg-info' % ((NAME, VERSION) + PYVERSION)
# The name of the generated wheel file:
# http://www.python.org/dev/peps/pep-0427/
WHEEL_TAG = 'py%s%s-none-any' % PYVERSION
WHEEL_NAME = '%s-%s-%s-none-any.whl' % (NAME, VERSION, WHEEL_TAG)
WHEEL_GENERATOR = 'setuppytest (%s)' % VERSION
WHEEL_META = '''\
Wheel-Version: 1.0
Generator: %s
Root-Is-Purelib: true
Tag: %s

''' % (WHEEL_GENERATOR, WHEEL_TAG)

# for the pydist.json file in a generated wheel.
PYDIST_JSON = {
    "document_names": {"description": "DESCRIPTION.rst"},
    "name": NAME,
    "metadata_version": METADATA_VERSION,
    "contacts": [{"role": "author", "email": EMAIL, "name": AUTHOR}],
    "generator": WHEEL_GENERATOR,
    "summary": "UNKNOWN",
    "project_urls": {"Home": URL},
    "version": VERSION,
}

# Top-level modules
MODULES = (
    'setuppytest',
)
# Files to be included in sdist.
# PKG-INFO is generated automatically.
MANIFEST_IN = (
    'setup.py',
    'README',
)

MODULES_PY = tuple(m + '.py' for m in MODULES)
MANIFEST = MODULES_PY + MANIFEST_IN

# :::::::::::::::::
#   Commands
# :::::::::::::::::

def main(*args):
    if not args or args[0] not in COMMANDS:
        print(repr(args))
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
        archive.addfile(info, StringIO(METADATA2))

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
    new_egg_path = join(site_packages, EGG_INFO_NAME)

    # Copy .py files to site-packages
    for module in MODULES_PY:
        _copy(module, join(site_packages, module), files_installed)

    # Copy files to the new egg directory
    for fname in os.listdir(egg_dir):
        src = join(egg_dir, fname)
        dst = join(new_egg_path, fname)
        _copy(src, dst, files_installed)

    # Write installed files to the record file
    with open(recordfile, 'w') as record:
        record.write('\n'.join(files_installed))

def bdist_wheel(*args):
    # Accept only these exact invocations until otherwise required.
    assert len(args) == 2
    wheelhouse = args[1]
    assert args == ('-d', wheelhouse)

    if not exists('build'):
        os.mkdir('build')

    # Temporary workspace
    builddir = tempfile.mkdtemp()

    # Keep track of all created files
    files_installed = []

    def open_app(path):
        f = open(join(builddir, path), 'w')
        files_installed.append(path)
        return f

    # First copy in any module files
    for module in MODULES_PY:
        shutil.copy(module, join(builddir, module))
        files_installed.append(module)

    # Now create the .dist-info directory
    distinfodir = SDIST_NAME + '.dist-info'
    os.mkdir(join(builddir, distinfodir))

    with open_app(join(distinfodir, 'DESCRIPTION.rst')) as description:
        description.write('UNKOWN\n\n\n')

    with open_app(join(distinfodir, 'METADATA')) as metadata:
        metadata.write(METADATA2)

    with open_app(join(distinfodir, 'WHEEL')) as wheelmeta:
        wheelmeta.write(WHEEL_META)

    with open_app(join(distinfodir, 'pydist.json')) as pydist_json:
        json.dump(PYDIST_JSON, pydist_json)

    with open_app(join(distinfodir, 'top_level.txt')) as top_level:
        top_level.write('\n'.join(MODULES))

    # Now compute hashes and lengths for the RECORD file
    # Needs to be last.
    N = len(builddir)
    recordname = join(distinfodir, 'RECORD')
    with open_app(recordname) as record:
        for path in files_installed:
            if path != recordname:
                print(path)
                with open(join(builddir, path)) as fin:
                    data = fin.read()
                hash = hashlib.sha256(data)
                length = len(data)
            else:
                hash = length = ''
            record.write('%s,%s,%s\n' % (path, hash, length))

    # Create the zipfile in-place
    with zipfile.ZipFile(join(wheelhouse, WHEEL_NAME), 'w') as wheel:
        for path in files_installed:
            wheel.write(os.path.join(builddir, path), path)


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
        pkginfo.write(METADATA2)

    with open(join(egg_dir, 'SOURCES.txt'), 'w') as sources:
        sources.write('\n'.join(MANIFEST + sourcespaths))

    with open(join(egg_dir, 'dependency_links.txt'), 'w') as dep:
        dep.write('\n')

    with open(join(egg_dir, 'top_level.txt'), 'w') as top_level:
        top_level.write('\n'.join(MODULES))


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
