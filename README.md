setuppytest
===============

Minimal setup.py implementation.

This repository shows how to implement a minimal setup.py that can be in an sdist so that pip could install from the sdist. The setup.py supports only the following invocations:

sdist
-----

    $ python setup.py sdist

The sdist command just creates an sdist `.tar.gz` archive under the `dist`
directory. This isn't directly by `pip` but we need an `sdist` before we can
invoke pip.

    $ python setup.py egg_info --egg-base $EGG_DIRECTORY

egg-info
--------

The `egg_info` commmand creates a `.egg-info` directory inside
`$EGG_DIRECTORY` and adds the following files:

* `PKG-INFO` : Distribution metadata in metadata version 1.0 format.
* `SOURCES.txt` : A list of the files in the project and in the `.egg-info`
                  directory.
* `dependency_links.txt` : An empty file
* `top_level.txt` : The name of the top-level module that will be installed.

The `egg_info` command is called by pip before installation. Presumably the
important part is the `dependency_links.txt` file that would be used to
discover if this distribution depends on any other distributions. `pip` would
want to install the othe

install
-------

    $ python setup.py install --record $RECORD_FILE         \
                        --single-version-externally-managed

    $ python setup.py install --record $RECORD_FILE         \
                        --single-version-externally-managed \
                        --intall-headers $HEADERS_DIR

After calling `egg_info` pip will call the `install` command. This needs to
copy/create any files in `site-packages` or anywhere else on the system. It
also needs to create/copy the `.egg-info` directory into site-packages.  A
list of all the installed files including those in the `.egg-info` directory
is written to `$RECORD_FILE`. When installing into a virtualenv the
`--install-headers` option is passed to the `install` command.
