"""
Compare two snapshots and save the results to database. The comparision is 
started as a background task as soon as Compare object is created. CompareResult
objects are created keyed with compare_id of corresponding Compare object. 
Once comparision is complete, application can query for corresponding 
CompareResults.
"""
from ..rest import Rest
from ..rest import api_callback
from ..rest import api_register
from ..rest import api_route
from ..utils import get_app_config
from ..utils import get_db
from ..utils import format_timestamp
from . import utils as aci_utils
from .definitions import Definitions
from .managed_objects import ManagedObjects
from .remap import Remap
from .remap import expand_range
from .snapshots import Snapshots

from flask import abort, jsonify
from multiprocessing import Pool
from multiprocessing import current_process
from natsort import natsorted as sorted
from werkzeug.exceptions import (NotFound, BadRequest)

import copy
import json
import logging
import os
import re
import shutil
import time
import traceback

# module level logging
logger = logging.getLogger(__name__)

@api_register(path="/aci/compare/results")
class CompareResults(Rest):
    """ ACI Compare Result REST class """
    logger = logging.getLogger(__name__)
    
    META_ACCESS = {
        "expose_id": True,
        "bulk_delete": True,
        "create": False,
        "update": False,
        "delete": False,
    }

    META = {
        "compare_id": {},
        "node_id": {
            "type": int
        },
        "classname": {},
        "name": {},
        "total": {
            "type": dict,
            "meta": {
                "s1": {
                    "type": int,
                    "description": "total objects from snapshot1"
                },
                "s2": {
                    "type": int,
                    "description": "total objects from snapshot2"
                },
                "created": {"type": int},
                "deleted": {"type": int},
                "modified": {"type": int},
                "equal": {"type": int},
            },
        },
        "created": {
            "type":list,
            "subtype":dict,
            "description": "list of new objects between snapshots",
        },
        "deleted": {
            "type":list,
            "subtype":dict,
            "description": "list of deleted objects between snapshots",
        },
        "modified": {
            "type":list,
            "subtype":dict,
            "description": """list of modified objects between snapshots. Note
                only changed tracked attributes that have changed are recorded.
            """
        },
        "equal": {
            "type":list,
            "subtype":dict,
            "description": "list of objects with no changes between snapshots",
        },
    }

