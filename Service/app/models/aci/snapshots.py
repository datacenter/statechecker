
from . import utils as aci_utils
from .definitions import Definitions
from .managed_objects import ManagedObjects
from .remap import Remap
from .fabrics import Fabrics
from ..rest import (Rest, api_register)
from ..utils import format_timestamp, get_user_data
from werkzeug.exceptions import (NotFound, BadRequest)
from flask import abort,jsonify,send_from_directory, request, current_app

import traceback, time, os, shutil, json, re, hashlib, uuid
import logging

# set sorted as natsort if available
try: from natsort import natsorted as sorted
except ImportError as e: pass

# module level logging
logger = logging.getLogger(__name__)

def background_snapshot(obj, **kwargs):
    """ start or restart snapshot operation """
    _id = kwargs.get("_id", None)
    if _id is None:
        logger.warn("invalid _id for newly created snapshot: %s" % kwargs)
        return
    s = Snapshots.load(_id=_id)
    if not s.exists(): abort(500, "failed to create snapshot")
    # don't execute runtime snapshotshot collection for non-runtime sources
    if s.source != "runtime": return
    # set start time to 'now' before executing background worker
    s.start_time = time.time()
    s.save()
    if not aci_utils.execute_worker("--snapshot %s" % _id):
        abort(500, "failed to start background snapshot process")

def delete_cleanup(filters, **kwargs):
    """ remove local snapshot files before snapshot delete """
    objs = Snapshots.read(_filters=filters, **kwargs)
    if "objects" in objs:
        for o in objs["objects"]:
            if len(o["filename"])>0 and os.path.exists(o["filename"]):
                try: 
                    logger.debug("removing snapshot(%s) file %s" % (
                        o["_id"], o["filename"]))
                    os.remove(o["filename"])
                except Exception as e:
                    logger.debug("failed delete snapshot file: %s" %(o))

    # should return unaltered filters
    return filters

def before_snapshot_create(data, **kwargs):
    """ before snapshot create, verify valid fabric and definition """
    fabric = data["fabric"]
    f = Fabrics.load(fabric=fabric)
    if not f.exists():
        abort(400, "fabric %s does not exist" % fabric)
    # relax checks for uploaded file as already verifed during upload extraction
    if data["source"] == "upload": return data
    d = Definitions.load(definition=data["definition"])
    if not d.exists():
        abort(400, "definition '%s' does not exist"  % data["definition"])
    # set a default description if one was not provided
    if len(data["description"].strip()) == 0:
        data["description"] = "%s.snapshot.%s" % (fabric, 
            format_timestamp(time.time()))
    return data

def download_snapshot(_id):
    # download a snapshot .tgz file 
    snapshot = Snapshots.load(_id=_id)
    if not snapshot.exists():
        abort(400, "snapshot %s not found" % _id)
    else:
        if snapshot.filename is not None:
            if os.path.isfile(snapshot.filename) is False:
                abort(400, "File not found")
            try: 
                path = snapshot.filename.split('/')
                filename = path[len(path) - 1]
                parent_dir_path = "/".join(path[:-1])
                return send_from_directory(parent_dir_path,filename, as_attachment = True)
            except Exception as err:
                logger.debug('Traceback :\n %s', traceback.format_exc())
                abort(500,'Error downloading the file') 
    abort(400, "File metadata not found")

