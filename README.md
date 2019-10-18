# black-box-tester
Runs the black box tests for SRE monitoring

This spins up two deployments:
* `black-box-runner` -- runs the `iqe-tests` docker image, and executes `src/runner.py`
* `selenium` -- runs selenium web driver pods used for UI testing

The black box runner runs tests for the IQE plugin and test marker defined in `src/runner.py`

It will scale up the number of selenium pods to match the number of plugins that need to be tested, and allocate a selenium pod for each plugin. The tests for each plugin then run in a thread.

## Deployment

First, switch into the project you want to deploy into:
```
oc project <my_project>
```

Collect the username/password for the Insights prod account that these tests should use. The latest username/password can be obtained from the QE team.

Convert the username/password into base64:
```
echo "my_username" | base64
echo "my_password" | base64
```

Edit the iqe creds secret and update the username/password:
```
cp iqe-creds-secret-example.yaml .iqe-creds.yaml
vi .iqe-creds.yaml
oc create -f .iqe-creds.yaml
```


Next you need a pull secret that can access the `quay.io/cloudservices` registry.

Download the docker config json from quay for an account that has access to the `quay.io/cloudservices/iqe-tests` repository:
1) Log in to https://quay.io/organization/cloudservices
2) Click on `Robot Accounts`
3) Click on `cloudservices+black_box`
4) Click on `Docker Configuration`
5) Click on `Download cloudservices-black-box-auth.json`

then create a secret using it:
```
oc create secret generic cloudservices-black-box-pull-secret --from-file=.dockerconfigjson=cloudservices-black-box-auth.json --type=kubernetes.io/dockerconfigjson
```

Now to deploy the black box runner, run:
```
./deploy.sh
```

You can run the command with `--debug` to enable debug logging on the runner pod, and/or with `--reset` which will delete the selenium deployment and re-create it.


If you want to update the runner script, edit the code in `src` and simply run `deploy.sh` again.