@api_register(path="/aci/compare")
class Compare(Rest):
    """ ACI Compare REST class """

    logger = logging.getLogger(__name__)
    META_ACCESS = {
        "expose_id": True,
    }

    META = {
        "snapshot1": {
            "type":str,
            "description": "_id of first snapshot used in comparison",
            "regex":"(?i)^[0-9a-f]{24}$",
        }, 
        "snapshot2": {
            "type":str,
            "description": "_id of second snapshot used in comparison",
            "regex":"(?i)^[0-9a-f]{24}$",
        },
        "snapshot1_description": {
            "type":str,
            "description": "description of the first snapshot used in comparison",
            "write": False,
        },
        "snapshot2_description": {
            "type":str,
            "description": "description of the second snapshot used in comparison",
            "write": False,
        },
        "severity": {
            "type": str,
            "description": """ Compare only objects and attributes with 
                severities greater than or equal to provided severity """,
            "default": "info",
            "values": ManagedObjects.SEVERITY.keys(),
        },
        "remap": {
            "type": bool,
            "default": True,
            "description": """ Enable or disable remapping function when 
            comparing objects. Since multiple resources have IDs that are 
            dynamically allocated (such as VLANs and Loopback numbers), 
            performing a comparision between device reload needs to be able to
            map attributes to logical value. If no state change is expected
            between comparision, then set remap to False.
            """,
        },
        "serialize": {
            "type": bool,
            "default": True,
            "description": """ disable multiprocessing and perfom comparision
                one object and one class at a time
            """
        },
        "nodes": {
            "type": list,
            "subtype": int,
            "description": """ perform comparison on a subset of nodes instead 
            of all nodes in the snapshot. Set to an empty list (default) to 
            perform comparision on all nodes """
        },
        "definition":{
            "type":str,
            "default":"default",
            "regex":"^[a-zA-Z0-9\-\.:_]{1,64}$",
            "description": """ perform comparision only on classes specified with definition file. 
            If empty or not found all classes within the snapshots will be compared.
            """
        },
        "dynamic": {
            "type": bool,
            "default": False,
            "description": "perform comparision on dynamic attributes",
        },
        "statistic": {
            "type": bool,
            "default": False,
            "description": "include statistic values in comparision",
        },
        "timestamp": {
            "type": bool,
            "default": False,
            "description": "include timestamp attributes in comparision"
        },
        "start_time": {
            "type": float,
            "description": "unix timestamp when compare was started",
            "write": False,
        },
        "total_time": {
            "type": float,
            "description": "total time for compare to complete",
            "write": False,
        },
        "progress":{
            "type":float,
            "default": 0.0,
            "write":False,
        },
        "status":{
            "type":str,
            "default":"init",
            "values": ["init", "running", "complete", "error", "abort"],
            "write":False,
        },
        "error":{
            "type":str,
            "default":"",
            "write":False,
        },
        "total":{
            "description":"""
            total created/modified/delete count for entire comparision
            """,
            "type":dict,
            "meta":{
                "created":{"type":int},
                "modified":{"type":int},
                "deleted":{"type":int},
                "equal":{"type":int},
            },
        },
        "total_per_class":{
            "type":list,
            "write":False,
            "description":"total created/modified/delete counts per class",
            "subtype":dict,
            "meta":{
                "classname":{},
                "name":{},
                "created":{"type":int},
                "modified":{"type":int},
                "deleted":{"type":int},
                "equal":{"type":int},
            }
        },
        "total_per_node":{
            "type":list,
            "write":False,
            "description":"total created/modified/delete counts per node",
            "subtype":dict,
            "meta":{
                "node_id":{"type":int},
                "created":{"type":int},
                "modified":{"type":int},
                "deleted":{"type":int},
                "equal":{"type":int},
            }
        },
    }


    @classmethod
    @api_callback("before_create")
    def before_compare_create(cls, data):
        """ before compare create ensure snapshots exists and are from the same fabric """
        s1 = Snapshots.load(_id=data["snapshot1"])
        s2 = Snapshots.load(_id=data["snapshot2"])
        if not s1.exists(): abort(404, "snapshot1 %s not found"%data["snapshot1"])
        if not s2.exists(): abort(404, "snapshot2 %s not found"%data["snapshot2"])
    
        # set snapshot1_name and snapshot2_name
        data["snapshot1_description"] = s1.description
        data["snapshot2_description"] = s2.description

        # ensure these snapshots are for the same fabric
        if s1.fabric != s2.fabric:
            emsg = "cannot perform comparision for snapshots between different "
            emsg+= "fabrics \"%s\" and \"%s\"" % (s1.fabric, s2.fabric)
            abort(400, emsg)

        # ensure timestamp for snapshot1 < timestamp for snapshot2
        # if not swap them and allow snapshot to continue...
        if s1.start_time > s2.start_time:
            data["snapshot1"] = s2._id
            data["snapshot2"] = s1._id
        return data

    @classmethod
    @api_callback("before_delete")
    def before_compare_delete(cls, filters):
        """ delete corresponding CompareResults when deleting Compare object """
        objs = Compare.read(_filters=filters)
        if "objects" in objs:
            for o in objs["objects"]: CompareResults.delete(compare_id=o["_id"]) 
        return filters

    @classmethod
    @api_callback("after_create")
    def after_compare_create(cls, data):
        """ after compare create start comparision background task """
        c = Compare.load(_id=data["_id"])
        if not c.exists():
            abort(404, "compare (_id=%s) not found" % _id)
        c.start_compare()


    @api_route(path="restart", methods=["POST"], swag_ret=["success"])    
    def start_compare(self):
        """ start/restart compare operation """

        if self.status == "running" or self.status == "abort":
            abort(400, "compare %s currently running, send abort before restart"%(self._id))
        # set start time to 'now' before executing background worker
        self.start_time = time.time()
        self.save()
        # delete old compare results before starting/restarting background process
        CompareResults.delete(compare_id=self._id)
        if not aci_utils.execute_worker("--compare %s" % self._id):
            abort(500, "failed to start background snapshot process")
        return jsonify({"success":True})

    @api_route(path="abort", methods=["POST"], swag_ret=["success"])
    def abort_compare(self):
        """ stop/abort running compare operation """
        is_running = (self.status == "running")
        self.status = "abort"
        if not self.save(): abort(500, "failed to save abort")
        # wait until status has changed to something other than abort which indicates that the abort 
        # was successful
        max_wait_time = 120
        if is_running:
            ts = time.time()
            max_ts = ts + max_wait_time
            aborted = False
            while time.time() < max_ts:
                self.reload()
                if not self.exists() or self.status != "abort":
                    return jsonify({"success": True})
                time.sleep(1)
            msg="Failed to abort compare process after %ss. Try deleting the object..."%max_wait_time
            abort(500, msg) 
        else:
            return jsonify({"success":True})

