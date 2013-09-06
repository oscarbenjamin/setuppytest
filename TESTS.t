setuppytest tests
=================

Minimal setup.py implementation.

This repository shows how to implement a minimal setup.py that can be in an
sdist so that pip could install from the sdist. The setup.py supports only the
following invocations.

First we need to get into the right directory and create a virtualenv.

  $ cd "${CWD}"

  $ if [ ! -d tmpvenv ]; then
  >     python -m virtualenv tmpvenv
  >     . tmpvenv/Scripts/activate
  >     pip install wheel
  > fi

  $ . tmpvenv/Scripts/activate

Now go to where the setup.py is and cleanup any old build artifacts

  $ if [ -d wheelhouse ]; then
  >    rm -r wheelhouse
  > fi

  $ cd "${CWD}/setuppytest"

  $ if [ -d wheelhouse ]; then
  >    rm -r wheelhouse
  > fi

  $ if [ -e ./dist/setuppytest.0.1.tar.gz ]; then
  >     rm dist/setuppytest.0.1.tar.gz
  > fi

  $ if [ -d ./eggsdir ]; then
  >     rm -r ./eggsdir
  > fi

  $ if [ -d ./setuppytest.egg-info ]; then
  >     rm -r ./setuppytest.egg-info
  > fi

  $ if [ -e dist/record.txt ]; then
  >     rm dist/record.txt
  > fi

Create the sdist
----------------

Actually create the sdist.

  $ python setup.py sdist
  running sdist

Check that it was actually created.

  $ ls ./dist
  setuppytest-0.1.tar.gz

  $ tar -tzf ./dist/setuppytest-0.1.tar.gz
  setuppytest-0.1/setuppytest.py
  setuppytest-0.1/setup.py
  setuppytest-0.1/README
  setuppytest-0.1[\/\\]+PKG-INFO (re)

egg-info
--------

The `egg_info` commmand creates a `.egg-info` directory inside
`$EGG_DIRECTORY` and adds the following files:

  $ python setup.py egg_info --egg-base .
  running egg_info

  $ ls setuppytest.egg-info
  PKG-INFO
  SOURCES.txt
  dependency_links.txt
  top_level.txt

  $ cat setuppytest.egg-info/PKG-INFO
  Metadata-Version: 2.0
  Name: setuppytest
  Version: 0.1
  Summary: UNKNOWN
  Home-page: https://github.com/oscarbenjamin/setuppytest
  Author: Oscar Benjamin
  Author-email: oscar.j.benjamin@gmail.com
  License: UNKNOWN
  Description: UNKNOWN
  Platform: UNKNOWN
  UNKOWN
  
  

  $ cat setuppytest.egg-info/SOURCES.txt
  setuppytest.py
  setup.py
  README
  .\setuppytest.egg-info\PKG-INFO
  .\setuppytest.egg-info\SOURCES.txt
  .\setuppytest.egg-info\dependency_links.txt
  .\setuppytest.egg-info\top_level.txt (no-eol)

  $ cat setuppytest.egg-info/dependency_links.txt
  

  $ cat setuppytest.egg-info/top_level.txt
  setuppytest (no-eol)


The `egg_info` command is called by pip before installation. Presumably the
important part is the `dependency_links.txt` file that would be used to
discover if this distribution depends on any other distributions. `pip` would
want to install the other distributions before running the `install` command.
In this minimal example there are no dependencies so this is an empty file.

install
-------

  $ python setup.py install --record dist/record.txt    \
  >                 --single-version-externally-managed
  running install

  $ cat dist/record.txt
  .+\\setuppytest.py (re)
  .+\\setuppytest-0.1-py2.7.egg-info (re)
  .+\\setuppytest-0.1-py2.7.egg-info\\dependency_links.txt (re)
  .+\\setuppytest-0.1-py2.7.egg-info\\PKG-INFO (re)
  .+\\setuppytest-0.1-py2.7.egg-info\\SOURCES.txt (re)
  .+\\setuppytest-0.1-py2.7.egg-info\\top_level.txt (re)

  $ cd ..  # Don''t import from CWD

  $ python -m setuppytest
  setuppytest.py
  getcwd\(\): ".*\\setuppytest" (re)
  __file__: ".*\\site-packages\\setuppytest.py" (re)
  __name__: "__main__"

  $ pip uninstall -y setuppytest
  Uninstalling setuppytest:
    Successfully uninstalled setuppytest

  $ python -m setuppytest
  .*python.exe: No module named setuppytest (re)
  [1]

  $ cd setuppytest

