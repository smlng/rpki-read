import logging
import time

from pymongo import MongoClient
from settings import BULK_MAX_OPS

def purge_notfound(dbconnstr, interval):
    """Periodically remove old, expired NotFound valitdation results from database"""
    logging.debug ("CALL purge_notfound, with mongodb: " +dbconnstr)
    # open db connection
    client = MongoClient(dbconnstr)
    db = client.get_default_database()
    while(True):
        bulkRemove = db.archive.initialize_unordered_bulk_op()
        counter = 0
        # purge old NotFound entries
        if "archive" in db.collection_names() and db.archive.count() > 0:
            try:
                pipeline = [
                    { "$group": { "_id": '$prefix', "plist": { "$push" : { "pid": "$_id", "timestamp": "$timestamp", "type": "$type", "validity": "$validated_route.validity.state" } }, "maxts": {"$max" : '$timestamp'} } },
                    { "$unwind": "$plist" },
                    { "$match": {'plist.validity' : "NotFound"} },
                    { "$project": {"toDelete": { "$cond": [ { "$lt": [ "$plist.timestamp", "$maxts" ] }, "true", "false" ] }, "_id" : '$plist.pid', 'maxts': '$maxts', 'timestamp': '$plist.timestamp'} },
                    { "$match": {'toDelete': "true"} },
                    { "$limit": BULK_MAX_OPS}
                ]
                purge = db.archive.aggregate(pipeline)
                for p in purge:
                    counter += 1
                    bulkRemove.find({"_id": p['_id']}).remove_one()
                if counter > 0:
                    bulkRemove.execute()
            except Exception, e:
                logging.exception ("PURGE failed with: " + e.message)
        if counter < (BULK_MAX_OPS * 0.8):
            time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description='', epilog='')
    parser.add_argument('-l', '--loglevel',
                        help='Set loglevel [DEBUG,INFO,WARNING,ERROR,CRITICAL].',
                        type=str, default='WARNING')
    parser.add_argument('-m', '--mongodb',
                        help='MongoDB connection parameters.',
                        type=str, required=True)

    args = vars(parser.parse_args())

    numeric_level = getattr(logging, args['loglevel'].upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level,
                        format='%(asctime)s : %(levelname)s : %(message)s')

    dbconnstr = None
    # BEGIN
    logging.info("START")
    dbconnstr = args['mongodb'].strip()
    purge_interval = SERVICE_INTERVAL
    if purge_interval < 1:
        purge_interval = 300
    purge_notfound(dbconnstr, purge_interval)

if __name__ == "__main__":
    main()
