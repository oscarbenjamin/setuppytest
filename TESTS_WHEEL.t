tests for wheel
---------------

These are separate from the other tests because they only work with pip>=1.4
which itself requires setuptools>=0.8.

Initial preparation:

  $ cd "${CWD}"

  $ if [ ! -d tmpvenv ]; then
  >     python -m virtualenv tmpvenv
  >     . tmpvenv/Scripts/activate
  >     pip install wheel
  > fi

  $ . tmpvenv/Scripts/activate

testing 'pip wheel X'
---------------------

Build a wheel

  $ cd setuppytest  # Back to the VCS root

  $ python setup.py sdist
  running sdist

  $ pip wheel dist/setuppytest-0.1.tar.gz
  Unpacking .\dist\setuppytest-0.1.tar.gz
    Running setup.py egg_info for package from file:\/\/\/.*setuppytest-0.1.tar.gz (re)
  Building wheels for collected packages: setuppytest
    Running setup.py bdist_wheel for setuppytest
    Destination directory: .*\\setuppytest\\setuppytest\\wheelhouse (re)
  Successfully built setuppytest
  Cleaning up...

Install from the wheel.

  $ pip install wheelhouse/setuppytest-0.1-py27-none-any-none-any.whl
  Unpacking .\wheelhouse\setuppytest-0.1-py27-none-any-none-any.whl
  Installing collected packages: setuppytest
  Successfully installed setuppytest
  Cleaning up...

Test the installation.

  $ pip list | grep setuppytest
  setuppytest (0.1)
  $ cd ..
  $ python -m setuppytest
  setuppytest.py
  getcwd\(\): ".*\\setuppytest" (re)
  __file__: ".*\\site-packages\\setuppytest.py" (re)
  __name__: "__main__"

And uninstall again

  $ pip uninstall -y setuppytest
  Uninstalling setuppytest:
    Successfully uninstalled setuppytest
  $ pip list | grep setuppytest
  [1]

  $ python -m setuppytest
  .*\python.exe: No module named setuppytest (re)
  [1]

  $ cd setuppytest

