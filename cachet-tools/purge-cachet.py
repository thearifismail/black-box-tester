#!/usr/bin/env python3

import requests
import os
import json

CACHET_HOSTNAME = os.environ.get("CACHET_HOSTNAME")
URL = f"https://{CACHET_HOSTNAME}/api/v1/components"
HEADERS = { 
    'X-Cachet-Token': os.environ.get("CACHET_TOKEN")
}

with requests.Session() as session:
    session.headers.update(HEADERS)

    response = session.get(URL  + "/groups", verify=False)
    groups   = response.json()['data']
    print("Number of groups found: " + str(len(groups)))

    for group in groups:
        components = group['enabled_components']
        print(group['name'] + " contains " + str(len(components)) + " components")
        for component in components:
            print("Deleting component: " + component['name'])
            cdr = session.delete(URL + "/" + str(component['id']), verify=False, )
            print (cdr)
        # delete the group
        print("Deleting group " + group['name'])
        gdr = session.delete(URL + "/groups/" + str(group['id']), verify=False, )
        print(gdr)

    # check and delete components not in any groups
    response = session.get(URL, verify=False)
    components = response.json()['data']
    print("Number of components not in any group: " + str(len(components)))

    for component in components:
        print("Deleting component: " + component['name'])
        cdr = session.delete(URL + "/" + str(component['id']), verify=False, )
        print (cdr)

    print("Done!!!")
