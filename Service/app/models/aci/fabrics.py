
import logging
from flask import jsonify, g, abort, current_app
from ..rest import (Rest, api_register)
from . import utils as aci_utils

def verify_credentials(fabric):
    """ check that current APIC credentials are valid """
    import os
    Rest.authenticated()

    ret = {
        "error": "Not tested",
        "success": False,
    }
    def fail(apic=""):
        if len(apic)>0: ret["error"] = apic
        return jsonify(ret)

    # verify valid configuration in settings
    fab = Fabrics.load(fabric=fabric)
    if not fab.exists(): return fail(apic="Fabric %s not found" % fabric)
    if current_app.config["ACI_APP_MODE"] and len(fab.apic_cert)>0:
        if not os.path.exists(fab.apic_cert):
            return fail(apic="Certificate file not found")
    elif len(fab.apic_password) == 0:
        # password requried in non-cert mode
        return fail(apic="No apic password configured")
    if len(fab.apic_username)==0:
        return fail(apic="No apic username configured")

    # connect to the APIC
    session = aci_utils.get_apic_session(fabric)
    if session is None: return fail(apic="Failed to connect to APIC")
    session.close()
    ret["success"] = True
    ret["error"] = ""

    # use this test to set cluster_ips within ACI_Fabric object ?
    return jsonify(ret)


def update_apic_controllers(fabric):
    """ connect to apic and get list of other active controllers in cluster and
        add them to fabric settings cluster_ips.  For simplicity, will add only
        IPv4 oob and inb mgmt addresses (if not 0) with preference for oob.
    """
    ret = {"error": "Not tested","success": False}
    def fail(msg=""):
        if len(msg)>0: ret["error"] = msg
        return jsonify(ret)
        
    f = Fabrics.load(fabric=fabric)
    if not f.exists(): return fail("fabric %s does not exists in db" % fabric)

    session = aci_utils.get_apic_session(fabric)
    if session is None: return fail("unable to connect to apic")
   
    objects = aci_utils.get_class(session, "topSystem")
    if objects is None: return fail("unable to read topSystem")

    try:
        controllers = []
        for o in objects:
            attr = o.values()[0]["attributes"]
            if "role" in attr and attr["role"] == "controller":
                if "state" in attr and attr["state"] == "in-service":
                    if "oobMgmtAddr" in attr and attr["oobMgmtAddr"]!="0.0.0.0":
                        if attr["oobMgmtAddr"] not in controllers:
                            controllers.append(attr["oobMgmtAddr"])
                    if "inbMgmtAddr" in attr and attr["inbMgmtAddr"]!="0.0.0.0":
                        if attr["inbMgmtAddr"] not in controllers:
                            controllers.append(attr["inbMgmtAddr"])
        if len(controllers) == 0:
            return fail("unable to find any additional controllers")

        # update database with new controller info
        if f.controllers != controllers:
            f.controllers = controllers
            if not f.save():
                return fail("unable to save result to database")
                
    except Exception as e:
        return fail("unexpected error: %s" % e)

    ret["error"] = ""
    ret["success"] = True
    return jsonify(ret)

@api_register(path="/aci/fabrics")
class Fabrics(Rest):
    """ ACI Fabrics REST class """

    logger = logging.getLogger(__name__)
    # meta data and type that are exposed via read/write 
    META_ACCESS = {
        "routes": [
            {
                "path": "verify",
                "keyed_url": True,
                "methods": ["POST"],
                "function": verify_credentials
            },
            {
                "path": "controllers",
                "keyed_url": True,
                "methods": ["POST"],
                "function": update_apic_controllers
            },
        ]
    }
    META = {
        "fabric":{
            "key": True,
            "type":str, 
            "default":"", 
            "regex":"^[a-zA-Z0-9\-\.:_]{1,64}$",
        },
        "apic_username":{
            "type":str, 
            "default":"admin",
            "regex":"^[a-zA-Z0-9\-_\.@]{1,128}$"
        },
        "apic_password":{
            "type": str, 
            "default": "",
            "read": False,
            "encrypt": True,
        },
        "apic_hostname":{
            "type":str, 
            "default":"",
        },
        "apic_cert": {
            "type":str,
            "default":"",
        },
        # dynamically discovered inband/outofband address
        "controllers": {
            "type":list,
            "subtype": str,
            "write": False,
        },
    }




