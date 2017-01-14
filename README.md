# w20e.paywall

A proof of concept paywall mechanism using the online payment platform [Mollie](https://www.mollie.com/nl/).

requirements
------------

* Flask
* requests
* redis
* mollie-api-python

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
    touch src/instance/config_overrides.py
    
Use config_overides.py for environment specicic configuration adjustments.

mod_wsgi snippet
----------------

    WSGIDaemonProcess paywall user=app-paywall-prd group=app-paywall-prd threads=5
    WSGIScriptAlias / /opt/APPS/paywall/prd/w20e.paywall/parts/wsgiscript/paywall.wsgi

    <Directory /opt/APPS/paywall/prd/w20e.paywall>
        WSGIProcessGroup paywall
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
    
The paywall.wsgi script was created by buildout.
