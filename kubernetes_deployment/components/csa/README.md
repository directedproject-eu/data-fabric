# CSA Installation for DIRECTED project

The installation of the Connected Systems API (CSA) consists of the following components:

* CSA API - Deployment - `api_*.yaml`
* Elastic Search - StatefulSet - `es_*.yaml`
* TimescaleDB - StatefulSet - `tsdb_*.yaml`

The configuration of each component is maintained in the according manifests prefixed accordingly.

The following secrets MUST be created beforehand:

* `csa-tsdb-user` with keys `username` and `password`.
* `cas-es-user` with keys `username` and `password`.

Certificates for elasticsearch have to be created and pasted into `es_configmap.yaml`.

## Links

* Repository: <https://github.com/directedproject-eu/pygeoapi_csa/>
* Web: <https://<my-host>/csa/>

## Creating Secrets

**Create two files** `.secrets.{tsdb|es}` with the following content:

```ini
username=user
password=your-secret-password-here
```

**Create** the secrets:

```shell
[.components/csa]$ kubectl create secret generic -n <my-namespace> csa-tsdb-user --from-env-file=.secrets.tsdb --dry-run=true  --output=yaml
```

```shell
[.components/csa]$ kubectl create secret generic -n <my-namespace> csa-es-user --from-env-file=.secrets.es --dry-run=true  --output=yaml
```

Remove the last two parameters (`--dry-run`, `--output=yaml`) to really create the secrets.

**Verfiy** the secrets creation:

```shell
kubectl -n <my-namespace> get secrets csa-tsdb-user --template='{{ index .data.username }}' | base64 -d ;\
echo "" ; \
kubectl -n <my-namespace> get secrets csa-tsdb-user --template='{{ index .data.password }}' | base64 -d ; \
echo "" ; \
echo "" ; \
kubectl -n <my-namespace> get secrets csa-es-user --template='{{ index .data.username }}' | base64 -d ;\
echo "" ; \
kubectl -n <my-namespace> get secrets csa-es-user --template='{{ index .data.password }}' | base64 -d
```
