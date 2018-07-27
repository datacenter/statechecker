
import logging
from ..rest import (Rest, api_register)

# shared force string to lower formatter function
def lower(v): return v.lower()

@api_register(path="/aci/mo")
class ManagedObjects(Rest):
    """ ACI ManagedObject model 

    classname   Each object corresponds to a specific class. 

    description the description of classname

    uri         During collection a class query is performed for the objects.
                Some objects (such as stat objects) cannot use the general
                class uri so a custom uri can be provided

    pseudo      boolean, if true this managed object references a pseudo class
                (which may be one or more classes). A custom analyzer is
                required for pseudo MO and also contains a list of classnames
                or uri's required during snapshot collection

    severity    Each attribute can have a severity for use to filter on
                more/less important objects. The default is notice

    key         For each object, the 'key' used for comparision defaults to the
                'dn' attribute.  This can be overriden with 'key' setting

    analyzer    specify specific analyzer function for object comparision
                supported analyzers definied in Definitions.ANALYZERS

    labels      Various filtering and comparision manipulation is handled on a
                per object basis via labels associated with the object. This
                option is a list of strings.  The following strings are
                currently supported:

                    dynamic     used to indicate value is hardware allocated or
                                and may be suscceptible to changing when the
                                object is reprogrammed or on reload. This is
                                also applicable for values that intermittently
                                change without impact to the state such as TCP
                                port numbers on socket objects

                    statistic   statistics are expected to change between
                                snapshots and by default are not compared.
                                This is slightly different from 'dynamic' as
                                statisic objects generally increase. User can
                                choose whether statistic objects/attributes are
                                included at snapshot comparision

                    list        attributes that are a list of comma separated 
                                values. During comparison, each value in the 
                                list is individually checked for the existing of 
                                the same value in the other compared attribute.
                                For now, repeated values are ignored...
            
                    list-expand similar to 'list' label for an attribute but
                                the list will be comma separated integers that
                                need to be expanded.  For example:
                                    5,7,10-110,221

                    timestamp   any attribute matching TIMESTAMP_REGEX
                                is assumed to be a timestamp but definition can
                                tag additional attributes with this label

                    no-timestamp    force attribute not to be treated as a
                                timestamp

                    no-key      for objects (such as statistic objects) where
                                only a single instance exists and there's no
                                'key' attribute. In this scenario, the first
                                object found for class is compared (per-node).

    include     List of attributes to include in comparison. By default all
                attributes are compared. By setting this field, it is assumed
                that all other attributes should be ignored

    exclude     List of attributes to exclude in comparision. If both include
                and exclude are provided (not empty list), then include will
                be used

    remap       list of remap keywords.  This is required for objects with key
                or other attributes that may change value on reprogramming. For
                example, a vlan id for a BD can be different if the BD is 
                reprogrammed.  For comparision, the vlan id needs to be 
                remapped based on VNID value for proper comparision between
                snapshots.
                If remap is provided for an object, it applies to the key. It
                can also be used on a per-attribute basis to remap the value of
                the attribute.
                The following mapping functions are available:
                    
                    all     perform remap for all known remapping functions

                    vlan    remap key with vlan to VNID of corresponding BD or
                            EPG. This substitues following values with VNID:
                                [vlan#]
                                ^vlan#$
                                ^vlan#,
                                ,vlan#$
                            requires vlanCktEp and l2BD

                    agg     remap key of aggregation (port-channel id) to name
                            requires pcAggrIf

                    encrtd  remap key to name if present or concatenation of 
                            encap and routed interface for switch
                            (need to test on E+ release with routed PC)
                            requires l3EncRtdIf

                    loopback    remap key for loopback based on ipv4If/ipv6If
                            objects where a unique loopback is defined as 
                            ipv4If(mode)+ipv6If(mode)+context 
                            requires l3LbRtdIf, ipv4If, ipv6If

                    tunnel  remap key of tunnel to concatenation of source and
                            destination IP address
                            requires tunnelIf
    """

    logger = logging.getLogger(__name__)

    # custom analyzers for object comparision
    ANALYZERS = {
        # empty string is same as 'default'
        "": {},
        # default analyzer
        "default": {},
        # used by REQUIRED_MANAGED_OBJECTS when collecting dependent objects
        # but skipping analysis for them
        "exclude": {},  
        "acls": {
            "classnames": ["actrlRule", "actrlEntry"],
        },
        "endpoints": {
            "classnames": ["epmIpEp", "epmMacEp", "epmRsMacEpToIpEpAtt"],
        },
    }

    # severity int mapping
    SEVERITY = {
        "debug":    10,
        "info":     20,
        "notice":   30,
        "warn":     40,
        "error":    50,
        "critical": 60,
    }

    # default timestamp regex
    TIMESTAMP_REGEX = "(T[SsMm]$)|(lastTran)|[Tt]ime$"

    # reusable meta for remap, labels, and severity
    severities = {
        "type": str,
        "formatter": lower,
        "values": ["debug", "info", "notice", "warn", "error","critical"],
        "default": "notice"
    }
    remap = {
        "type": list,
        "subtype": str,
        "formatter": lower,
        "values": ["all", "vlan", "agg", "encrtd", "loopback","tunnel"],
    }
    labels = {
        "type": list,
        "subtype": str,
        "formatter": lower,
        "values": ["dynamic", "statistic", "timestamp", "no-timestamp", 
                    "no-key", "list", "list-expand"],
    }

    META_ACCESS = {
        "create": False,
        "update": False,
        "delete": False,
    }

    META = {
        "classname":{
            "type": str,
            "regex": "^[a-zA-Z0-9]{4,256}$",
            "key": True,
        },
        "description":{
            "type": str,
            "regex": "^(.|[\r\n]){2,8192}$",
            "description": "user friendly description of classname",
        },
        "pseudo": {
            "type": bool,
            "default": False,
            "description": """ this managed object references a pseudo class
                (which may be one or more classes). A custom analyzer is
                required for pseudo MO and also contains a list of classnames
                or uri's required during snapshot collection
            """,
        },
        "analyzer": {
            "type":str, 
            "default":"",
            "values": ANALYZERS,
        },
        "uri": {},
        "key": {
            "type": str, 
            "default":"dn"
        },
        "severity": severities, 
        "labels": labels,
        "remap": remap,
        "include": {"type":list,"subtype": str},
        "exclude": {"type":list,"subtype": str},
        "attributes": {
            "type": list,
            "subtype": dict,
            "meta":{
                "name": {"type": str, "default": ""},
                "severity": severities,
                "labels": labels,
                "remap": remap,
            },
        },
    }

    @staticmethod
    def severity_match(sev1, sev2):
        """ compare string severity 1 to severity 2. If severity 2 is greater 
            than or equal to severity 1 then return true
        """
        sev1 = ManagedObjects.SEVERITY.get(sev1, 0)
        sev2 = ManagedObjects.SEVERITY.get(sev2, 0)
        return sev2 >= sev1


