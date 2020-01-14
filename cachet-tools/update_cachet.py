"""Cachet Updater
This script updates status in Cachet by first querying Cachet for services,
checks the status, each service discovered, on Insights, and then updates Cachet with
latest status.
"""

import json
import os
import logging
import requests
import time

# target cachet listing insights services 
CACHET_HOSTNAME = os.environ.get("CACHET_HOSTNAME")
CACHET_TOKEN    = os.getenv("CACHET_TOKEN")
CACHET_URL      = f"https://{CACHET_HOSTNAME}/api/v1/components"
HEADERS         = { 'X-Cachet-Token': os.environ.get("CACHET_TOKEN") }

# insights server hosting live services status
INSIGHTS_USERNAME = os.getenv("INSIGHTS_USERNAME")
INSIGHTS_PASSWORD = os.getenv("INSIGHTS_PASSWORD")
INSIGHTS_SERVER   = os.getenv("INSIGHTS_SERVER")
API_URL           = f"https://{INSIGHTS_SERVER}/api"

# format the logger message
logging.basicConfig(level='INFO', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S %p: ')
logger = logging.getLogger(__name__)

# session used by every request, only URLs and args will change
session = requests.Session()

def update_all_services():
    logger.info("Starting services status check ...")

    # session = requests.Session()
    session.headers.update(HEADERS)

    # TODO:  add exception handling and check if except: can catch every exception if none specified to catch
    try:
        response = session.get(CACHET_URL + "/groups", verify=False)
        groups   = response.json()['data']
        logger.info("Number of groups found: " + str(len(groups)))

        for group in groups:  # for somereason not using groups returns 20 components but should return 23
            components = group['enabled_components']
            logger.info("Starting to check each of " + str(len(components)) + " components in group \"" + group['name'] + "\"")
            for component in components:
                # assuming the component in the parent group is accessible because it showed up.
                svc_status = get_service_status(component['name'])
                update_svc = set_svc_status(component['id'], svc_status)
                if update_svc:
                    logger.info("Successfully updated status of \"" + component['name'] + "\" service")
                else:
                    logger.error("Failed to updated status of \"" + component['name'] + "\" service")
                time.sleep(2) 
            # end of for components loop
        # end of for groups loop
    except Exception as ex:
        logger.exception(ex)
    # end of try/except block

    logger.info("Done updating all services!!!")
# end of def update_all_services

def get_service_status(name):
    result = True # set to False if exception thrown
    url = API_URL + "/" + name + "/v1/"
    try:
        response = session.get(url, auth=(INSIGHTS_USERNAME, INSIGHTS_PASSWORD), verify=False, )
        logger.info(str(response.status_code) + " received from " + url)
        return response.status_code
    except requests.exceptions.RequestException as re:
        logger.info("Error reading service \"" + name + "\" from Insights")
        logger.exception(re)
        result = False
# end of def get_service_status

def set_svc_status(id, status):
    result = True # set to by exception handler
    url = CACHET_URL + "/" + str(id)

    try:
        # change status to "Unknown" temporarily before setting the actual status.
        # reason: timestampp is not updated, when before and after status remains the same.
        ret = session.put(url, data={"status": 0}, verify=False)
        ret = session.get(url, verify=False)

        # now set the actual status
        if (status >= 200 and status <= 299): # check for >199 and <300
            actual_status={"status": 1 }
        else:
            actual_status={"status": 4 }
        ret = session.put(url, data=actual_status, verify=False)
        ret = session.get(url, verify=False)
    except requests.exceptions.RequestException as re:
        logging.error("Return Code = %s", str(ret.status_code) + " by resetting or updating the status")
        logger.exception(re)
        result = False
    return result
# end of def set_svc_status

def main():
    while True:
        update_all_services()
        logger.info("Going to sleep for 5 minutes ...")
        time.sleep(300)

if __name__ == '__main__':
   logger.info ("Let's kick the pig!")
   main()
