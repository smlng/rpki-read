import logging
import time

from pymongo import MongoClient
from settings import BULK_MAX_OPS

def archive_notfound(dbconnstr, interval):
    """Periodically archive old, expired NotFound valitdation results in database"""
    logging.debug ("CALL archive_notfound, with mongodb: " +dbconnstr)
    # open db connection
    client = MongoClient(dbconnstr)
    db = client.get_default_database()
    while(True):
        bulkInsert = db.archive.initialize_unordered_bulk_op()
        bulkRemove = db.validity.initialize_unordered_bulk_op()
        counter = 0
        # archive old NotFound entries
        if "validity" in db.collection_names() and db.validity.count() > 0:
            try:
                pipeline = [
                    { "$group": { "_id": '$prefix', "plist": { "$push" : { "pid": "$_id", "timestamp": "$timestamp", "type": "$type", "validity": "$validated_route.validity.state" } }, "maxts": {"$max" : '$timestamp'} } },
                    { "$unwind": "$plist" },
                    { "$project": {"toArchive": { "$cond": [ { "$lt": [ "$plist.timestamp", "$maxts" ] }, "true", "false" ] }, "_id" : '$plist.pid', 'maxts': '$maxts', 'timestamp': '$plist.timestamp'} },
                    { "$match": {'toArchive': "true"} },
                    { "$limit": BULK_MAX_OPS}
                ]
                archive = db.validity.aggregate(pipeline)
                for p in archive:
                    counter += 1
                    bulkInsert.insert(db.validity.find_one({"_id": p['_id']}))
                    bulkRemove.find({"_id": p['_id']}).remove_one()
                if counter > 0:
                    bulkRemove.execute()
                    bulkInsert.execute()
            except Exception, e:
                logging.exception ("archive failed with: " + e.message)
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
    archive_interval = SERVICE_INTERVAL
    if archive_interval < 1:
        archive_interval = 300
    archive_notfound(dbconnstr, archive_interval)

if __name__ == "__main__":
    main()
