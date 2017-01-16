from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('w20e.paywall.settings')
app.config.from_pyfile('settings_overrides.py')
app.secret_key = app.config.get('CSRF_SECRET_KEY')
