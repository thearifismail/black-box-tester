#!/usr/bin/env python3

import json
import os
import requests

INSIGHTS_USERNAME = os.environ.get("INSIGHTS_USERNAME")
INSIGHTS_PASSWORD = os.environ.get("INSIGHTS_PASSWORD")
INSIGHTS_SERVER   = os.environ.get("INSIGHTS_SERVER")

API_URL           = f"https://{INSIGHTS_SERVER}/api"

services = [                        # Service names in GUI
        "apicast-tests",            # APICast Tests
        "approval",                 # Approval",
        "automation-hub",           # Automation Hub
        "catalog",                  # Catalog",
        "compliance",               # Compliance
        "cost-anagement",           # Cost Management,
        "drift",                    # Drift
        "echo",                     # Echo
        "entitlements",             # Entitlements
        "hooks",                    # Hooks
        "ingress",                  # Ingress
        "insights",                 # Insights
        "inventory",                # Inventory
        "rbac",                     # Rbac
        "remediations",             # Remediations
        "rhsm-subscriptions",       # Rhsm Subscriptions
        "sources",                  # Sources
        "subscriptions",            # Subscriptions
        "system-baseline",          # System Baseline
        "topological-inventory",    # Topological Inventory
        "tower-analytics",          # Tower Analytics
        "vulnerability",            # Vulnerability
        "webhooks"                  # Webhooks
    ]

with requests.Session() as session:
    for service in services:
        url = API_URL + "/" + service + "/v1/"
        print(url)
        response = session.get(url, auth=(INSIGHTS_USERNAME, INSIGHTS_PASSWORD))
        print("returned: " + str(response.status_code))
    print("Done!!!")
