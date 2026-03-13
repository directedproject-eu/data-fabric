# Forestry data ingestion for DIRECTED project

The following secrets MUST be created beforehand:

* `bucket` with keys `name`, `key` and `secret`.

## Links

* Repository: <https://github.com/directedproject-eu/forestry-data-ingestor>
* Forestry Data: <https://met.boreas.hu/bakonyerdo/index.php>

## Creating Secrets

**Create two files** with the following content:

`.secrets.bucket`:

```ini
name=your-name-here
key=your-key-here
secret=your-secret-here
```

**Create** the secret:

```shell
[.components/forestry_data]$ kubectl create secret generic -n <my-namespace> bucket --from-env-file=.secrets.bucket --dry-run=true  --output=yaml
```

Remove the last two parameters (`--dry-run`, `--output=yaml`) to really create the secrets.

**Verify** the secret creation:

```shell
echo "bucket name  : $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.name }}' | base64 -d)" ;\
echo "bucket key   : $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.key }}' | base64 -d)" ;\
echo "bucket secret: $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.secret }}' | base64 -d)"
```
