
import logging
from flask import abort
from ..rest import (Rest, api_register)
from .managed_objects import ManagedObjects

def check_all_mo_exist(mos):
    """ ensure all objects in provided list has existing managedObject
        abort with 400 error if the object does not exist
    """
    # for list of MOs ensure they each exist. since MOs are static it's better
    # to read all ManagedObjects and then cross reference against provided list
    all_mos = ManagedObjects.read()
    all_mos = [ o["classname"] for o in all_mos["objects"] ]
    for cn in mos:
        if cn not in all_mos:
            abort(400, "unknown managed_object classname '%s'" % cn)

def before_definition_create(data, **kwargs):
    # ensure that all managed objects in new definition exist
    check_all_mo_exist(data["managed_objects"])
    return data

def before_definition_update(filters, data, **kwargs):
    # ensure that all managed objects in definition update exist
    if "managed_objects" in data:
        check_all_mo_exist(data["managed_objects"])
    return (filters, data)

def before_definition_delete(filters, **kwargs):
    obj = Definitions.load(_filters = filters , **kwargs)
    if obj.template == True:
        abort( 400, "Cannot delete a predefined template")
    return filters

@api_register(path="/aci/definitions")
class Definitions(Rest):
    """ ACI Definition model """

    logger = logging.getLogger(__name__)
    
    META_ACCESS = {
        "before_create": before_definition_create,
        "before_update": before_definition_update,
        "before_delete": before_definition_delete
    }

    META = {
        "definition": {
            "type": str,
            "default": "default",
            "key": True,
            "key_index": 0,
            "regex":"^[a-zA-Z0-9\-\.:_]{1,64}$",
            "description": "unique identifier for definition object",
        },
        "description":{
            "type": str,
            "regex": "^(.|[\r\n]){1,8192}$",
            "description": "definition description",
        },
        "managed_objects":{
            "type": list,
            "subtype": str,
            "regex": "^[a-zA-Z0-9]{4,256}$",
            "description": """
            list of managed objects (classes) compared in this definition
            """,
        },
        "template":{
            "type": bool,
            "default": False,
            "write": False,
            "description": "template definitions are statically defined and cannot be changed by the user"
        }
    }

    def get_managed_objects(self, include_description=False):
        """ get full dict representation of all managed objects definied under
            this definition. Result is returned as a dict indexed by MO
            classname.  By default the description is excluded from the MO
        """
        all_mos = ManagedObjects.read()
        indexed = {}
        for o in all_mos["objects"]: 
            if o["classname"] in self.managed_objects:
                if not include_description: o.pop("description", None)
                indexed[o["classname"]] = o
        return indexed

        
