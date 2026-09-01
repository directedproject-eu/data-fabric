# "Secure" GeoServer

Start with official base image:

```shell
docker pull docker.osgeo.org/geoserver:3.0.1
```

## Required k8s Resources

* statefulset vs deployment:
  * geoserver
* ingress
* storage:
  * geoserver datadir

## Create GeoServer Admin Credentials as k8s Secrets

**Create file** `.secrets` with the following command:

```shell
echo -e "\
  username=admin-$(tr -dc A-Za-z0-9 </dev/urandom | head -c 30; echo)\n\
  password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 64; echo)" \
  > .secrets
```

```ini
username=admin
password=your-secret-password-here
```

**Create** the secret:

```shell
[.components/secure-geoserver]$ kubectl create secret generic -n <my-namespace> secure-geoserver-admin --from-env-file=.secrets --dry-run=true  --output=yaml
```

Remove the last two parameters (`--dry-run`, `--output=yaml`) to really create the secret.

**Verify** the secret creation:

```shell
kubectl -n <my-namespace> get secrets secure-geoserver-admin --template='{{ index .data.username }}' | base64 -d ;\
echo "" ; \
kubectl -n <my-namespace> get secrets secure-geoserver-admin --template='{{ index .data.password }}' | base64 -d
```

**Share** the secret via a secure channel.

## Create GeoServer

```shell
[.components/secure_geoserver]$ kubectl apply -k . && kubectl get events --watch
```

## Clean-Up GeoServer Objects

With secrets:

```shell
[.components/secure_geoserver]$ kubectl delete -k . \
&& kubectl delete secrets secure-geoserver-admin \
&& kubectl delete pvc storage-secure-geoserver-0
```

Without secrets:

```shell
[.components/secure_geoserver]$ kubectl delete -k . \
&& kubectl delete pvc storage-secure-geoserver-0
```

## Configure Keycloak and GeoServer

This configures GeoServer following the [official keycloak configuration instructions](https://docs.geoserver.org/main/en/user/extensions/oidc/oauth2/keycloak/) using the keycloak instance provided from [`../keycloak/`](../keycloak/README.md).

### Keycloak Client

1. Login at keycloak to master realm.

1. Go to <my-realm> realm clients

1. Add new client
   1. General Settings
      * Client Type: OpenID Connect
      * Client ID: `secure-geoserver`
      * Name: `GeoServer`
      * Description: `Secured GeoServer`
      * Always display in UI: off
   2. Capability config
      * Client authentication: On
      * Authorization: Off
      * Authentication Flow (only active listed):
        * Standard flow
        * Direct access grants
   3. Login settings
      * Root URL: `<my-host>/secure/geoserver/`
      * Home URL:
      * Validation redirect URIs:
        * `<my-host>/secure/geoserver/web/login/oauth2/code/<my-realm>-keycloak__oidc`
        * `<my-host>/*`
           Should/could be limited to applications really needing access.
      * Valid post logout redirect URIs: `<my-host>/secure/geoserver/web/`
      * Web origins: `+`

1. Add roles to the new client
   1. Add role with name `geoserverAuthenticatedUser`
   1. Check mapper…
   1. Might not be required, or maybe better specified as `<my-realm>GeoserverUser`…

### GeoServer Security Configuration

1. Login as admin.

2. Add new authentication Filter via Security → Authentication → Add new authentication filter → Open Id Connect Login.

   * Name: `<my-realm>-keycloak`
   * Client-ID: see above
   * Client-Secret: Retrieve from above
   * OpenID discovery document: <my-host>/auth/realms/<my-realm>/.well-known/openid-configuration
   * Authorization
     * Role Source Resolution: ID Token
     * JSON Path: `resource_access.secure-geoserver.roles`
     * Role Converter Map: `geoserverAuthenticatedUser=ROLE_AUTHENTICATED`
     * Only allow External Roles that are explicitly named above: On

