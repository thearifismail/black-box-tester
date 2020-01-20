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

## Cachet Updater Deployment
Deploying cachet-upater requires creating a new-app, which by default uses a git repo. Even for a local repo, OpenShift attempts to connect to the remote repo in `github`.  Connecting to remote repo requires authentication.  Authenticating with gitrepo by OpensShift requires creating a secret holding username and password in the same namespace and linking it to builder in OpenShift.  The next time new-app is created, OpenShift uses this secret for authenticating with `github`

```
oc create secret generic <SECRET_NAME> --from-literal=username=<GITHUB_USERNAME --from-literal=password=<GITHUB_PASSWORD> -n <NAMESPACE>
oc secrets link builder <SECRET_NAME>
oc create secret <secret containg values of environment variables, CACHET_HOSTNAME, CACHET_TOKEN, INSIGHTS_SERVER, INSIGHTS_USERNAME, INSIGHTS_PASSWORD, and PYTHONWARNINGS>
oc new-app ...

If the build does not complete successfully, check the environment variables in deployment configuration.
```

More to follow. 

