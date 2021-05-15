#!/usr/bin/env bash
python3 setup.py clean sdist bdist_wheel
pip install -U "dist/$(bash -c 'ls -1rth dist | tail -1')"