def execute_compare(compare_id):
    """ perform comparison between two snapshots """
    logger.debug("execute compare for: %s" % compare_id)

    ts = time.time()    
    c = Compare.load(_id=compare_id)
    if not c.exists():
        logger.warn("compare object %s not found" % compare_id)
        return

    # init progress, error, status to block second process from running
    c.progess = 0.0
    c.start_time = ts
    c.total_time = 0
    c.error = ""
    c.status = "running"
    c.save()

    # delete any previous CompareResults
    CompareResults.delete(_filters={"compare_id":c._id})

    # create a working directory to extract objects
    config = get_app_config()
    tmp = config.get("TMP_DIR", "/tmp/")
    tmp = "%s/compare.%s.%s" % (tmp, c._id, int(ts)) 
    
    # update state with error message and error status
    def fail(msg="", cleanup=True):
        if len(msg)>0: c.error = msg
        c.status = "error"
        c.total_time = abs(time.time() - ts)
        logger.debug("compare %s failed: %s" % (c._id, c.error))
        if not c.save(): logger.warn("failed to save compare %s state"%c._id)
        if cleanup: tmp_cleanup()
        return

    # clean up working directory
    def tmp_cleanup():
        if os.path.isdir(tmp):
            logger.debug("cleanup directory %s" % tmp)
            try: shutil.rmtree(tmp)
            except Exception as e: 
                logger.warn("failed to cleanup directory(%s): %s"%(tmp,e))
        else: logger.debug("cleanup directory %s not found" % tmp)

    # update snapshot progress percentage
    def progress(i, total):
        abort_compare() # check for abort signal before progress update
        if total>0: p = round(i/(1.0*total), 2)
        else: p = 0
        if p > 1: p = 1
        c.progress = p
        c.total_time = abs(time.time() - ts)
        if not c.save(): logger.warn("failed to save compare %s state"%c._id)
        logger.debug("progress %s/%s = %s" % (i, total, p))
        return

    # user can force compare execution to stop by deleting the object
    # abort_compare is checked at a regular interval.  If compare was deleted
    # then perform cleanup and return True, else return False
    def abort_compare():
        _s = Compare.load(_id=c._id)
        if not _s.exists() or _s.status == "abort":
            logger.debug("compare object %s has been aborted"%c._id)
            tmp_cleanup()
            raise Exception("compare operation %s aborted" % c._id)

    # return dict representation of json in provided filename
    def get_json_data(fname):
        with open(fname, "r") as f:
            return json.load(f)

    # load snapshot1 (s1) and snapshot2 (s2) along with definition in compare object
    s1 = Snapshots.load(_id=c.snapshot1)
    s2 = Snapshots.load(_id=c.snapshot2)
    d = Definitions.load(definition=c.definition)
    classnames = []
    if not s1.exists(): return fail("snapshot %s not found" % c.snapshot1)
    if not s2.exists(): return fail("snapshot %s not found" % c.snapshot2)
    if not s1.status=="complete": 
        return fail("snapshot %s not complete"%c.snapshot1)
    if not s2.status=="complete":
        return fail("snapshot %s not complete"%c.snapshot2)
    if not d.exists(): 
        logger.debug("unknown definition provided in compare request: '%s'", c.definition)
    else:
        classnames = d.get_managed_objects()

    try:
        # create tmp directory for extracting files
        if os.path.exists(tmp):
            return fail("tmp directory already exists: %s"%tmp, cleanup=False)
        logger.debug("make directory: %s" % tmp)
        os.makedirs(tmp)

        # extract snaphots to tmp directories
        for index, s in enumerate([s1, s2]):
            td = "%s/%s/%s" % (tmp, index, s._id)
            logger.debug("make directory: %s" % td)
            os.makedirs(td)
            if not os.path.exists(s.filename):
                return fail("snapshot file %s not found" % s.filename)
            shutil.copy(s.filename, td)
            fname = s.filename.split("/")[-1]
            # extract snapshot contents
            cmd = "cd %s ; tar --force-local -zxf %s" % (td, fname)
            if aci_utils.run_command(cmd) is None:
                return fail("failed to extract snapshot %s" % s.id)
            for f in ["bundle.tgz", "md5checksum.json"]:
                if not os.path.exists("%s/%s" % (td, f)):
                    return fail("snapshot %s missing required file %s"%(s.id,f))
            # check bundle against md5
            embedded = get_json_data("%s/md5checksum.json" % td)["md5checksum"]
            md5 = aci_utils.get_file_md5("%s/bundle.tgz" % td)
            if md5 is None or md5!=embedded:
                return fail("snapshot %s invalid md5(%s) expected(%s)" % (
                    s.id, md5, embedded))
            # extract bundle
            cmd = "cd %s ; tar -zxf %s" % (td, "bundle.tgz")
            if aci_utils.run_command(cmd) is None:
                return fail("failed to extract bundle %s" % s.id)
           
        # get the union of the list of classes from both s1 and s2 definitions,
        # use the managed_object definition from s2 (should always be the same) 
        # use the definition in s2 for list of objects, attributes, and flags
        # if the classname is not present in definition from s1 then skip it
        js1 = get_json_data("%s/0/%s/definition.json" % (tmp, s1._id))
        js2 = get_json_data("%s/1/%s/definition.json" % (tmp, s2._id))
        if len(js1)==0: return fail("invalid definition in snapshot %s"%s1._id)
        if len(js2)==0: return fail("invalid definition in snapshot %s"%s2._id)
        s1_classes = [cn for cn in js1["managed_objects"].keys()]
        managed_objects = {}
        for classname in js2["managed_objects"]:
            if classname not in s1_classes:
                logger.debug("skipping %s not in snapshot1" % classname)
                continue
            managed_objects[classname] = js2["managed_objects"][classname]

        # build list of all nodes (join of s1 and s2 nodes)
        nodes =[ int(x) for x in sorted(list(set().union(s1.nodes, s2.nodes)))]

        # create pool to perform work
        pool = Pool(processes=config.get("MAX_POOL_SIZE", 4))

        filtered_nodes = []
        for n in nodes:
            if len(c.nodes)==0 or n in c.nodes: filtered_nodes.append(n)

        # build out work that needs to be completed
        class_work = [] # list of classes to perform 'class' work
        analyzer_work = [] # list of customer analyzers to work
        for classname in managed_objects:
            mo = managed_objects[classname]
            if len(classnames)>0 and classname not in classnames: continue
            if mo["analyzer"]=="" or mo["analyzer"]=="default": class_work.append(classname)
        for analyzer in ManagedObjects.ANALYZERS:
            # skip empty analyzer and default analyzer as they are 'class-work'
            if len(analyzer)==0 or analyzer=="default": continue
            # if a filter is set on the comparison for specific classname, then
            # ensure should be the name of the analyzer
            if len(classnames)==0 or analyzer in classnames: analyzer_work.append(analyzer)

        # think of progress as the sum of all tasks that need to be completed.
        # one task for each class in 'class_work' per node plus
        # one task for each analyzer in 'analyzer_work' per node plus
        # two task per node to for remapping (one for each snapshot)
        total_progress =len(class_work)*len(filtered_nodes) + \
                        len(analyzer_work)*len(filtered_nodes) + \
                        len(filtered_nodes)*2
        current_progress = 0
        progress(current_progress, total_progress)

        # perform comparision for each node
        for i,n in enumerate(filtered_nodes):
            if n!="0" and c.remap:
                # build remap for s1 and s2 
                r1 = Remap(n, "%s/0/%s/node-%s" % (tmp, s1._id, n))
                current_progress+=1
                r2 = Remap(n, "%s/1/%s/node-%s" % (tmp, s2._id, n))
                current_progress+=1
            else: 
                # create disabled remap objects
                r1 = Remap(n)
                r2 = Remap(n) 
                current_progress+=2
            progress(current_progress, total_progress) 
    
            work = []
            # build out classwork
            for classname in class_work:
                o = managed_objects[classname]
                cn = "node-%s/%s.json" % (n, classname)
                f1 = "%s/0/%s/%s" % (tmp, s1._id, cn)
                f2 = "%s/1/%s/%s" % (tmp, s2._id, cn)
                work.append(("class", c, o, f1, f2, r1, r2))

            # build out analyzer work
            f1 = "%s/0/%s/node-%s/" % (tmp, s1._id, n)
            f2 = "%s/1/%s/node-%s/" % (tmp, s2._id, n)
            for analyzer in analyzer_work:
                work.append(("custom", analyzer, c, f1, f2, r1, r2 ))
                
            # start the work using multiprocessing or serialize
            if c.serialize:
                for w in work: 
                    generic_compare(w)
                    current_progress+=1
                    progress(current_progress, total_progress) 
            else:
                pool.map(generic_compare, work)
                current_progress+= len(work)
                progress(current_progress, total_progress) 
                
        # cleanup tmp extracted files
        tmp_cleanup() 

        # create totals by summing over current compareResults
        counters = ["created", "modified", "deleted", "equal"]
        base = {"created":0, "modified":0, "deleted":0, "equal":0}
        total = copy.deepcopy(base)
        per_class = {}  # indexed per classname
        per_node = {}   # indexed per node_id
        results = CompareResults.read(compare_id=c._id)
        for o in results["objects"]:
            if o["classname"] not in per_class:
                per_class[o["classname"]] = copy.deepcopy(base)
                per_class[o["classname"]]["classname"] = o["classname"]
                per_class[o["classname"]]["name"] = o["name"]
            if o["node_id"] not in per_node:
                per_node[o["node_id"]] = copy.deepcopy(base)
                per_node[o["node_id"]]["node_id"] = o["node_id"]
            for counter in counters:
                per_class[o["classname"]][counter]+= o["total"][counter]
                per_node[o["node_id"]][counter]+= o["total"][counter]
                total[counter]+= o["total"][counter]
        # save totals
        c.total = total
        c.total_per_class = [per_class[k] for k in sorted(per_class.keys())]
        c.total_per_node = [per_node[k] for k in sorted(per_node.keys())]

        # after everything is complete, update progress to 100% and complete
        c.progress = 1.0
        c.status = "complete"
        c.total_time = abs(time.time() - ts)
        if not c.save(): logger.warn("failed to save compare status")
        logger.debug("compare complete: %s " % c._id)

    except Exception as e:
        logger.debug(traceback.format_exc())
        fail("unexpected error occurred: %s" % e)

