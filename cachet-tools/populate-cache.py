#!/usr/bin/env python3

import json
import logging
import requests
import pathlib
import os

from services import Services

CACHET_HOSTNAME = os.environ.get("CACHET_HOSTNAME")
URL = f"https://{CACHET_HOSTNAME}/api/v1/components"
HEADERS = {
    'X-Cachet-Token': os.environ.get("CACHET_TOKEN")
}

# setup log format
logging.basicConfig(level='INFO', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p: ')
logger = logging.getLogger(__name__)

with requests.Session() as session:
    session.headers.update(HEADERS)

    groups = Services().getData()

    for group, services in groups.items():
        logger.info(f"Creating group {group}")
        r = session.post(URL + "/groups", verify=False, json={
            "name": group,
            "collapsed": 0,
            "visible": 1
        })
        group_id = r.json()["data"]["id"] 

        for service in services:
            logger.info(service['name']) 

            logger.info(f'Creating service "{service}" under group "{group}" ({group_id})')
            r = session.post(URL, verify=False, json={
                "name": service['label'],
                "group_id": group_id,
                "status": 0
            })
