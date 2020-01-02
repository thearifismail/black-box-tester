#!/usr/bin/env python3

import json
import os
import requests

INSIGHTS_USERNAME = os.environ.get("INSIGHTS_USERNAME")
INSIGHTS_PASSWORD = os.environ.get("INSIGHTS_PASSWORD")
INSIGHTS_SERVER   = os.environ.get("INSIGHTS_SERVER")

API_URL           = f"https://{INSIGHTS_SERVER}/api"

services = [                        
        "apicast-tests",
        "approval",
        "automation-hub",
        "catalog",
        "compliance",
        "cost-anagement",
        "drift",
        "echo",
        "entitlements",
        "hooks",
        "ingress",
        "insights",
        "inventory",
        "rbac",
        "remediations",
        "rhsm-subscriptions",
        "sources",
        "subscriptions",
        "system-baseline",
        "topological-inventory",
        "tower-analytics",
        "vulnerability",
        "webhooks"
    ]

with requests.Session() as session:
    for service in services:
        url = API_URL + "/" + service + "/v1/"
        print(url)
        response = session.get(url, auth=(INSIGHTS_USERNAME, INSIGHTS_PASSWORD))
        print("returned: " + str(response.status_code))
    print("Done!!!")