def generic_compare(args):
    """ execute either per_node_class_comare or per_node_custom_compare
        based on value at arg[0].
        Note, list of args are provided as workaround to Pool.map restriction
    """
    if current_process().name != "MainProcess":
        logger.debug("creating new db connection object for child process")
        get_db(uniq=True, overwrite_global=True)

    args = list(args)
    compare_type = args.pop(0)
    if compare_type == "custom":
        if len(args)!=6:
            logger.warn("invalid arg list for custom_compare: %s" % args)
            return
        else:
            custom_type = args.pop(0)
            if custom_type == "acls":
                acl_compare(*args)
            elif custom_type == "endpoints": 
                endpoint_compare(*args)
            elif custom_type == "exclude":
                # no comparison performed for 'exclude' analyzer
                pass
            else:
                logger.warn("unknown custom compare type %s" % custom_type)
    elif compare_type == "class":
        if len(args)!=6:
            logger.warn("invalid arg list for class_compare: %s" % args)
            return
        else: 
            per_node_class_compare(*args)
    else:
        logger.warn("unknown compare type %s" % compare_type)

def get_subset(obj, attributes, key=""):
    """ return new dict with with specific attributes copied from original object """
    ret = {}
    for a in attributes: 
        if a in obj: 
            ret[a] = obj[a]
    if "_key" in obj: ret["_key"] = obj["_key"]
    if key in obj: ret[key] = obj[key]
    return ret

