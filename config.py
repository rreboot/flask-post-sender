import os.path as op

basedir = op.abspath(op.dirname(__file__))


class Config(object):
    DEBUG = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + op.join(basedir, 'app/app.db')

    SECRET_KEY = 'secret_key_random_string'

    SECURITY_PASSWORD_SALT = 'password_salt_random_string'
    SECURITY_PASSWORD_HASH = 'sha512_crypt'

    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_HEIGHT = 100
    CKEDITOR_FILE_UPLOADER = 'main.upload'
    UPLOADED_PATH = op.join(basedir, 'uploads')
    CKEDITOR_LANGUAGE = 'ru'
    # CKEDITOR_FILE_BROWSER = 'main.browse'  # TODO: realize file browser
