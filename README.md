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
want to install the other distributions before running the `install` command.
In this minimal example there are no dependencies so this is an empty file.

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

bdist-wheel
-----------

    $ python setup.py bdist_wheel -d $WHEEL_HOUSE

When using `pip wheel X` pip will obtain the `sdist` unpack it, run `egg_info`
and then run `bdist_wheel` with the line above. The `setup.py` script should
create a PEP-427 wheel file under the directory `$WHEEL_HOUSE` with a filename
like `setuppytest-0.1-py27-none-any-none-any.whl`. The resulting wheel file
can then be installed with `pip install $WHEEL_NAME`.

testing 'pip install X'
-----------------------

Test if setuppytest is installed yet:

    $ pip list | grep setuppytest
    $ python -m setuppytest
    q:\tools\Python27\python.exe: No module named setuppytest

Checkout and build the sdist:

    $ git clone https://github.com/oscarbenjamin/setuppytest
    Cloning into setuppytest...
    remote: Counting objects: 24, done.
    remote: Compressing objects: 100% (18/18), done.
    remote: Total 24 (delta 5), reused 23 (delta 4)
    Unpacking objects: 100% (24/24), done.
    $ cd setuppytest/setuppytest/
    $ python setup.py sdist
    running sdist
    $ ls dist
    setuppytest-0.1.tar.gz

Install from the sdist and test

    $ pip install dist/setuppytest-0.1.tar.gz
    Unpacking .\dist\setuppytest-0.1.tar.gz
      Running setup.py egg_info for package from file:///q%7C%5Ccurrent%5Ctmp%5Ctpip%5Csetuppytest%5Csetuppytest%5Cdist%5Csetuppytest-0.1.tar.gz
    Installing collected packages: setuppytest
      Running setup.py install for setuppytest
    Successfully installed setuppytest
    Cleaning up...

Test the installation

    $ pip list | grep setuppytest
    setuppytest (0.1)
    $ cd ..  # Don't import setuppytest.py from cwd
    $ python -m setuppytest
    setuppytest.py
    getcwd(): "q:\current\tmp\tpip\setuppytest"
    __file__: "q:\tools\Python27\lib\site-packages\setuppytest.py"
    __name__: "__main__"

Test uninstallation

    $ pip uninstall setuppytest
    Uninstalling setuppytest:
      q:\tools\python27\lib\site-packages\setuppytest-0.1-py2.7.egg-info
      q:\tools\python27\lib\site-packages\setuppytest.py
    Proceed (y/n)? y
      Successfully uninstalled setuppytest
    $ pip list | grep setuppytest
    $ python -m setuppytest
    q:\tools\Python27\python.exe: No module named setuppytest

testing 'pip wheel X'
---------------------

Build a wheel

    $ cd setuppytest  # Back to the VCS root
    $ pip wheel dist/setuppytest-0.1.tar.gz
    Unpacking .\dist\setuppytest-0.1.tar.gz
      Running setup.py egg_info for package from file:///q%7C%5Ccurrent%5Csrc%5Csetuppytest%5Csetuppytest%5Cdist%5Csetuppytest-0.1.tar.gz
    Building wheels for collected packages: setuppytest
      Running setup.py bdist_wheel for setuppytest
      Destination directory: q:\current\src\setuppytest\setuppytest\wheelhouse
    Successfully built setuppytest
    Cleaning up...
    $ pip install wheelhouse/setuppytest-0.1-py27-none-any-none-any.whl
    Unpacking .\wheelhouse\setuppytest-0.1-py27-none-any-none-any.whl
    Installing collected packages: setuppytest
    Successfully installed setuppytest
    Cleaning up...

Test the wheel

    $ pip list | grep setuppytest
    setuppytest (0.1)
    $ cd ..
    $ python -m setuppytest
    setuppytest.py
    getcwd(): "q:\current\src\setuppytest"
    __file__: "q:\tools\Python27\lib\site-packages\setuppytest.py"
    __name__: "__main__"

And uninstall again

    $ pip uninstall setuppytest
    Uninstalling setuppytest:
      q:\tools\python27\lib\site-packages\setuppytest-0.1.dist-info\description.rst
      q:\tools\python27\lib\site-packages\setuppytest-0.1.dist-info\metadata
      q:\tools\python27\lib\site-packages\setuppytest-0.1.dist-info\pydist.json
      q:\tools\python27\lib\site-packages\setuppytest-0.1.dist-info\record
      q:\tools\python27\lib\site-packages\setuppytest-0.1.dist-info\top_level.txt
      q:\tools\python27\lib\site-packages\setuppytest-0.1.dist-info\wheel
      q:\tools\python27\lib\site-packages\setuppytest.py
    Proceed (y/n)? y
      Successfully uninstalled setuppytest
    $ pip list | grep setuppytest
    $ cd ..
    $ python -m setuppytest
    q:\tools\Python27\python.exe: No module named setuppytest
