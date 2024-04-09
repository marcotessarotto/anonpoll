import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Set up django-environ
env = environ.Env(
    # Default values for variables if not set
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


s = f"""
sudo mysql

CREATE DATABASE { env('DB_NAME') } CHARACTER SET UTF8;

CREATE USER { env('DB_USER') }@localhost IDENTIFIED BY '{env('DB_PASSWORD')}';

GRANT ALL PRIVILEGES ON {env('DB_NAME')}.* TO {env('DB_USER')}@localhost;

FLUSH PRIVILEGES;


CREATE DATABASE test_{ env('DB_NAME') } CHARACTER SET UTF8;
GRANT ALL PRIVILEGES ON test_{ env('DB_NAME') }.* TO { env('DB_USER') }@localhost;
FLUSH PRIVILEGES;
"""


print(s)
