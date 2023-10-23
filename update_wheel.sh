#! /bin/bash

cd ~/repos/github/quimera-ps
rm dist/*
rm -Rf build/*
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
sudo -H pip3 install --upgrade quimeraps
sudo -H pip3 install --upgrade quimeraps