# k8s job manager

Using [pygeoapi-k8s-manager](https://github.com/52North/pygeoapi_k8s-manager).

## Required Credentials

### API Token

* **Create**:

  Execute command:

  ```shell
  kubectl create secret generic -n <my-namespace> k8s-job-manager-token --from-literal=token=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32; echo)
  ```

* **Validate**:

  ```shell
  echo "k8s-job-manager-token.token: '$(kubectl -n <my-namespace> get secrets k8s-job-manager-token --template='{{ .data.token }}' | base64 -d)'"
  ```

* **Delete**:

  ```shell
  kubectl delete secrets -n <my-namespace> k8s-job-manager-token
  ```

### Log Finalizer S3 Credentials

The set-up requires S3 credentials to access the bucket in the OTC cloud.

Retrieve the credentials from the OTC web console via the "My Credentials button" on the top right from a user that has the MOST LIMITED set of permissions required for this deployment!

Create the credentials with the following commands.

Prepare a file `.secrets.otc-s3` with the following layout:

```ini
key=12345678901234567890
secret=1234567890123456789012345678901234567890
```

and execute the following command:

```shell
kubectl create secret generic -n <my-namespace> k8s-job-manager-s3-credentials --from-env-file=.secrets.otc-s3
```

Verify the creation of the secrets via the following command:

```shell
echo "Key    : $(kubectl -n <my-namespace> get secrets k8s-job-manager-s3-credentials --template='{{ .data.key }}' | base64 -d)" && \
echo "Secret : $(kubectl -n <my-namespace> get secrets k8s-job-manager-s3-credentials --template='{{ .data.secret }}' | base64 -d)"
```

Delete the secret with:

```shell
kubectl delete secrets -n <my-namespace> k8s-job-manager-s3-credentials
```