def upload_snapshot():
    from ..utils import get_app_config
    if request.files is None:
        abort(400, "No files uploaded")
    else:
        tmp_dir = os.path.realpath("%s/%s" % (current_app.config["TMP_DIR"],uuid.uuid4()))
        config = get_app_config()
        dst = config.get("DATA_DIR", "/tmp/")
        try:
            for filename in request.files:
                f = request.files[filename] 
                # validate file is .tgz file and allowed name
                if not re.search("(?i)^[a-z0-9\-_\.:]+?\.tgz$", f.filename):
                    abort(400, "Invalid filename for snapshot: %s" % f.filename)
                logger.debug("upload request for file: %s", f.filename)
                temp_filename = os.path.join(tmp_dir , f.filename)
                # create the directory
                os.mkdir(tmp_dir)
                os.chdir(tmp_dir)
                # unzip and stuff..
                f.save(temp_filename)
                if aci_utils.run_command('tar --force-local -zxf ' + temp_filename) is None:
                    abort(500,"Failed to unzip snapshot")
                if aci_utils.run_command('tar --force-local -zxf bundle.tgz') is None:
                    abort(500,"Failed to unzip snapshot")
                # try to extract required data, abort if not in correct format which triggers exception
                try:
                    checksum = json.loads(open( os.path.join(tmp_dir,'md5checksum.json')).read()).get('md5checksum')
                    bundle_checksum = aci_utils.get_file_md5('bundle.tgz') 
                    if bundle_checksum != checksum:
                        abort(400,"snapshot file md5 is invalid")
                    fnew = open(os.path.join(tmp_dir,'snapshot.json'), 'r')
                    fileJson = json.loads(fnew.read())
                except BadRequest as e: raise e
                except Exception as e:
                    logger.debug("Traceback:\n %s", traceback.format_exc())
                    abort(400, "Invalid snapshot file")

                for node in fileJson.get('nodes'):
                    if os.path.exists(os.path.join(tmp_dir,'node-') + node) is False:
                        abort(400,'One or more nodes missing in provided snapshots')
                    snap = Snapshots()
                    supported_attr = ["fabric","definition", "description", "fabric_domain", "nodes",
                                        "start_time", "wait_time", "total_time"]
                    for attr in supported_attr:
                        if attr in fileJson:
                            setattr(snap, attr, fileJson[attr])
                    # ensure fabric and definition exists as that will trigger save to fail
                    f = Fabrics.load(fabric=snap.fabric)
                    if not f.exists():
                        abort(400, "fabric %s does not exist" % fabric)
                    d = Definitions.load(definition=snap.definition)
                    if not d.exists():
                        abort(400, "definition '%s' does not exist"  % data["definition"])
                        # set a default description if one was not provided
                    if len(snap.description.strip()) == 0:
                        snap.description = "%s.snapshot.%s" % (fabric,format_timestamp(time.time()))
                    snap.progress = 1.00
                    snap.status = 'complete'
                    snap.error = False
                    snap.source = 'upload'
                    snap.filename = "snapshot.%s.%s.tgz" % (snap.fabric, 
                                                format_timestamp(snap.start_time,msec=True))
                    snap.filename = os.path.join(dst,snap.filename)
                    # create the directory if not present
                    if not os.path.isdir(dst): os.makedirs(dst)
                    shutil.copyfile(temp_filename, snap.filename)
                    snap.filesize = os.path.getsize(snap.filename)
                    if not snap.save(): abort(500, "failed to save snapshot")
                    return jsonify({"success": True})
            # no valid file found
            abort(400, "no filename provided in upload")
        except BadRequest as e: raise e
        except Exception as err:
            logger.debug("Traceback:\n %s", traceback.format_exc())
            abort(500,"An error occurred processing snapshot")
        finally:
            # ensure tmp directories are always cleaned up
            logger.debug("removing tmp directory: %s", tmp_dir)
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
    
    # if for some reason did not hit return...
    abort(500,"Error in request")

