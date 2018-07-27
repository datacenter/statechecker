
from flask import current_app, Blueprint, render_template
auth_prefix = "/auth"
auth = Blueprint("auth", __name__, url_prefix=auth_prefix)

from flask import Flask, jsonify, flash, redirect
from flask import request, make_response, g, abort
from flask_login import (LoginManager, login_required, current_user)

from ..models.users import Users
from ..models.rest import Role
from ..models.utils import MSG_403, get_user_data
import logging, re

# module level logging
logger = logging.getLogger(__name__)

# setup login manager
login_manager = LoginManager()

# since this is a blueprint, use record_once instead of login_manager.init_app
@auth.record_once
def on_load(state):
    login_manager.login_view = "%s/login/" % auth_prefix
    login_manager.login_message = ""
    login_manager.init_app(state.app)

@auth.before_app_request
def before_request():
    # force everything over HTTPS if enabled
    if current_app.config.get("force_https", False):
        fwd_proto = request.headers.get("x-forwarded-proto",None)
        if fwd_proto is not None:
            if fwd_proto.lower() == "http":
                return redirect(request.url.replace("http:","https:", 1))
        else:
            if re.search("^http:", request.url) is not None:
                return redirect(request.url.replace("http:","https:", 1))

    # set global object various configs
    g.app_name = current_app.config.get("app_name", "AppName1")

    # set global object 'g.user' based off current user session
    g.ROLE_FULL_ADMIN = Role.FULL_ADMIN
    g.user = current_user
    if g.user is not None:
        if hasattr(g.user, 'role') and g.user.role == Role.BLACKLIST:
            Users.logout()
            abort(403, MSG_403)
        elif not current_app.config.get("LOGIN_ENABLED", True) and \
            (g.user.is_authenticated is False):
            # auto-login user as local if login is disabled
            Users.login("local", "password", force=True)
            g.user = Users.load(username="local")

@login_manager.user_loader
def load_user(username):
    u = Users.load(username=username)
    if not u.exists(): return None
    return u

