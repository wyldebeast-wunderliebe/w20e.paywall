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
    
run on development
------------------
    export FLASK_APP=w20e/paywall/app.py
    ./bin/flask run
    
config overrides
----------------
Use config_overides.py for environment specific configuration adjustments.

    touch src/instance/config_overrides.py
    
mod_wsgi snippet
----------------
The paywall.wsgi script gets created by buildout. Below a mod_wsgi snippet to get things going on Apache.

    WSGIDaemonProcess paywall user=app-paywall-prd group=app-paywall-prd threads=5
    WSGIScriptAlias / /opt/APPS/paywall/prd/w20e.paywall/parts/wsgiscript/paywall.wsgi

    <Directory /opt/APPS/paywall/prd/w20e.paywall>
        WSGIProcessGroup paywall
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
   
