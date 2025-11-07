# GeoServer for DIRECTED

Start with official base image:

```shell
docker pull docker.osgeo.org/geoserver:2.27.1
```

## Required k8s Resources

* statefulset vs deployment:
  * geoserver
* ingress
* storage:
  * geoserver datadir

* Variables for community extensions:

  * `COMMUNITY_EXTENSIONS`: `cog-s3,s3-geotiff`
  * `COMMUNITY_PLUGIN_URL`, default: <https://build.geoserver.org/geoserver/2.25.x/community-latest>

## Create GeoServer Admin Credentials as k8s Secrets

**Create file** `.secrets` with the following content:

```ini
username=admin
password=your-secret-password-here
```
[README.md](README.md)
**Create** the secret:

```shell
[.components/geoserver]$ kubectl create secret generic -n <my-namespace> geoserver-admin --from-env-file=.secrets --dry-run=true  --output=yaml
```

Remove the last two parameters (`--dry-run`, `--output=yaml`) to really create the secret.

**Verify** the secret creation:

```shell
kubectl -n <my-namespace> get secrets geoserver-admin --template='{{ index .data.username }}' | base64 -d ;\
echo "" ; \
kubectl -n <my-namespace> get secrets geoserver-admin --template='{{ index .data.password }}' | base64 -d
```

## Create GeoServer

```shell
[.components/geoserver]$ kubectl apply -k . && kubectl get events --watch
```

## Clean-Up GeoServer Objects

With secrets:

```shell
[.components/geoserver]$ kubectl delete -k . \
&& kubectl delete secrets geoserver-admin \
&& kubectl delete pvc geoserver-storage-0
```

Without secrets:

```shell
[.components/geoserver]$ kubectl delete -k . \
&& kubectl delete pvc geoserver-storage-0
```
