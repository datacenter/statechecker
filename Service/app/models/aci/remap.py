
import re, json
import logging
from ..utils import pretty_print

# set sorted as natsort if available
try: from natsort import natsorted as sorted
except ImportError as e: pass

# module level logging
logger = logging.getLogger(__name__)

class Remap(object):

    # required objects for compare remapping
    REQUIRED_MANAGED_OBJECTS = [
        "vlanCktEp",
        "l2BD",
        "pcAggrIf",
        "l3EncRtdIf",
        "l3LbRtdIf",
        "ipv4If",
        "ipv6If",
        "tunnelIf",
    ]
    _vlan = [
        "\[vlan[0-9]+\]",
        "^vlan[0-9]+,?$",
        ",vlan[0-9]+$",
        "^vlan-[0-9]+$",
        "^[0-9]+$",
    ]
    _vlan = "|".join(["(%s)"%v for v in _vlan])
    _encrtd = [
        "eth[0-9]+/[0-9]+\.[0-9]+",
        "po[0-9]+\.[0-9]+"
    ]
    _encrtd = "|".join(["(%s)"%v for v in _encrtd])
    REMAP_ORDERED = ["vlan", "encrtd", "agg", "loopback", "tunnel"]
    REMAP_REGEX = {
        "vlan": re.compile("(?P<v>%s)"%_vlan),
        "encrtd": re.compile("(?P<v>%s)"%_encrtd),
        "agg": re.compile("(?P<v>po[0-9]+)"),
        "loopback": re.compile("(?P<v>lo[0-9]+)"),
        "tunnel": re.compile("(?P<v>tunnel[0-9]+)"),
    }

    def __init__(self, node_id, folder=None):
        """ receive node_id and folder containing extracted snapshot objects 
            to build remap.  If folder is not provided then instaniate empty
            remaps (i.e., remapping is disabled)
        """
        self.node_id = node_id
        self.folder = folder
        self.vlans = {}
        self.aggs = {}
        self.encrtds = {}
        self.loopbacks = {}
        self.tunnels = {}
        self.remaps = {}   
        self.disabled = True
        if folder is not None:
            self._remap_vlan()
            self._remap_agg()
            self._remap_encrtd()
            self._remap_loopback()
            self._remap_tunnel()
            self.remaps = {
                "vlan": [ Remap.REMAP_REGEX["vlan"], self.vlans ],
                "encrtd": [ Remap.REMAP_REGEX["encrtd"], self.encrtds],
                "agg": [ Remap.REMAP_REGEX["agg"], self.aggs ],
                "loopback": [ Remap.REMAP_REGEX["loopback"], self.loopbacks ],
                "tunnel": [ Remap.REMAP_REGEX["tunnel"], self.tunnels ],
            }
            self.disabled = False

    def remap_attribute(self, value, mo_remaps=[]):
        """ remap provided value according remap selectors 

        """
        if len(mo_remaps)==0: return value
        dmsg = "remap %s to " % value
        allset = "all" in mo_remaps
        #logger.debug("remap(%s) %s" , mo_remaps, value)
        for r in self.REMAP_ORDERED:
            if allset or r in mo_remaps:
                t = self.remaps[r]
                r1 = t[0].search(value)
                if r1 is not None:
                    match = re.sub("[\[\]\,]","",r1.group("v"))
                    if match in t[1]:
                        #logger.debug("matching(%s) %s",match,t[1][match])
                        value = t[0].sub(t[1][match], value)
                
        #logger.debug("%s %s" ,dmsg, value)
        return value

    @staticmethod
    def get_object_attributes(fname, classname=None):
        """ return list of object attributes from json file for corresponding
            classname.  If no classname is provided then extract classname
            from file <path>/<classname>.json
        """
        if classname is None:
            classname = re.sub("\.json$","", fname.split("/")[-1])
        logger.debug("get object attributes for %s from %s"%(classname,fname))
        objects = []
        try:
            with open(fname, "r") as f:
                js = json.load(f)
                for o in js:
                    if classname in o and \
                        "attributes" in o[classname]:
                        objects.append(o[classname]["attributes"])
        except Exception as e:
            logger.info("failed to get objects from %s: %s" % (fname,e))
        return objects

    @staticmethod
    def get_per_classname_object_attributes(fname):
        """ return dict of all object attributes from json file indexed by
            classname.  I.e., support multiple classnames within the file and
            return the corresponding attributes for each classname
        """
        ret = {}
        logger.debug("get all object attributes from %s" % (fname))
        try:
            with open(fname, "r") as f:
                js = json.load(f)
                for o in js:
                    if type(o) is dict and len(o)>0:
                        classname = o.keys()[0]
                        if type(o[classname]) is dict and \
                            "attributes" in o[classname]:
                            if classname not in ret: ret[classname] = []
                            ret[classname].append(o[classname]["attributes"])
        except Exception as e:
            logger.info("failed to get objects from %s: %s" % (fname, e))
        logger.debug("returning classes: %s" % ret.keys())
        return ret


    def _remap_vlan(self):
        """ build vlan remap by building dict of vlan id to VNID for EPGs and
            BDs.  
            requires vlanCktEp and l2BD
        """
        fds=Remap.get_object_attributes("%s/%s.json"%(self.folder,"vlanCktEp"))
        bds=Remap.get_object_attributes("%s/%s.json"%(self.folder,"l2BD"))
        for o in fds+bds:
            if "id" in o and "fabEncap" in o:
                k = "vlan%s" % o["id"]
                if k not in self.vlans: 
                    self.vlans[k] = o["fabEncap"]
                else:
                    logger.warn("%s duplicate vlan id %s (%s and %s)" % (
                        self.node_id, k, self.vlans[k], 
                        o["fabEncap"]))

    def _remap_agg(self):
        """ build port-channel (agg) remap by mapping agg id to name.
            requires pcAggrIf
        """
        agg=Remap.get_object_attributes("%s/%s.json"%(self.folder,"pcAggrIf"))
        for o in agg:
            if "id" in o and "name" in o:
                if o["id"] not in self.aggs: self.aggs[o["id"]] = o["name"]
                else:
                    logger.warn("%s duplicate agg id %s (%s and %s)" % (
                        self.node_id, o["id"], self.aggs[o["id"]], 
                        o["name"]))

    def _remap_encrtd(self):
        """ build sub-interface (encRtd) remap by mapping id to EITHER 
            interface number plus vlan encap OR (for port-channels) name and 
            vlan encap
            requires l3EncRtdIf

            NOTE, for some reason APIC uses same id (po1.ENCAP) for both 
            bond0 and bond1.  For now, will not build remap for APICs
        """
        if int(self.node_id) < 32: return   # skip APIC remap
        enc=Remap.get_object_attributes("%s/%s.json"%(self.folder,"l3EncRtdIf"))
        for o in enc:
            if "id" in o and "encap" in o and "name" in o:
                r1 = re.search("^(?P<if>eth[0-9]+/[0-9]+)\.[0-9]+", o["id"])
                if r1 is not None:
                    v = "%s.%s" % (r1.group("if"), o["encap"])
                elif len(o["name"])>0 and re.search("^po[0-9]+", o["id"]):
                    v = "%s.%s" % (o["name"], o["encap"])
                else:
                    logger.warn("%s cannot map l3EncRtdIf %s"%(self.node_id,o))
                    continue
                #logger.debug("map %s to %s" % (o["id"], v))
                if o["id"] not in self.encrtds: self.encrtds[o["id"]] = v
                else:
                    logger.warn("%s duplicate encrtd id %s (%s and %s)" % (
                        self.node_id, o["id"], self.encrtds[o["id"]], v))

    def _remap_loopback(self):
        """ build loop l3LbRtdIf id to vrf:ipv4If(mode). Right now, no ipv6 
            control loopbacks so a loopback is limited to user vrf. However, for
            overlay loopbacks can be uniquely allocated for functions
            requires l3LbRtdIf
        """
        # first get list of loopbacks that we care about and parse vrf
        lo=Remap.get_object_attributes("%s/%s.json"%(self.folder,"l3LbRtdIf"))
        loopbacks = {}
        reg = "sys/(inst|ctx)-(?P<vrf>(overlay-1)|(\[vxlan-[0-9]+\]))/"
        reg = re.compile(reg)
        for o in lo:
            if "id" in o and "dn" in o:
                r1 = reg.search(o["dn"])
                if r1 is not None:
                    loopbacks[o["id"]] = re.sub("\[|\]","",r1.group("vrf"))
                else:
                    logger.warn("%s failed to parse loopback dn %s" % (
                        self.node_id, o["dn"]))

        # second get list of ipv4If to get mode for each loopback and add to 
        # final self.loopbacks dict
        lo=Remap.get_object_attributes("%s/%s.json"%(self.folder,"ipv4If"))
        for o in lo:
            if "id" in o and "mode" in o:
                # we only care about loopback ipv4If so if not present skip
                if o["id"] not in loopbacks: continue
                self.loopbacks[o["id"]]="%s:%s"%(loopbacks[o["id"]],o["mode"])
        
    def _remap_tunnel(self):
        """ map tunnel id to concatenation of tunnelIf src and dst IPs.
            we will also include vrf name although, at this point, tunnels are
            only created on overlay-1  (exception for multicast tunnels)
            requires tunnelIf
        """
        tn=Remap.get_object_attributes("%s/%s.json"%(self.folder,"tunnelIf"))
        for o in tn:
            if "id" in o and "src" in o and "dest" in o and "vrfName" in o:
                if o["id"] not in self.tunnels:
                    self.tunnels[o["id"]] = "%s:%s:%s" % (o["vrfName"], 
                        o["src"], o["dest"])
                else:
                    logger.warn("%s duplicate tunnel id %s (%s and %s)" % (
                        self.node_id, o["id"], self.tunnels[o["id"]], 
                        "%s:%s:%s"%(o["vrfName"],o["src"],o["dest"])))

                

RANGE_REGEX = "^ *(?P<s>[0-9]+) *- *(?P<e>[0-9]+) *$"
def expand_range(value):
    """ receive a value in form a-d,x-y,z and return list of expanded values. 
        Note, all remap functions expect strings so the expanded range will 
        also be a list of strings.
        if unable to expand range then return list with original value
    """
    try:
        result = []
        for v in list(set(value.split(","))):
            r1 = re.search(RANGE_REGEX, v)
            if r1 is None: 
                result.append(v)
                continue
            start = int(r1.group("s"))
            end = int(r1.group("e"))
            if start > end:
                for i in range(end, start+1): result.append("%d" % i)
            else:
                for i in range(start, end+1): result.append("%d" % i)
        return sorted(set(result))
    except Exception as e: 
        logger.warn("failed to expand range (%s): %s" % (value, e))
        return ["%s" % value]
