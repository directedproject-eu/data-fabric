# k8s Namespace → Component → Keycloak

This component provides the namespace [Keycloak][kc_docu] instance.

## Secrets

The set-up requires the following secrets to be configured:

* `keycloak` with keys
  * `keycloak.username`
  * `keycloak.password`
  * `keycloak.db.user`
  * `keycloak.db.password`

### Create

```shell
kubectl create secret generic -n <my-namespace> keycloak \
--from-literal=keycloak_username=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 16; echo) \
--from-literal=keycloak_password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 64; echo) \
--from-literal=keycloak_db_user=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 16; echo) \
--from-literal=keycloak_db_password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 64; echo)
```

### Verify/Check

```shell
echo "Keycloak Username   : '$(kubectl -n <my-namespace> get secrets keycloak --template='{{ .data.keycloak_username }}' | base64 -d)'" && \
echo "Keycloak Password   : '$(kubectl -n <my-namespace> get secrets keycloak --template='{{ .data.keycloak_password }}' | base64 -d)'" && \
echo "Keycloak DB Username: '$(kubectl -n <my-namespace> get secrets keycloak --template='{{ .data.keycloak_db_user }}' | base64 -d)'" && \
echo "Keycloak DB Password: '$(kubectl -n <my-namespace> get secrets keycloak --template='{{ .data.keycloak_db_password }}' | base64 -d)'"
```

<!-- LINKS -->
[kc_docu]: https://www.keycloak.org/getting-started/getting-started-kube