def per_node_class_compare(compare,mo,file1,file2,remap1,remap2):
    """ receive compare object and managed_object (single classname) directives along with file 
        pointers to corresponding objects. If the file does not exist or cannot be read, treat in 
        same manner as if there were no objects present (i.e., going to have a lot of 'created' or
        'deleted' objects in the result)
    """
    # node-id is present in remap object (should be the same node...)
    logger.debug("compare %s classname %s, node: %s", compare._id, mo["classname"], remap1.node_id)

    # check for abort (which might not be seen during multiprocessing progress)
    _s = Compare.load(_id=compare._id)
    if not _s.exists() or _s.status == "abort": 
        logger.debug("%s aborted", compare._id)
        return

    # check if MO itself has been filtered by compare settings
    if not ManagedObjects.severity_match(compare.severity, mo["severity"]):
        logger.debug("%s filtered by severity %s", mo["classname"], compare.severity)
        return
    if not compare.dynamic and "dynamic" in mo["labels"]:
        logger.debug("%s filtered by dynamic-disabled option", mo["classname"])
        return
    if not compare.statistic and "statistic" in mo["labels"]:
        logger.debug("%s filtered by statistic-disabled option", mo["classname"])
        return

    # get list of objects
    s1_objects = Remap.get_object_attributes(file1, mo["classname"])
    s2_objects = Remap.get_object_attributes(file2, mo["classname"])

    # rebuild snapshot object as a dict indexed by remapped mo key
    def get_indexed_objects(objects, remapper):
        s = {}
        # for no-key objects, return a single fixed-indexed dict with 
        # first object found
        if "no-key" in mo["labels"] and len(objects)>0: return {"-":objects[0]}
        for o in objects:
            if mo["key"] in o:
                key = remapper.remap_attribute(o[mo["key"]], mo["remap"])
                if key not in s: s[key] = o 
                else:
                    logger.warn("(%s) duplicate key in snapshot: %s", mo["classname"], key)
            else:
                logger.warn("(%s) key %s not found in %s", mo["classname"], mo["key"], o)
        return s

    s1 = get_indexed_objects(s1_objects, remap1)
    s2 = get_indexed_objects(s2_objects, remap2)

    # unique CompareResult per operation (should never be cumlative and does not require db read)
    result = CompareResults(compare_id=compare._id, node_id=remap1.node_id,classname=mo["classname"])
    result.total["s1"] = len(s1)
    result.total["s2"] = len(s2)

    # list of objects are all of the same class - build out the attributes that
    # we care about based on mo and compare settings 
    attributes = {}             # interesting attributes to examine
    mo_attributes = {}          # all attributes referenced in definition
    for a in mo["attributes"]: mo_attributes[a["name"]] = a
    default_attr = {
        "severity": ManagedObjects.severities.get("default", "notice"),
        "labels": [],
        "remap": [],
    }
    if len(s2)>0:
        for a in s2[s2.keys()[0]]:
            if len(mo["include"])>0 and a not in mo["include"]: continue
            elif len(mo["exclude"])>0 and a in mo["exclude"]: continue
            # no need to compare keys as already validated they match
            if a == mo["key"]: continue
            attr = mo_attributes.get(a, default_attr)
            # filter based on severity
            if not ManagedObjects.severity_match(compare.severity, attr["severity"]): continue
            # fitler based on dynamic
            if not compare.dynamic and "dynamic" in attr["labels"]: continue
            # determine if attribute is a timestamp
            is_timestamp = False
            if "timestamp" in attr["labels"] or \
                (re.search(ManagedObjects.TIMESTAMP_REGEX,a) and \
                "no-timestamp" not in attr["labels"]):
                is_timestamp = True
            if is_timestamp and not compare.timestamp: continue
            # filter based on statistic
            if not compare.statistic and "statistic" in attr["labels"]:continue
            # this is an interesting attribute to compare
            attributes[a] = attr

    logger.debug("%s interesting attributes: %s", mo["classname"],attributes.keys())

    # check for modified and deleted
    for k in s1:
        if mo["key"] in s1[k]: s1[k]["_key"] = s1[k][mo["key"]]
        else: s1[k]["_key"] = mo["classname"]
        if k not in s2:
            result.total["deleted"]+=1
            # create object with only attributes we care about
            result.deleted.append(get_subset(s1[k], attributes, key=mo["key"]))
            continue

        if mo["key"] in s2[k]: s2[k]["_key"] = s2[k][mo["key"]]
        else: s2[k]["_key"] = mo["classname"]

        # list of differences in following format:
        #   {
        #       "_key": <always key2>
        #       "key1": <definition (usually value of dn)>
        #       "key2": <definition (usually value of dn)>
        #       "map_key": <remapped definition (usually value of dn)>
        #       "modified": [{
        #           "attribute": <attribute-name>,
        #           "value1": <value in s1>,
        #           "value2": <value in s2>,
        #           "map_value1": <remapped value in s1>,
        #           "map_value2": <remapped value in s2>,
        #       }]
        #   }
        diff = {
            "map_key": k,
            "key1": s1[k].get(mo["key"], ""),
            "key2": s2[k].get(mo["key"], ""),
            "_key": s2[k].get("_key", ""),
            "modified": [],
            "equal": [],
        }
        # if mo["key"] exists, always add to equal list
        if mo["key"] not in attributes and mo["key"] in s2[k]:
            diff["equal"].append({
                "attribute": mo["key"],
                "value": s2[k][mo["key"]]
            })

        for a in attributes:
            # this should never happen since it implies different attributes
            # for objects of the same class
            if a not in s2[k]:
                logger.warn("%s attribute not found in s2", mo["classname"],a)
                continue

            # handle list and list-extended cases
            attr = attributes[a]
            attr_list = False
            attr_list_expand = False
            if "labels" in attr:
                if "list-expand" in attr["labels"]: 
                    attr_list_expand = True
                    attr_list = True
                elif "list" in attr["labels"]: attr_list = True
            
            # assume match before starting comparison    
            match = True
           
            # process attribute values as ordered list
            if attr_list:

                # expand ranges if enabled
                if attr_list_expand:
                    v1 = expand_range(s1[k].get(a,""))
                    v2 = expand_range(s2[k].get(a,""))
                else:
                    # build list of unique values
                    v1 = list(set(s1[k].get(a,"").split(",")))
                    v2 = list(set(s2[k].get(a,"").split(",")))
                # remove empty value
                if "" in v1: v1.remove("")
                if "" in v2: v2.remove("")

                # remap each value individually
                (v1_remap, v2_remap) = ([], [])
                for v in v1:
                    v1_remap.append(remap1.remap_attribute(v, attr["remap"]))
                for v in v2:
                    v2_remap.append(remap2.remap_attribute(v, attr["remap"]))

                # check for presence of each value in both v1 and v2
                for v in v1_remap:
                    if v not in v2_remap:
                        match = False
                        break
                if match:
                    for v in v2_remap:
                        if v not in v1_remap: 
                            match = False
                            break
                # set v1/v2 to remap values
                v1 = ",".join(v1_remap)
                v2 = ",".join(v2_remap)

            # process attribute as a single value
            else: 
                # perform remaps for each value
                v1 = remap1.remap_attribute(s1[k].get(a,""), attr["remap"])
                v2 = remap2.remap_attribute(s2[k].get(a,""), attr["remap"])

                # should rarely happen that new attribute is added to object
                if a not in s1[k]:
                    logger.debug("%s attribute %s not found in s1", mo["classname"], a)
                    match = False
                elif v1!= v2:
                    match = False
            
            # add to equal list on match        
            if match:
                diff["equal"].append({
                    "attribute": a,
                    "value": s2[k].get(a, ""),
                })
            # highlight diff on mismatch
            else:
                logger.debug("%s attribute mismatch %s != %s", a, v1, v2)
                diff["modified"].append({
                    "attribute": a,
                    "value1": s1[k].get(a, ""),
                    "value2": s2[k].get(a, ""),
                    "map_value1": v1,
                    "map_value2": v2
                })

        # if diffs are present then object was modified
        if len(diff["modified"])==0:
            result.total["equal"]+=1
            result.equal.append(get_subset(s1[k], attributes,key=mo["key"]))
        else:
            result.total["modified"]+=1
            result.modified.append(diff)

    # check only for created objects (those absent from s1)
    for k in s2:
        if k not in s1:
            if mo["key"] in s2[k]: s2[k]["_key"] = s2[k][mo["key"]]
            else: s2[k]["_key"] = mo["classname"]
            result.total["created"]+=1
            result.created.append(get_subset(s2[k], attributes,key=mo["key"]))

    logger.debug("comparison complete(%s) %s: %s", result.compare_id,result.classname, result.total)
    result.save()