@api_register(path="/aci/snapshots")
class Snapshots(Rest):
    """ ACI Snaphots REST class """

    logger = logging.getLogger(__name__)
    META_ACCESS = {
        "expose_id": True,
        "update": False,
        "bulk_delete": False,
        "before_create": before_snapshot_create,
        "after_create": background_snapshot,
        "before_delete": delete_cleanup,
        "routes":[{
            "path":"download",
            "keyed_url": True,
            "methods":["GET"],
            "function":download_snapshot
        }, 
        {
            "path":"upload",
            "keyed_url": False,
            "methods":["POST"],
            "function": upload_snapshot
        }]
    }
    META = {
        "fabric":{
            "type":str, 
            "default":"", 
            "regex":"^[a-zA-Z0-9\-\.:_]{1,64}$",
        },
        "definition":{
            "type":str,
            "default":"default",
            "regex":"^[a-zA-Z0-9\-\.:_]{1,64}$",
        },
        "description":{
            "type":str,
            "description": "snapshot description (up to 8K characters)",
            "regex":"^.{0,8192}$",
        },
        "fabric_domain":{
            "type":str,
            "write":False,
        },
        "nodes":{
            "type":list,
            "subtype":str,
            "write":False,
        },
        "filename": {
            "type":str,
            "default":"",
            "write":False,    
        },
        "filesize": {
            "type":float,
            "write": False,
        },
        "start_time": {
            "type": float,
            "write": False,
        },
        "wait_time": {
            "type": float,
            "write": False,
        },
        "total_time": {
            "type": float,
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
            "values": ["init", "running", "complete", "error"],
            "write":False,
        },
        "error":{
            "type":str,
            "default":"",
            "write":False,
        },
        "source":{
            "type":str,
            "values":["upload","runtime"],
            "default": "runtime",
            "write": False,
        },
    }


