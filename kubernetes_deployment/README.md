# Kubernetes deployment

## Commands

### Namespace

#### Create

Execute the following command to create the namespace with all resources:

```sh
./data-fabric$ kubectl apply -k .
```

#### Read

Execute the following command to get any resource in the namespace:

```sh
kubectl get all --namespace <my-namespace>
```

#### Update

Execute the following command to update any resource in the namespace:

```sh
./data-fabric$ kubectl apply -k .
```

#### Delete

Execute the following command to delete the complete namespace with all its resources:

```sh
kubectl delete namespaces <my-namespace>
```