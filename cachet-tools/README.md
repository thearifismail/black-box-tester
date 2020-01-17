# Cachet Tools
Cachet tools include scripts for populating, updating, and deleting services from a Cachet status page.

## Add New Service

Adding a new service requires adding the new service to `hosted-services.json`, deleting the existing services, and running `populate-cachet.py` script.

## Delete Existing Service

Deleting a service requires deleteing it from `hosted-services.json`, deleting the existing services, and running `populate-cachet.py` script.

This scripts can be executed from anywhere given the required environment variables are provided.

## Environment Variables

The following environment variables are needed.
```
CACHET_HOSTNAME
CACHET_TOKEN
INSIGHTS_SERVER
INSIGHTS_USERNAME
INSIGHTS_PASSWORD
PYTHONWARNINGS = "ignore:Unverified HTTPS request"
```

