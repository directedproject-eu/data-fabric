# GeoSphere forecast data ingestion for DIRECTED project

The following secrets MUST be created beforehand:

* `bucket` with keys `name`, `key` and `secret`.

## Links

* Repository: <https://github.com/directedproject-eu/geosphere-ingestor/>
* GeoSphere dataset description: <https://data.hub.geosphere.at/dataset/nwp-v1-1h-2500m>

## Creating Secrets

**Create one file** with the following content:

`.secrets.bucket`:

```ini
name=your-name-here
key=your-key-here
secret=your-secret-here
```

**Create** the secrets:

```shell
[.components/geosphere_data]$ kubectl create secret generic -n <my-namespace> bucket --from-env-file=.secrets.bucket --dry-run=true  --output=yaml
```

Remove the last two parameters (`--dry-run`, `--output=yaml`) to really create the secrets.

**Verify** the secrets creation:

```shell
echo "bucket name  : $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.name }}' | base64 -d)" ;\
echo "bucket key   : $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.key }}' | base64 -d)" ;\
echo "bucket secret: $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.secret }}' | base64 -d)"
```