def endpoint_compare(compare, folder1, folder2, remap1, remap2):
    """ perform endpoint comparision between snapshots. Note only local
        endpoints are captured in the comparision.  This will created filtered
        list of objects and write to file and then use per_node_class_compare
        for consistent comparision of the 'interesting' objects
    """

    logger.debug("compare %s endpoints, node: %s", compare._id, remap1.node_id)

    # check for abort (which might not be seen during multiprocessing progress)
    _s = Compare.load(_id=compare._id)
    if not _s.exists() or _s.status == "abort": 
        logger.debug("%s aborted", compare._id)
        return
    
    # for filtering, need to read in mo for 'endpoints' and get severity
    mo = ManagedObjects.load(classname="endpoints")
    mo = mo.to_json()

    # check if MO itself has been filtered by compare settings first
    if not ManagedObjects.severity_match(compare.severity, mo["severity"]):
        logger.debug("endpoints filtered by severity %s", compare.severity)
        return

    # expect for 'endpoints.json' file within each folder
    f1 = "%s/endpoints.json" % folder1
    f2 = "%s/endpoints.json" % folder2
    s1_objects = Remap.get_per_classname_object_attributes(f1)
    s2_objects = Remap.get_per_classname_object_attributes(f2)

    # build list of attributes (same for all objects and only compared if
    # present).  addr, createTs, flags, ifId, modTs, pcTag, status
    attributes = ["addr", "flags", "ifId", "pcTag", "status"]
    if compare.timestamp: attributes+= ["createTs", "modTs"]

    # return list of objects filtered on local/non-svi/non-loopback objects only
    def get_local_objects(objects):
        ret = []
        for o in objects:
            if "flags" not in o or (re.search("local(,|$)",o["flags"]) and "svi" not in o["flags"]):
                ret.append({"endpoints":{"attributes":o}})
        return ret

    # ensure all required classes are present
    classes = ["epmMacEp", "epmIpEp", "epmRsMacEpToIpEpAtt"]
    for c in classes:
        if c not in s1_objects: s1_objects[c] = []
        if c not in s2_objects: s2_objects[c] = []

    # walk through epmIpEp objects and add empty mac, bd, and encap
    # then walk through epmRsMacEpToIpEpAtt and add to corresponding epmIpEp
    reg = "/bd-\[vxlan-(?P<bd>[0-9]+)\]/vx?lan-\[(?P<encap>vx?lan-[0-9]+)\]/"
    reg+= "db-ep/mac-(?P<mac>[0-9A-Fa-f:]+)/rsmacEpToIpEpAtt-"
    s1_epmIpEp = {}
    s2_epmIpEp = {}
    for o in s1_objects["epmIpEp"]: 
        o["mac"] = "-"
        o["bd"] = "-"
        o["encap"] = "-"
        s1_epmIpEp[o["dn"]] = o
    for o in s2_objects["epmIpEp"]: 
        o["mac"] = "-"
        o["bd"] = "-"
        o["encap"] = "-"
        s2_epmIpEp[o["dn"]] = o
    for o in s1_objects["epmRsMacEpToIpEpAtt"]:
        r1 = re.search(reg, o["dn"])
        if r1 is not None:
            tDn = o["tDn"]
            if tDn in s1_epmIpEp: 
                s1_epmIpEp[tDn]["mac"] = r1.group("mac")
                s1_epmIpEp[tDn]["bd"] = "vxlan-%s" % r1.group("bd")
                s1_epmIpEp[tDn]["encap"] = r1.group("encap")
            else:
                logger.debug("tDn(%s) not found for %s", tDn, o["dn"])
        else:
            logger.debug("failed to match rsmacEpToIpEpAtt regex for %s", o["dn"])
    for o in s2_objects["epmRsMacEpToIpEpAtt"]:
        r2 = re.search(reg, o["dn"])
        if r2 is not None:
            tDn = o["tDn"]
            if tDn in s2_epmIpEp: 
                s2_epmIpEp[tDn]["mac"] = r2.group("mac")
                s2_epmIpEp[tDn]["bd"] = "vxlan-%s" % r2.group("bd")
                s2_epmIpEp[tDn]["encap"] = r2.group("encap")
            else:
                logger.debug("tDn(%s) not found for %s", tDn, o["dn"])
        else:
            logger.debug("failed to match reg(%s) regex for %s", reg,o["dn"])
        
    # here we overwrite endpoints.json file with only interesting (local) endpoints.  We need to 
    # merge epmIpEp and epmMacEp objects into single file
    all_s1_objects = []
    all_s2_objects = []
    # check epmMacEp, epmIpEp
    for c in ["epmMacEp", "epmIpEp"]:
        # build subset of interesting objects with classname 'endpoints' and
        # write to file for per_node_class_compare to read
        all_s1_objects+= get_local_objects(s1_objects.get(c, []))
        all_s2_objects+= get_local_objects(s2_objects.get(c, []))
    try:
        with open(f1, "w") as f: json.dump(all_s1_objects, f)
        with open(f2, "w") as f: json.dump(all_s2_objects, f)
        per_node_class_compare(compare, mo, f1, f2, remap1, remap2)
    except Exception as e: 
        logger.error("failed to perform endpoints comparions on %s: %s", c, e)
    
def acl_compare(compare, folder1, folder2, remap1, remap2):
    """ perform acl comparision between snapshots """
    # TODO 
    pass 
