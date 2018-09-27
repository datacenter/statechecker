
from . rest import api_register
from . rest import api_route
from . rest import Rest

from flask import abort
from flask import current_app
from flask import jsonify

import logging
import os

logger = logging.getLogger(__name__)

@api_register(path="/aci/app-status")
class AppStatus(Rest):
    META_ACCESS = {
        "read": False,
        "create": False,
        "update": False,
        "delete": False,
    }
    META = {
        "version": {
            "reference": True,
            "type": dict,
            "description": "app version information",
            "meta": {
                "version": {
                    "type": str,
                    "description": "app version",
                },
                "commit": {
                    "type": str,
                    "description": "git commit hash",
                },
                "date": {
                    "type": str,
                    "description": "ISO timestamp of git commit"
                },
                "timestamp": {
                    "type": float,
                    "description": "EPOCH timestamp of git commit",
                },
                "branch": {
                    "type": str,
                    "description": "branch name of git commit",
                },
                "author": {
                    "type": str,
                    "description": "author email of git commit",
                },
            },
        },
    }

    @staticmethod
    @api_route(path="/", methods=["GET"], authenticated=False, swag_ret=["success", "error"])
    def api_check_status():
        """ check the startup status of the app. A 500 error may occur if the webserver is not 
            running or app is not ready.  A 503 service unavailable is return if not ready with an
            error description
        """
        (success, status) = AppStatus.check_status()
        if success: return jsonify({"success": True})
        abort(503, status)

    @staticmethod
    def check_status():
        """ check status and return tuple (bool, description) where bool is True if running """
        status = ""
        if os.path.exists(current_app.config["ACI_STARTED_FILE"]):
            logger.debug("application started flag is set")
            return (True, "started")
        logger.debug("application started flag not found, checking for status")
        if os.path.exists(current_app.config["ACI_STATUS_FILE"]):
            try:
                with open(current_app.config["ACI_STATUS_FILE"], "r") as f:
                    status = f.read()
                    logger.debug("application status: %s" % status)
            except Exception as e:
                logger.debug("failed to open status file: %s" % e)
        else:
            logger.debug("application status flag not found")
            status = "not-ready"
        return (False, status)

    @staticmethod
    @api_route(path="/version", methods=["GET"], authenticated=False, swag_ret=["version"])
    def get_version():
        """ get app version and build info """
        return jsonify({
            "version": current_app.config.get("APP_VERSION", "-"),
            "commit": current_app.config.get("APP_COMMIT", ""),
            "date": current_app.config.get("APP_COMMIT_DATE", ""),
            "timestamp": current_app.config.get("APP_COMMIT_DATE_EPOCH", 0),
            "branch": current_app.config.get("APP_COMMIT_BRANCH", ""),
            "author": current_app.config.get("APP_COMMIT_AUTHOR", ""),
        })
        
