#!/usr/bin/env python3

import requests
import os
import logging

CACHET_HOSTNAME = os.environ.get("CACHET_HOSTNAME")
URL = f"https://{CACHET_HOSTNAME}/api/v1/components"
HEADERS = {
    'X-Cachet-Token': os.environ.get("CACHET_TOKEN")
}

# setup log format
logging.basicConfig(level='INFO', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p: ')
logger = logging.getLogger(__name__)

groups = {
    "Cloud Services Applications": [
        "webhooks",
        "vulnerability",
        "tower-analytics",
        "topological-inventory",
        "system-baseline",
        "subscriptions",
        "sources",
        "rhsm-subscriptions",
        "remediations",
        "rbac",
        "inventory",
        "insights",
        "ingress",
        "hooks",
        "entitlements",
        "echo",
        "drift",
        "cost-anagement",
        "compliance",
        "catalog",
        "automation-hub",
        "approval",
        "apicast-tests"
    ]
}
with requests.Session() as session:
    session.headers.update(HEADERS)

    for group, services in groups.items():
        logger.info(f"Creating group {group}")
        r = session.post(URL + "/groups", verify=False, json={
            "name": group,
            "collapsed": 0,
            "visible": 1
        })
        group_id = r.json()["data"]["id"]
        for service in services:
            logger.info(f'Creating service "{service}" under group "{group}" ({group_id})')
            r = session.post(URL, verify=False, json={
                "name": service,
                "group_id": group_id,
                # set new service status to Unknown
                # options are: 0=Unknown, 1=Operational, 2=Performance Issues , 3=Partial Outage , 4=Major Outage
                "status": 0
            })
