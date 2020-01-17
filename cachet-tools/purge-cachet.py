#!/usr/bin/env python3

import json
import logging
import requests
import os

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

    response = session.get(URL  + "/groups", verify=False)
    groups   = response.json()['data']
    logger.info("Number of groups found: " + str(len(groups)))

    for group in groups:
        components = group['enabled_components']
        logger.info(group['name'] + " contains " + str(len(components)) + " components")
        for component in components:
            logger.info("Deleting component: " + component['name'])
            cdr = session.delete(URL + "/" + str(component['id']), verify=False, )
            logger.info (cdr)
        # delete the group
        logger.info("Deleting group " + group['name'])
        gdr = session.delete(URL + "/groups/" + str(group['id']), verify=False, )
        logger.info(gdr)

    # check and delete components not in any groups
    response = session.get(URL, verify=False)
    components = response.json()['data']
    logger.info("Number of components not in any group: " + str(len(components)))

    for component in components:
        logger.info("Deleting component: " + component['name'])
        cdr = session.delete(URL + "/" + str(component['id']), verify=False, )
        logger.info (cdr)

    logger.info("Done!!!")
