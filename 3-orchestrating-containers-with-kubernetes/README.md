# Week 3 - Orchestrating Containers with Kubernetes
This lab walks you through 
- Using Kubernetes `kubectl` client
- Creating Kubernetes resources to run your application
- Exposing applications
- Using Helm package manager

## 0 - Install Kubernetes
- Docker Desktop: 
If you have been using Docke Desktop, you can turn on Kubernetes by following [this documentation](https://docs.docker.com/desktop/kubernetes/#turn-on-kubernetes)

- Rancher Desktop: 
[Enable Kubernetes](https://rancherdesktop.io/) for Rancher Desktop

## 1 - Clone Repo
1. In AWS CloudShell, clone the workshop repository with the command below
  
    ```
    git clone https://github.com/kordaralabs/free-containers-workshop.git
    cd free-containers-workshop
    ```
    
2. Change directory to `3-orchestrating-containers-with-kubernetes`

    `3-orchestrating-containers-with-kubernetes`

## 2 - Explore Popular kubernetes resource types
### 2.1 - Pods

- Create an Ubuntu with the `ubuntu-pod.yaml` manifest file. The `tail` command ensures that the container does not exit since there are no servers or applications to keep it running indefinitely.
  
`kubectl apply -f ubuntu-pod.yaml`

- See pods in default namespace

`kubectl get pods`

- Describe the ubuntu pod that was just created.

`kubectl describe pod ubuntu`

- Delete the ubuntu pod

`kubectl delete pod ubuntu`

### 2.2 - Deployment 

- Create the deployment
  
`kubectl apply -f ubuntu-pod.yaml`

- Show all deployments in the namespace
  
`kubectl get deployments`

- Describe deployment to see additional info and events
  
`kubectl describe deployment nginx-demo`

- Show all pods
  
`kubectl get pods`

- Show pods in the `nginx-demo` deployment using the label `tier: frontend`

`kubectl get pods -l tier=frontend`

- Show `replicaset` of the deployment

`kubectl get replicaset`

### 2.3 - Service
Traffic can be sent to pods in the `nginx-demo` Deployment through the Kubernetes Service resource below. The service resource collates the IP address of all pods that matches the `tier: frontend` label in the Service manifest and on the `nginx-demo` pods.

- Create the service

`kubectl apply -f service.yaml`

- See all services in the default namespace. Grab the `EXTERNAL-IP` of `nginx-test` Service from the output. It will be used to test service.

`kubectl get services`

- Test the LoadBalancer Service by visiting `<EXTERNAL-IP>:8000` in a web browser

- Describe the `nginx-test` service

`kubectl describe service nginx-test`

- See the IPs/Endpoints that the service will forward traffic to. IPs shown will be the IPs of the two pods in the deployment

`kubectl get endpoints nginx-test`

### 2.4 - Ingress
Unlike LoadBalancer Services, Ingress resources require an Ingress Controller to configure the HTTP routes. Steps below walk you through creating an Ingress however, you will be unable to acess the application. See step `5.3` where the Nginx Ingress Controller is installed to support creation of Ingress resources.

- Create an Ingress resource

`kubectl apply -f ingress.yaml`

- See all Ingress in the default namespace

`kubectl get ingress`

- Describe an Ingress resource
  
`kubectl describe ingress nginx`

- Delete an Ingress resource

`kubectl delete ingress nginx`

### 2.5 - Cleanup 

- Delete the pod

`kubectl pod ubuntu`

- Delete the service

`kubectl delete service nginx-test`

- Delete the deployment
  
`kubectl delete deployment nginx-demo`

### 2.6 - Using manifest files with multiple resources
In previous examples, seperate files have been used to create the deployments, services, etc. ALl these resources can be combined in a single manifest file, here such file has been named `manifest.yaml`.

- Create resources using the manifest file

`kubectl apply -f manifest.yaml`

- Delete all resources provisioned with the manifest file
  
`kubectl delete -f manifest.yaml`

## 3 - Working with multiple clusters
### 3.1 - Show all Kubernetes clusters
- The command below can be used to get all the clusters that have been configured with `kubectl` on your machine
```
$ kubectl config get-contexts
```

The output of such command could look like this. In this example `rancher-desktop` is the current Kubernetes cluster in use.
```
CURRENT   NAME              CLUSTER           AUTHINFO          NAMESPACE
          docker-desktop    docker-desktop    docker-desktop
*         rancher-desktop   rancher-desktop   rancher-desktop
```

### 3.2 - Change cluster in use
The command below can be used to set the Kubernetes cluster to use

`kubectl config use-context <context name>`

```
$ kubectl config use-context docker-desktop
Switched to context "docker-desktop".
```

### 3.3 - Kube Config file
- Linux/Mac
 
`cat ~/.kube/config`

- Windows Powershell

```
cd ~\.kube
notepad config
```

## 4 - Helm
Helm is a package manager manager for Kubernetes. It makes deploying applications with multiple components easy

### 4.1 - Install 
Helm can be installed using instructions from this [documentation](https://helm.sh/docs/intro/install/)

### 4.2 - Commons Helm commands

`helm list` - Show all applications installed with Helm in all namespaces

`helm install [NAME] [CHART] [flags]` - Install an application with Helm

`helm upgrade [RELEASE] [CHART] [flags]` - Upgrade an application installed with Helm 

`helm uninstall RELEASE_NAME` - Uninstall an applciation installed with Helm

Note: These popular Helm commands are scoped to namespaces, so add the `-n <namespace>` to target a Kubernetes namespace

## 5 - Controllers
### 5.1 - Install the Nginx Ingress Controller with Helm
The [Nginx Ingress Controller](https://docs.nginx.com/nginx-ingress-controller/intro/overview/) is used to manage Ingress Resources. It can be installed with Helm in the `ingress-nginx` namespace with the command below.

`helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx --namespace ingress-nginx --create-namespace`

### 5.2 - Test the controller
- Install the a sample Nginx chart from the `nginx-demo` directory using the commands below
  
`helm install demo nginx-demo`

- Follow instructions in the Helm Notes to reach and test the application

## 5.3 - Cleanup
- Remove the nginx-demo application installed with Helm
  
`helm uninstall demo`

- Remove the Nginx Ingress Controller
  
`helm uninstall ingress-nginx -n ingress-nginx`