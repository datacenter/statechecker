from flask import Flask, g, abort
from flask_pymongo import PyMongo
from flask_login import (LoginManager, login_required, login_user, 
    current_user, logout_user)
from flask import request, make_response, render_template, jsonify
import re

def get_app_config(config_filename="config.py"):
    # returns only the app.config without creating full app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config")
    # pass if unable to load instance file
    try: app.config.from_pyfile(config_filename) 
    except IOError: pass
    # import private config when running in APP_MODE
    try: app.config.from_pyfile("/home/app/config.py", silent=True)
    except IOError: pass
    return app.config

def create_app(config_filename="config.py"):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config")
    # pass if unable to load instance file
    try: app.config.from_pyfile(config_filename)
    except IOError: pass
    # import private config when running in APP_MODE
    try: app.config.from_pyfile("/home/app/config.py", silent=True)
    except IOError: pass

    # register dependent applications
    app.mongo = PyMongo(app)

    # import model objects (which auto-register with api)
    from .models.settings import Settings
    from .models.users import Users
    from .models.rest.swagger.docs import Docs
    from .models.aci.fabrics import Fabrics
    from .models.aci.definitions import Definitions
    from .models.aci.managed_objects import ManagedObjects
    from .models.aci.snapshots import Snapshots
    from .models.aci.app_status import AppStatus
    from .models.aci.compare import (Compare, CompareResults)

    # auto-register api objects
    from .views.api import api
    from .models.rest import register
    register(api, uni=False)

    # register blueprints
    from .views.auth import auth
    from .views.base import base
    from .views.doc import doc
    app.register_blueprint(base)
    app.register_blueprint(auth) # auth has fixed url_prefix
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(doc, url_prefix="/docs")

    # register error handlers
    register_error_handler(app)
    
    # if cors is enabled, add to entire app
    if app.config.get("ENABLE_CORS", False):
        from flask_cors import CORS
        CORS(app, supports_credentials=True, automatic_options=True)

    return app


def register_error_handler(app):    
    """ register error handler's for common error codes to app """
    def error_handler(error):
        code = getattr(error, "code", 500)
        # default text for error code
        text = {
            400: "Invalid Request",
            401: "Unauthenticated",
            403: "Forbidden",
            404: "URL not found",
            405: "Method not allowed",
            500: "Internal server error",
        }.get(code, "An unknown error occurred")

        # override text description with provided error description
        if error is not None and hasattr(error, "description") and \
            len(error.description)>0:
            text = error.description

        # return json for all errors for now...
        return make_response(jsonify({"error":text}), code)

    for code in (400,401,403,404,405,500):
        app.errorhandler(code)(error_handler)

    return None

def basic_auth():
    """ basic authentication that can be provided to admin-only blueprints
        that aborts on error else returns None
    """
    g.user = current_user
    if g.user is not None:
        if hasattr(g.user, "is_authenticated") and hasattr(g.user, "role"):
            if g.user.is_authenticated and g.user.role == g.ROLE_FULL_ADMIN:
                return
    abort(403, "")

