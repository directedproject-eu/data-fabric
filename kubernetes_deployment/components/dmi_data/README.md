# DMI forecast data ingestion for DIRECTED project

The following secrets MUST be created beforehand:

* `dmi-user` with keys `key`.
* `bucket` with keys `name`, `key` and `secret`.

## Links

* Repository: <https://github.com/directedproject-eu/dmi-ingestor/>
* DMI Open Data: <https://opendatadocs.dmi.govcloud.dk/DMIOpenData/>

## Creating Secrets

**Create two files** with the following content:

`.secrets.dmi`:

```ini
key=your-secret-key-here
```

For different DMI APIs, separate keys are needed. We use the `forecastedr` API.

`.secrets.bucket`:

```ini
name=your-name-here
key=your-key-here
secret=your-secret-here
```

**Create** the secrets:

```shell
[.components/dmi_data]$ kubectl create secret generic -n <my-namespace> dmi-user --from-env-file=.secrets.dmi --dry-run=true  --output=yaml
```

```shell
[.components/dmi_data]$ kubectl create secret generic -n <my-namespace> bucket --from-env-file=.secrets.bucket --dry-run=true  --output=yaml
```

Remove the last two parameters (`--dry-run`, `--output=yaml`) to really create the secrets.

**Verify** the secrets creation:

```shell
echo "user key     : $(kubectl -n <my-namespace> get secrets dmi-user --template='{{ index .data.key }}' | base64 -d)" ;\
echo "bucket name  : $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.name }}' | base64 -d)" ;\
echo "bucket key   : $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.key }}' | base64 -d)" ;\
echo "bucket secret: $(kubectl -n <my-namespace> get secrets bucket --template='{{ index .data.secret }}' | base64 -d)"
```
