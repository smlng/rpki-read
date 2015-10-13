import logging
import psycopg2
import sys

from datetime import datetime

def get_validation_stats(dbconnstr):
    try:
        con = psycopg2.connect(dbconnstr)
    except Exception, e:
        logging.exception ("connecting to database, failed with: " + e.message)
        sys.exit(1)
    cur = con.cursor()
    counts = dict()
    stats = dict()
    stats['latest_ts'] = 'now'
    stats['num_valid'] = 0
    stats['num_invalid_as'] = 0
    stats['num_invalid_len'] = 0
    stats['num_not_found'] = 0
    query = "SELECT state, count(*) FROM t_validity GROUP BY state"
    query_ts = "SELECT ts FROM t_validity ORDER BY ts DESC LIMIT 1"
    try:
        cur.execute(query)
        rs = cur.fetchall()
    except Exception, e:
        logging.exception ("QUERY failed with: " + e.message)
        con.rollback()
    else:
        for row in rs:
            counts[row[0]] = row[1]
    try:
        cur.execute(query_ts)
        rs = cur.fetchone()
    except Exception, e:
        logging.exception ("QUERY failed with: " + e.message)
        con.rollback()
    else:
        stats['latest_ts'] = rs[0].strftime('%Y-%m-%d %H:%M:%S')

    stats['num_valid'] = counts.get('Valid', 0)
    stats['num_invalid_as'] = counts.get('InvalidAS', 0)
    stats['num_invalid_len'] = counts.get('InvalidLength', 0)
    stats['num_not_found'] = counts.get('NotFound', 0)

    return stats

def get_validation_tables(dbconnstr):
    try:
        con = psycopg2.connect(dbconnstr)
    except Exception, e:
        logging.exception ("connecting to database, failed with: " + e.message)
        sys.exit(1)
    cur = con.cursor()
    query = "SELECT prefix, origin, state, ts, roas FROM t_validity WHERE state != 'NotFound' ORDER BY origin"
    tables = dict()
    tables['valid'] = list()
    tables['invalid_as'] = list()
    tables['invalid_len'] = list()
    try:
        cur.execute(query)
        rs = cur.fetchall()
    except Exception, e:
        logging.exception ("QUERY failed with: " + e.message)
        con.rollback()
    else:
        for row in rs:
            if row[2] == 'Valid':
                tables['valid'].append([row[0],row[1],row[3]])
            elif row[2] == 'InvalidAS':
                tables['invalid_as'].append([row[0],row[1],row[3]])
            else:
                tables['invalid_len'].append([row[0],row[1],row[3]])

    tables['num_valid'] = len(tables['valid'])
    tables['num_invalid_as'] = len(tables['invalid_as'])
    tables['num_invalid_len'] = len(tables['invalid_len'])
    return tables
