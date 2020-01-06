"""Cachet Update Daemon
This script updates status in Cachet by first querying Cachet for services.
Checks the status each service discovered and then updates Cachet with 
latest status.

Check if the following comment is true.
The only configuration that needs to be done is to export the cachet
URL and the cachet X token as ENV variables.  Example:

export CACHET_URL="cachet.cachet.svc"
export CACHET_TOKEN="fXPydfUD3c1aBUGiQnSb"
"""
import json
import os
import logging
import requests

# target cachet listing insights services 
CACHET_HOSTNAME = os.environ.get("CACHET_HOSTNAME")
CACHET_TOKEN    = os.getenv("CACHET_TOKEN")
URL             = f"https://{CACHET_HOSTNAME}/api/v1/components"
HEADERS         = { 'X-Cachet-Token': os.environ.get("CACHET_TOKEN") }

# insights server hosting live services status
INSIGHTS_USERNAME = os.getenv("INSIGHTS_USERNAME")
INSIGHTS_PASSWORD = os.getenv("INSIGHTS_PASSWORD")
INSIGHTS_SERVER   = os.getenv("INSIGHTS_SERVER")
API_URL           = f"https://{INSIGHTS_SERVER}/api"

logging.basicConfig(level='INFO', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p: ')
logger = logging.getLogger(__name__)

# check status
def check_status():
    logger.info("Entring check_status ...")
    
    with requests.Session() as session: # try with session 1 and session 2
        session.headers.update(HEADERS)

        response = session.get(URL  + "/groups", verify=False)
        groups   = response.json()['data']
        logger.info("Number of groups found: " + str(len(groups)))

        for group in groups:
            components = group['enabled_components']
            logger.info(group['name'] + " contains " + str(len(components)) + " components")
            for component in components:
                svc_name = component['name']
                svc_id   = component['id']
                # component_id   = component['id']
                logger.info("Browsing component: " + svc_name + " ID: " + str(svc_id))
                cdr = session.get(URL + "/" + str(svc_id), verify=False, )
                logger.info (cdr)

                if (cdr.status_code == 200): # check for >199 and <300
                    url = API_URL + "/" + svc_name + "/v1/"
                    logger.info("Checking status: " + url)
                    response = session.get(url, auth=(INSIGHTS_USERNAME, INSIGHTS_PASSWORD), verify=False)
                    logger.info(response.status_code) 

                    if (response.status_code == 200):
                        somestr={"status": 1 }
                    else:
                        somestr={"status": 4 }

                    url = URL + "/" + str(svc_id)
                    try:
                        # ret = session.post(url, data['source_name']="Unknown", verify=False)
                        ret = session.put(url, data=somestr, verify=False)
                        logger.info(str(ret))
                        ret = session.get(url, verify=False)
                        # updated_svc = ret.json()
                    except requests.exceptions.RequestException as update_exception:
                        logging.error("Return Code = %s", str(ret.status_code))
                        logging.exception(update_exception)
                    # end of if response_code
    logger.info("Done!!!")

def main():
    logger.info ("Using logger to get started!")
    logger.info (check_status())

# end of main function

if __name__ == '__main__':
    main()
