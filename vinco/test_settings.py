from .settings import *

# Override the database configuration from settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Use memory storage for files during tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Disable password hashing to speed up tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Turn off debugging for tests
DEBUG = False
