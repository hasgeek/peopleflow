#: Timezone for displayed datetimes
TIMEZONE = 'Asia/Calcutta'
#: Database backend
SQLALCHEMY_DATABASE_URI = ''
#: Secret key
SECRET_KEY = 'make this something random' 
#: Folderto upload the participants list
UPLOAD_FOLDER = 'uploads/'
#: Supported extensions
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
#: LastUser server
LASTUSER_SERVER = 'https://auth.hasgeek.com'
#: LastUser client id
LASTUSER_CLIENT_ID = ''
#: LastUser client secret
LASTUSER_CLIENT_SECRET = ''
#: Mail settings
#: MAIL_FAIL_SILENTLY : default True
MAIL_SERVER = ''
#: MAIL_PORT : default 25
#: MAIL_USE_TLS : default False
#: MAIL_USE_SSL : default False
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
DEFAULT_MAIL_SENDER = 'ContactPoint <MAIL_USERNAME>'
