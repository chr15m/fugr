EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "mccormix@gmail.com"
EMAIL_HOST_PASSWORD = "0hontaz2"
EMAIL_USE_TLS = True
EMAIL_PORT = 587

ADMINS = (
	("Chris McCormick", "chris@mccormickit.com"),
	("Mccormix", "mccormix+permapleat@gmail.com"),
)

DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': 'fugr',                                    # Or path to database file if using sqlite3.
                'USER': 'fugr',                                       # Not used with sqlite3.
                'PASSWORD': 'f00g3r',                           # Not used with sqlite3.
                'HOST': '',                                       # Set to empty string for localhost. Not used with sqlite3.
                'PORT': '',                                       # Set to empty string for default. Not used with sqlite3.
        }
}

SECRET_KEY = "dev-booyah!"
