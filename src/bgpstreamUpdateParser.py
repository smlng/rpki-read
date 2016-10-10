#!/usr/bin/python

import argparse
import calendar
import json
import logging
import os
import random
import re
import socket
import string
import sys
import time

import multiprocessing as mp

from datetime import datetime

from settings import *
from BGPmessage import *

def output(queue):
    """Output parsed BGP messages as JSON to STDOUT"""
    logging.info ("CALL output")
    while True:
        odata = queue.get()
        if (odata == 'STOP'):
            break
        json_str = json.dumps(odata.__dict__)
        print json_str
        sys.stdout.flush()
    return True

def main():
    """The main loop"""
    parser = argparse.ArgumentParser(description='', epilog='')
    parser.add_argument('-l', '--loglevel',
                        help='Set loglevel [DEBUG,INFO,WARNING,ERROR,CRITICAL].',
                        type=str, default='ERROR')
    parser.add_argument('-a', '--addr',
                        help='Address or name of BGPmon host.',
                        type=str, default=DEFAULT_BGPMON_SERVER['host'])
    parser.add_argument('-p', '--port',
                        help='Port of BGPmon Update XML stream.',
                        type=int, default=DEFAULT_BGPMON_SERVER['uport'])
    parser.add_argument('-r', '--ribport',
                        help='Port of BGPmon RIB XML stream.',
                        type=int, default=DEFAULT_BGPMON_SERVER['rport'])
    args = vars(parser.parse_args())

    numeric_level = getattr(logging, args['loglevel'].upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level,
                        format='%(asctime)s : %(levelname)s : %(message)s')

    port = args['port']
    addr = args['addr'].strip()

    logging.info("START")

    output_queue = mp.Queue()
    ot = mp.Process(target=output,
                    args=(output_queue,))
    rt = mp.Process(target=recv_bgpmon_rib,
                    args=(addr,args['ribport'], output_queue))
    try:
        ot.start()
        if args['ribport'] > 0:
            rt.start()
        recv_bgpmon_updates(addr,port,output_queue)
    except KeyboardInterrupt:
        logging.exception ("ABORT")
    finally:
        output_queue.put("STOP")

    if args['ribport'] > 0:
        rt.terminate()
    ot.join()
    logging.info("FINISH")
    # END

if __name__ == "__main__":
    main()
