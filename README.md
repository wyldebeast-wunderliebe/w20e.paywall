# w20e.paywall

A proof of concept paywall mechanism using the microframework 
[Flask](http://flask.pocoo.org/) and the online payment platform 
[Mollie](https://www.mollie.com/nl/).

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
    
buildout
--------
    cd w20.paywall
    pip install zc.buildout
    buildout -v
    
settings overrides
------------------
Use settings_overides.py for environment specific configuration adjustments like MOLLIE_API_KEY, REDIS_HOST and CSRF_SECRET_KEY.

    touch src/instance/settings_overrides.py

fire up on development
----------------------
    export FLASK_APP=src/w20e/paywall/app.py
    ./bin/flask run
    
ngrok or serveo for localhost testing
---------------------------
Since Mollie needs to be able to reach your server (webhook_verification), you might consider using [ngrok](https://ngrok.com/) or serveo to create a secure tunnel to your localhost.

    Serveo example: ssh -R 80:localhost:5000 serveo.net

fire up on production: mod_wsgi snippet
---------------------------------------
The paywall.wsgi script gets created by buildout. Below is a mod_wsgi snippet to 
get things going on Apache.

    WSGIDaemonProcess paywall user=app-paywall-prd group=app-paywall-prd threads=5
    WSGIScriptAlias / /opt/APPS/paywall/prd/w20e.paywall/parts/wsgiscript/paywall.wsgi

    <Directory /opt/APPS/paywall/prd/w20e.paywall>
        WSGIProcessGroup paywall
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

routes
------
For starters, you can navigate the following routes.
<dl>
  <dt>[host]/<strong>manage_vouchers</strong></dt>
  <dd>Needs to be restricted in a production environment. Gives an overview of all active vouchers, both valid and not.</dd>

  <dt>[host]/<strong>test_voucher</strong></dt>
  <dd>A verify-buy-redirect chain, roundtripping the entire paywall mechanism.</dd>
  
  <dt>[host]/<strong>new_voucher</strong></dt>
  <dd>Buy a voucher using a predefined set of voucher types.</dd>
</dl>
