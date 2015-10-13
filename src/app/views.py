import json
import logging
import sys

from flask import render_template
from app import app

import config
if config.DATABASE_TYPE == 'mongodb':
    from mongodb import get_validation_stats, get_validation_tables
elif config.DATABASE_TYPE == 'postgresql':
    from postgresql import get_validation_stats, get_validation_tables
else:
    logging.critical("unknown database type!")
    sys.exit(1)

@app.route('/about')
def about():
    return render_template("about.html")
@app.route('/')

@app.route('/stats')
def stats():
    stats = get_validation_stats(config.DATABASE_CONN)
    table = [['Validity', 'Count']]
    table.append([ 'Valid', stats['num_valid'] ])
    table.append([ 'Invalid AS', stats['num_invalid_as'] ])
    table.append([ 'Invalid Length', stats['num_invalid_len'] ])
    stats['table_roa'] = table
    table_all = list(table)
    table_all.append([ 'Not Found', stats['num_not_found'] ])
    stats['table_all'] = table_all
    return render_template("stats.html", stats=stats)

@app.route('/tables')
def tables():
    tables = get_validation_tables(config.DATABASE_CONN)
    return render_template("tables.html", tables=tables)
