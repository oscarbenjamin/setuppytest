#!/bin/sh

set -o errexit

# Run test.sh against all versions of setuptools and pip
setuptools_versions="\
1.1.3   \
1.1.2   \
1.1.1   \
1.1     \
1.0     \
0.9.8   \
0.9.7   \
0.9.6   \
0.9.5   \
0.9.4   \
0.9.3   \
0.9.2   \
0.9.1   \
0.9     \
0.8     \
0.7.8   \
0.7.7   \
0.7.6   \
0.7.5   \
0.7.4   \
0.7.3   \
0.7.2   \
0.7.1   \
0.7     \
"

pip_versions="\
1.4.1   \
1.4     \
1.3.1   \
1.3     \
1.2.1   \
1.2     \
1.1     \
1.0.2   \
1.0.1   \
1.0     \
0.8.3   \
0.8.2   \
0.8.1   \
0.8     \
0.7.2   \
0.7.1   \
0.6.1   \
0.6     \
0.5     \
0.4     \
0.3     \
"

venvdir="tmpvenv"

for sver in $setuptools_versions; do
    for pver in $pip_versions; do

        echo Setuptools version: $sver
        echo Pip version:        $pver
        
        # Can we build wheels with these versions?
        export NO_WHEEL=0
        if [ "$pver" \< "1.4" ]; then
            export NO_WHEEL=1
        fi
        if [ $sver \< "0.8" ]; then
            export NO_WHEEL=1
        fi

        # First create a virtalenv with the appropriate setuptools/pip/wheel
        # versions.
        if [ -d "$venvdir" ]; then
            rm -r "$venvdir"
        fi
        python -m virtualenv -q --no-site-packages --no-pip --no-setuptools \
                "$venvdir" &> /dev/null
        cd "$venvdir"
            wget -q --no-check-certificate \
            https://pypi.python.org/packages/source/s/setuptools/setuptools-${sver}.tar.gz\
                    &> /dev/null

            tar -xzf setuptools-${sver}.tar.gz
            cd setuptools-$sver
                ../Scripts/python setup.py install &> /dev/null
            cd ..
            wget -q --no-check-certificate \
            https://pypi.python.org/packages/source/p/pip/pip-${pver}.tar.gz \
                    &> /dev/null
            tar -xzf pip-${pver}.tar.gz
            cd pip-$pver
                ../Scripts/python setup.py install &> /dev/null
            cd ..
            if [ "$NO_WHEEL" -eq "0" ]; then
                Scripts/pip install wheel > /dev/null
            fi
        cd ..

        # Now run the tests from the VCS root.
        ./test.sh
    done
done