def execute_snapshot(snapshot_id):
    """ perform snapshot operation for provided fabric name and definition name.
        The snapshot will be stored in config["DATA_DIR"]. The progress of the
        collection and final result are saved to the database.

        format of snapshot:
            snapshot.<fabric-name>.<date>.tgz
            /md5checksum                checksum of bundle.tgz
            /bundle.tgz
                /snapshot.json          snapshot object attributes
                /definition.json
                /node-X                 note, node-0 is for global objects
                    /<classname.json>   per-object class collection

    """
    from ..utils import (get_app_config, format_timestamp, pretty_print)
    logger.debug("execute snapshot for: %s" % snapshot_id)

    config = get_app_config()
    src = config.get("TMP_DIR", "/tmp/")
    dst = config.get("DATA_DIR", "/tmp/")

    reg = "topology/pod-[0-9]+/node-(?P<node>[0-9]+)(/|$)"
    reg = re.compile(reg)

    # verify that snapshot object exists, if not abort since no way to alert
    # user of final result
    ts = time.time()    
    apic = None
    s = Snapshots.load(_id=snapshot_id)
    if not s.exists():
        logger.warn("snapshot %s not found" % snapshot_id)
        return
    
    filename = "snapshot.%s.%s.tgz"% (s.fabric, format_timestamp(ts,msec=True))
    src = "%s/%s"%(src, re.sub("\.tgz$","", filename))

    # update snapshot state with error message and error status
    def fail(msg="", cleanup=True):
        if len(msg)>0: s.error = msg
        s.status = "error"
        s.total_time = abs(time.time() - ts)
        logger.debug("snapshot %s failed: %s" % (s._id, s.error))
        if not s.save(): logger.warn("failed to save snapshot %s state"%s._id)
        if cleanup: tmp_cleanup()
        return

    # clean up working directory
    def tmp_cleanup():
        if os.path.isdir(src):
            logger.debug("cleanup directory %s" % src)
            try: shutil.rmtree(src)
            except Exception as e: 
                logger.warn("failed to cleanup directory(%s): %s"%(src,e))
        else: logger.debug("cleanup directory %s not found" % src)
        if apic is not None: apic.close()

    # update snapshot progress percentage
    def progress(i, total):
        abort_snapshot() # check for abort signal before progress update
        if total>0: p = round(i/(1.0*total), 2)
        else: p = 0
        s.progress = p
        s.total_time = abs(time.time() - ts)
        if not s.save(): logger.warn("failed to save snapshot %s state"%s._id)
        return

    # user can force snapshot execution to stop by deleting the object
    # abort_snapshot is checked at a regular interval.  If snapshot was deleted
    # then perform cleanup and return True, else return False
    def abort_snapshot():
        _s = Snapshots.load(_id=s._id)
        if not _s.exists(): 
            logger.debug("snapshot %s has been deleted, aborting" % s._id)
            tmp_cleanup()
            raise Exception("snapshot operation %s aborted" % s._id)

    # write dict data to specified path
    def json_write(path, data):
        if not re.search("\.json$", path): path = "%s.json" % path
        if not os.path.exists(os.path.dirname(path)): 
            os.makedirs(os.path.dirname(path))
        logger.debug("saving to %s" % (path))
        with open("%s" % path, "w") as f: json.dump(data, f)

    # init progress, error, status
    s.nodes = []
    s.fabric_domain = ""
    s.progess = 0.0
    s.filename = ""
    s.filesize = 0
    s.start_time = ts
    s.total_time = 0
    s.wait_time = 0
    s.error = ""
    s.status = "running"
    s.save()

    try:
        # setup working directory to store collection outputs
        if os.path.exists(src):
            return fail("tmp directory already exists: %s"%src, cleanup=False)
        os.makedirs(src)

        # get definition managed_objects to collect
        d = Definitions.load(definition=s.definition)
        if not d.exists():
            return fail("unable to read definition: %s" % s.definition)
        managed_objects = d.get_managed_objects()

        # ensure all required objects are within definition.  If not add them
        for r in Remap.REQUIRED_MANAGED_OBJECTS:
            if r not in managed_objects:
                logger.debug("adding required mo to definition: %s"%r)
                mo = ManagedObjects(classname=r)
                mo.analyzer = "exclude"
                managed_objects[mo.classname] = mo.to_json()

        # create apic session
        apic = aci_utils.get_apic_session(s.fabric)
        if apic is None: return fail("unable to connect to %s apic" % s.fabric)
    
        ret = aci_utils.get_class(apic,"infraCont")
        if ret is not None and len(ret)>0 and "infraCont" in ret[0] and \
            "attributes" in ret[0]["infraCont"] and \
            "fbDmNm" in ret[0]["infraCont"]["attributes"]:
            s.fabric_domain = ret[0]["infraCont"]["attributes"]["fbDmNm"]

        complete_count = 0
        for classname in managed_objects:
            complete_count+=1
            o = managed_objects[classname]
            if len(o["classname"])==0:
                logger.warn("%s ignoring empty classname %s" % (
                    s.definition, o["classname"]))
                continue
            _t = time.time()
            response_classes = []
            logger.debug("getting data for class %s" % o["classname"])
            if o["pseudo"]: 
                # for pseudo mo, collect each of the classnames defined in the
                # corresponding customer analyzer.  If no customer analyzer then
                # no objects will be collected...
                if o["analyzer"] in ManagedObjects.ANALYZERS and \
                    "classnames" in ManagedObjects.ANALYZERS[o["analyzer"]]:
                    ret = []
                    for ac in ManagedObjects.ANALYZERS[o["analyzer"]]["classnames"]:
                        order = "%s.%s" % (ac, "dn")   # static to dn for now
                        sret = aci_utils.get_class(apic, ac, orderBy=order)
                        if sret is not None: 
                            ret+= sret
                            response_classes.append(ac)
            elif len(o["uri"])>0: 
                ret = aci_utils.get(apic, o["uri"])
                response_classes.append(o["classname"])
            else: 
                order = "%s.%s" % (o["classname"], o["key"])
                ret = aci_utils.get_class(apic, o["classname"], orderBy=order)
                response_classes.append(o["classname"])
            s.wait_time += abs(time.time() - _t)
            # if failed to get object, might not exists on current version of
            # code.  just continue
            if ret is None: 
                progress(complete_count, len(managed_objects)+1)
                continue
            
            # need to parse each received object and group based on node-id
            cc_match = None # cache expected response_classes value (usually the
                            # same for all objects expect for pseudo case)
            nodes = {}
            for c in ret:
                node = "0"
                if type(c) is dict and len(c)>=1:
                    cc = None
                    # check for each possible response_class in returned object
                    if cc_match is not None and cc_match in c:
                        cc = c[cc_match]
                    else:
                        for rclass in response_classes:
                            if rclass in c:
                                cc_match = rclass
                                cc = c[cc_match]
                                break
                            else:
                                # check if 'children' is present and first level
                                # child has corresponding object. before child 
                                # check, try to extract node-id (i.e., stats 
                                # object node-id from original parent object)
                                tc = c[c.keys()[0]]
                                if "attributes" in tc and "dn" in tc["attributes"]:
                                    r = reg.search(tc["attributes"]["dn"])
                                    if r is not None: node = r.group("node")
                                if "children" in tc:
                                    for child in tc["children"]:
                                        if rclass in child:
                                            cc = child[rclass]
                                            c = child
                                            break
                    if cc is None:
                        logger.debug("failed to extract data for %s from %s"%(
                            o["classname"], c))
                        continue
                    if type(cc) is dict and len(cc)>=1 and "attributes" in cc:
                        if "dn" in cc["attributes"]: 
                            r = reg.search(cc["attributes"]["dn"])
                            if r is not None: node = r.group("node")
                        if node not in nodes: nodes[node] = []
                        if node not in s.nodes: s.nodes.append(node)
                        nodes[node].append(c)
                        continue
                logger.debug("skipping unsupported object: %s" % c) 

            # for each node, write results to file
            for n in nodes:
                json_write("%s/node-%s/%s" % (src,n, o["classname"]), nodes[n])

            # check for abort and then update progress 
            progress(complete_count, len(managed_objects)+1)

        # sort nodes before saving
        s.nodes = sorted(s.nodes)

        json_write("%s/snapshot" % src, s.to_json())
        json_write("%s/definition" % src, {
            "definition": s.definition,
            "managed_objects": managed_objects
        })

        # bundle all files 
        ret = aci_utils.run_command("cd %s ; tar -zcvf bundle.tgz ./*" % src)
        if ret is None: return fail("failed to create snapshot bundle")

        # get md5 for bundle
        md5 = aci_utils.get_file_md5("%s/bundle.tgz" % src)
        if md5 is None: return fail("failed to calculate bundle md5")
        json_write("%s/md5checksum" % src, {"md5checksum": md5})

        # create final bundle with bundle.tgz and md5checksum.json
        cmd = "cd %s ; tar --force-local -zcvf %s " % (src,filename)
        cmd+= "./bundle.tgz ./md5checksum.json" 
        if aci_utils.run_command(cmd) is None:
            return fail("failed to create snapshot bundle")

        # to prevent race condition of 'delete' operation during compression,
        # perform one last abort check before moving complete file to dst
        abort_snapshot()

        # create the directory if not present
        if not os.path.isdir(dst): os.makedirs(dst)

        # move final bundle to dst directory and cleanup tmp directory
        if aci_utils.run_command("mv %s/%s %s/" % (src,filename, dst)):
            return fail("failed to save snapshot bundle")
        tmp_cleanup()

        # after everything is complete, update progress to 100% and complete
        s.progress = 1.0
        s.status = "complete"
        s.filename = "%s/%s" % (dst, filename)
        s.filesize = os.path.getsize("%s/%s" % (dst, filename))
        s.total_time = abs(time.time() - ts)
        if not s.save(): logger.warn("failed to save snapshot status")
        logger.debug("snapshot %s complete: %s " % (snapshot_id, s))

    except Exception as e:
        logger.debug(traceback.format_exc())
        fail("unexpected error occurred: %s" % e)



