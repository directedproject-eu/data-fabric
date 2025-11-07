# RIM2D - Image

Build image:

```shell
TAG=<my-tag>; docker build -t "<my-container-registry>/<my-image-name>:$TAG" .
```

Upload image to container registry.

Trigger async execution

```shell
curl -X 'POST' \
  'https://<my-host>/k8s-jobs/processes/rim2d-rimini-pluvial/execution' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Prefer: respond-async' \
  -d "{
  \"inputs\": {
    \"token\": \"$(kubectl -n <my-namespace> get secrets k8s-job-manager-token --template='{{ .data.token }}' | base64 -d)\"
  }
}"
```