After calling `egg_info` pip will call the `install` command. This needs to
copy/create any files in `site-packages` or anywhere else on the system. It
also needs to create/copy the `.egg-info` directory into site-packages.  A
list of all the installed files including those in the `.egg-info` directory
is written to `$RECORD_FILE`. When installing into a virtualenv the
`--install-headers` option is passed to the `install` command.

bdist-wheel
-----------

  $ mkdir wheelhouse

  $ python setup.py bdist_wheel -d wheelhouse
  running bdist_wheel

When using `pip wheel X` pip will obtain the `sdist` unpack it, run `egg_info`
and then run `bdist_wheel` with the line above. The `setup.py` script should
create a PEP-427 wheel file under the directory `$WHEEL_HOUSE` with a filename
like `setuppytest-0.1-py27-none-any-none-any.whl`. The resulting wheel file
can then be installed with `pip install $WHEEL_NAME`.

bdist-egg
---------

  $ mkdir eggsdir

  $ python setup.py -q bdist_egg --dist-dir eggsdir
  running bdist_egg

  $ ls eggsdir
  setuppytest-0.1-py2.7.egg

  $ rm -r eggsdir

When using `'easy_install x'` the sdist will be extracted and the line above
is run. The `setup.py` script should create a `.egg` archive inside the
`$DIST_DIR` directory.

testing 'pip install X'
-----------------------

Test if setuppytest is installed yet:

  $ cd ..

  $ python -m setuppytest
  .*\python.exe: No module named setuppytest (re)
  [1]

  $ cd setuppytest

Install from the sdist and test

  $ pip install dist/setuppytest-0.1.tar.gz
  Unpacking .\dist\setuppytest-0.1.tar.gz
    Running setup.py egg_info for package from file:\/\/.*dist%5Csetuppytest-0.1.tar.gz (re)
  Installing collected packages: setuppytest
    Running setup.py install for setuppytest
  Successfully installed setuppytest
  Cleaning up...

Test the installation

  $ cd ..  # Don''t import setuppytest.py from cwd

  $ python -m setuppytest
  setuppytest.py
  getcwd\(\): ".*\\setuppytest" (re)
  __file__: ".*\\site-packages\\setuppytest.py" (re)
  __name__: "__main__"

Test uninstallation

  $ pip uninstall -y setuppytest
  Uninstalling setuppytest:
    Successfully uninstalled setuppytest

  $ python -m setuppytest
  .*\python.exe: No module named setuppytest (re)
  [1]

testing easy-install X
----------------------

Install

  $ cd "$CWD"/setuppytest

  $ easy_install dist/setuppytest-0.1.tar.gz
  Processing setuppytest-0.1.tar.gz
  Writing .*setuppytest-0.1\\setup.cfg (re)
  Running setuppytest-0.1\\setup.py -q bdist_egg --dist-dir .*setuppytest-0.1.* (re)
  running bdist_egg
  creating .*site-packages\\setuppytest-0.1-py2.7.egg (re)
  Extracting setuppytest-0.1-py2.7.egg to .*site-packages (re)
  Adding setuppytest 0.1 to easy-install.pth file
  
  Installed .*setuppytest-0.1-py2.7.egg (re)
  Processing dependencies for setuppytest==0.1
  Finished processing dependencies for setuppytest==0.1

Test

  $ cd ..
  $ python -m setuppytest
  setuppytest.py
  getcwd\(\): ".*\\setuppytest" (re)
  __file__: ".*\\site-packages\\setuppytest-0.1-py2.7.egg\\setuppytest.py" (re)
  __name__: "__main__"

Uninstall again.

  $ pip uninstall -y setuppytest
  Uninstalling setuppytest:
    Successfully uninstalled setuppytest
  $ python -m setuppytest
  .*\python.exe: No module named setuppytest (re)
  [1]

And that''s all...
