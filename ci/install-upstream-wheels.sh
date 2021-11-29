#!/usr/bin/env bash

conda uninstall -y --force \
    numpy
# to limit the runtime of Upstream CI
python -m pip install pytest-timeout
python -m pip install \
    -i https://pypi.anaconda.org/scipy-wheels-nightly/simple \
    --no-deps \
    --pre \
    --upgrade \
    numpy
