# w20e.paywall

SETUP
=====

virtualenv
----------
    virtualenv VENV
    . ./VENV/bin/activate
    
clone from git
--------------
    git clone https://github.com/wyldebeast-wunderliebe/w20e.paywall.git
    
build
-----
    cd w20.paywall
    pip install zc.buildout
    buildout -v
    
run
---
    export FLASK_APP=
    
config overrides
----------------
    touch src/w20e/paywall/config_overrides.py
    