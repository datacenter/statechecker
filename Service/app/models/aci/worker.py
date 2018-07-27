"""
    For direct execution, ensure script is run as a library module:
        python -m app.models.aci.worker

    @author agossett@cisco.com
"""

from .. utils import get_app, setup_logger
import logging, sys, traceback

# setup logging for everything in 'app'
logger = setup_logger(logging.getLogger("app"), stdout=True, quiet=True)

def db_is_alive():
    """ perform connection attempt to database 
        return True on success or False on error
    """
    logger.debug("checking if db is alive")
    app = get_app()
    try:
        with app.app_context():
            db = app.mongo.db
            db.collection_names()
            logger.debug("database is alive")
            return True
    except Exception as e: pass
    logger.error("failed to connect to database")
    return False

def execute_snapshot(snapshot_id):
    """ start collection process for snapshot id """
    from .snapshots import execute_snapshot
    execute_snapshot(snapshot_id)

def execute_compare(compare_id):
    """ start comparison for provided compare id """
    from .compare import execute_compare
    execute_compare(compare_id)

def get_args():
    """ get arguments for worker """
    import argparse
    desc = """ 
    standalone worker process for aci fabric functions
    """
    parser = argparse.ArgumentParser(description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    parser.add_argument("--check_db", action="store_true", dest="check_db",
        help="validate successful database connection")
    parser.add_argument("--snapshot", action="store", dest="snapshot",
        default=None, help="execute snapshot for provided snapshot id")
    parser.add_argument("--compare", action="store", dest="compare",
        default=None, help="perform comparison for provided compare id")
    args = parser.parse_args()
    return args

if __name__ == "__main__":

    # get args from user
    args = get_args()
    method = None
    method_args = []

    if args.check_db: 
        logger.debug("worker request: check_db")
        method = db_is_alive
    elif args.snapshot is not None:
        logger.debug("worker request: snapshot (%s)"%args.snapshot)
        method = execute_snapshot
        method_args = [args.snapshot]
    elif args.compare is not None:
        logger.debug("worker request: compare (%s)"%args.compare)
        method = execute_compare
        method_args = [args.compare]
    else:
        logger.warn("no action provided.  use -h for help")
        sys.exit(1)

    # execute method with required arguments and exit with appropriate exit code
    from ..utils import get_app
    app = get_app()
    with app.app_context():
        try:
            if not method(*method_args): sys.exit(1)
            sys.exit(0)
        except Exception as e:
            sys.stderr.write("%s\n"% traceback.format_exc())
    sys.exit(1)

