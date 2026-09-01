# k8s Namespace → Component → OAuth2 Proxy

We are using oauth2 to protect our applications.
In the end, the components should contains this application with an application specific application.

The set-up contains three applications:

* [keycloak][kc_k8s] - to authenticate and more - 🛠️ (see [its own component][kc_comp])
* [oauth-proxy2][oap_helm] - to protect and serve - ⛑️
* pygeoapi - to be protected - 🛠️

OAuth2 proxy is deployed using helm (⛑️).

## The API to be Protected

For the workshop, we provide data from Zala in GeoJSON files via pygeoapi.
The according manifests are all prefixed with `api_`.
The ingress is used for testing only and is not added to the `kustomization.yaml`.
The data is uploaded manually via [kubectl cp][kubectl_cp] and taken from the project's Google Drive.
The instructions to upload the data:

```shell
POD=$(kubectl get po -o custom-columns=:.metadata.name | grep --color=never oauth2-proxy-api) && \
kubectl cp forest_and_vegetation_fires_events.geojson "<my-namespace>/$POD:/pygeoapi/data/collections/" && \
kubectl cp storm_damage_events.geojson "<my-namespace>/$POD:/pygeoapi/data/collections/" && \
kubectl cp timber_cutting_events.geojson "<my-namespace>/$POD:/pygeoapi/data/collections/" && \
kubectl cp water_damage_events.geojson "<my-namespace>/$POD:/pygeoapi/data/collections/" && \
kubectl exec -it "$POD" -- ls -lha /pygeoapi/data/collections/
```

## Keycloak Configuration

The set-up requires the following secrets to be configured:

* `values.yaml::config.existingSecret` with keys
  * `client-id`
  * `client-secret`
  * `cookie-secret`

### Create Secret

Create a secret `.secrets.oauth-client` file to be used during secret creation to not leak information in the shell history:

```ini
client-id=
client-secret=
```

Create the secret with the following command using the identifier from the `values.yaml::config.existingSecret`:

```shell
echo "cookie-secret=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32; echo)" >> .secrets.oauth-client \
&& kubectl create secret generic protected-api \
       -n <my-namespace> \
       --from-env-file=.secrets.oauth-client \
&& head -n -1 .secrets.oauth-client > temp.txt && mv temp.txt .secrets.oauth-client
```

### Verify

```shell
echo "Client ID     : '$(kubectl -n <my-namespace> get secrets protected-api --template='{{ index .data "client-id" }}' | base64 -d)'" && \
echo "Client Secret : '$(kubectl -n <my-namespace> get secrets protected-api --template='{{ index .data "client-secret" }}' | base64 -d)'" && \
echo "Cookie Secret : '$(kubectl -n <my-namespace> get secrets protected-api --template='{{ index .data "cookie-secret" }}' | base64 -d)'"
```

## Helm Instructions

### Installation

1. Add repo for oauth2-proxy:

   ```shell
   helm repo add oauth2-proxy https://oauth2-proxy.github.io/manifests \
   && helm repo update
   ```

1. List latest version available:

   ```shell
   helm search repo oauth2-proxy --versions --version '>10.7.0'
   ```

1. Save (possible) config values:

   ```shell
   helm show values oauth2-proxy/oauth2-proxy --version 10.7.0 > values-reference.yaml
   ```

1. Create deployment specific config values in `values.yaml`.

1. Install chart using our adjusted values:

   ```shell
   helm install -f values.yaml --namespace <my-namespace> --version 10.7.0 protected-api oauth2-proxy/oauth2-proxy
   ```

   Watch the installation status with the following command:

   ```shell
   kubectl --namespace <my-namespace> get pods -l "app=oauth2-proxy"
   ```

### Management

Update with new values:

```shell
helm upgrade --values values.yaml protected-api oauth2-proxy/oauth2-proxy --version 10.7.0
```

Upgrade to new version after checking for available versions and compare new reference-values:

```shell
helm upgrade protected-api oauth2-proxy/oauth2-proxy --reset-then-reuse-values -f values.yaml --install --version <version>
```

<!-- LINKS -->
[kc_k8s]: https://www.keycloak.org/getting-started/getting-started-kube
[kc_comp]: ../keycloak/
[kubectl_cp]: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_cp/
[oap_helm]: https://github.com/oauth2-proxy/manifests
