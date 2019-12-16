#!/usr/bin/env python3

import requests
import os

CACHET_HOSTNAME = os.environ.get("CACHET_HOSTNAME")
URL = f"https://{CACHET_HOSTNAME}/api/v1/components"
HEADERS = {
    'X-Cachet-Token': os.environ.get("CACHET_TOKEN")
}

groups = {
    "Cloud Services Applications": [
        "Cost Management",
        "Approval",
        "Catalog",
        "Cloudigrade",
        "Compliance",
        "Drift",
        "Entitlements",
        "Hooks",
        "Ingress",
        "Inventory",
        "Rbac",
        "Remediations",
        "Rhsm Subscriptions",
        "Sources",
        "Subscriptions",
        "Topological Inventory",
        "Vulnerability",
        "Webhooks",
        "APICast Tests"
    ],
    "Cloud Services Platform": [
        "3scale",
        "Kafka",
        "Prometheus",
        "Alert Manager",
        "Grafana",
        "OC Logs",
        "Elastic Search Exporter",
        "Legacy Infrastructure",
        "Payload Tracker",
    ],
    "Amazon Web Services": [
        "Elastic Search",
        "CloudWatch Lambda Service",
        "RDS",
        "S3",
    ],
    "Akamai": [
        "Akamai",
        "Fakamai"
    ],
    "OSD": [
        "Prod Cluster",
        "Dev Cluster"
    ],
    "IT Managed Services": [
        "BOP",
        "SSO",
        "Entitlements"
    ]
}

with requests.Session() as session:
    session.headers.update(HEADERS)
    for group, services in groups.items():
        print(f"Creating group {group}")
        r = session.post(URL + "/groups", verify=False, json={
            "name": group,
            "collapsed": 1
        })
        group_id = r.json()["data"]["id"]
        for service in services:
            print(f"Creating service {service} under group {group} ({group_id})")
            r = session.post(URL, verify=False, json={
                "name": service,
                "group_id": group_id,
                "status": 1
            })
