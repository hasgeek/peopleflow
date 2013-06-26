DEFAULT_MAIL_SENDER = 'ContactPoint <MAIL_USERNAME>'

# -*- coding: utf-8 -*-
#: Site title
SITE_TITLE = 'HasGeek App'
#: Site id (for network bar)
SITE_ID = ''
#: Google Analytics code
GA_CODE = ''
#: Google site verification code (inserted as a meta tag)
GOOGLE_SITE_VERIFICATION = ''
#: Typekit code
TYPEKIT_CODE = ''
#: Database backend
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
#: Secret key
SECRET_KEY = 'make this something random'
#: Timezone
TIMEZONE = 'Asia/Kolkata'
#: Lastuser server
LASTUSER_SERVER = 'https://auth.hasgeek.com/'
#: Lastuser client id
LASTUSER_CLIENT_ID = ''
#: Lastuser client secret
LASTUSER_CLIENT_SECRET = ''
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
DEFAULT_MAIL_SENDER = ('HasGeek', 'info@hasgeek.com')
#: Logging: recipients of error emails
ADMINS = []
#: Log file
LOGFILE = 'error.log'
UPLOAD_FOLDER = 'uploads'
STATIC_UPLOAD_FOLDER = 'peopleflow/static/uploads'