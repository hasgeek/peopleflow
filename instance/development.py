# -*- coding: utf-8 -*-
#: Site title
SITE_TITLE = 'HasGeek People Flow'
#: Site id (for network bar)
SITE_ID = 'people flow '
#: Timezone
TIMEZONE = 'Asia/Calcutta'
#secret key
SECRET_KEY = 'people flow test secret key so it doesnt matter'
#: Database backend
SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
UPLOAD_FOLDER = 'uploads/'
#: LastUser server
#LASTUSER_SERVER = 'https://auth.hasgeek.com/'
#LASTUSER_SERVER = 'https://login.hasgeek.com/'
LASTUSER_SERVER = 'http://lastuser.local:7000'
#: LastUser client id
LASTUSER_CLIENT_ID = 'fwl4txgJR2aOxQkjf4J_pA'
#: LastUser client secret
LASTUSER_CLIENT_SECRET = 'E3oZrDNRSA6qNxRWhUjvHwxv9XO-eQTr-v8Z5kpdXUfA'
#: Typekit id
TYPEKIT_CODE = 'qhx6vtv'
#: Mail settings
#: MAIL_FAIL_SILENTLY : default True
#: MAIL_SERVER : default 'localhost'
#: MAIL_PORT : default 25
#: MAIL_USE_TLS : default False
#: MAIL_USE_SSL : default False
#: MAIL_USERNAME : default None
#: MAIL_PASSWORD : default None
#: DEFAULT_MAIL_SENDER : default None
MAIL_FAIL_SILENTLY = False
MAIL_SERVER = 'localhost'
DEFAULT_MAIL_SENDER = ('HasGeek', 'bot@hasgeek.com')
#: Logging: recipients of error emails
ADMINS = ['kiran@hasgeek.com']
#: Log file
LOGFILE = 'error.log'
