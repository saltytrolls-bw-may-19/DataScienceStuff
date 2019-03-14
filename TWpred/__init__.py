""" entry point for flask app -> <dir>:APP """
from .app import create_app

APP = create_app()
