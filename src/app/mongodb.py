import logging

from datetime import datetime
from pymongo import MongoClient

def get_validation_stats(dbconnstr):
    client = MongoClient(dbconnstr)
    db = client.get_default_database()

    stats = dict()
    stats['latest_ts'] = 'now'
    stats['num_valid'] = 0
    stats['num_invalid_as'] = 0
    stats['num_invalid_len'] = 0
    stats['num_not_found'] = 0
    try:
        stats['num_valid'] = db.validity.find({'validated_route.validity.state' : 'Valid' }).count()
        stats['num_invalid_as'] = db.validity.find({'validated_route.validity.state' : 'InvalidAS' }).count()
        stats['num_invalid_len'] = db.validity.find({'validated_route.validity.state' : 'InvalidLength' }).count()
        stats['num_not_found'] = db.validity.find({'validated_route.validity.state' : 'NotFound' }).count()
        ts_tmp = db.validity.find_one(projection={'timestamp': True, '_id': False}, sort=[('timestamp', -1)])['timestamp']
        stats['latest_ts'] = datetime.fromtimestamp(int(ts_tmp)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception, e:
        logging.exception ("QUERY failed with: " + e.message)

    return stats

def get_validation_tables(dbconnstr):
    return '{}'
