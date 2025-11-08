
# Microk8s Deployment Diff & Security Tool

A Python CLI tool that interacts with the Kubernetes API to:
- List Deployments within a namespace (`show`)
- Compare Deployments between two namespaces (`diff`)
- Perform basic security checks (`scan`)


## Purpose

This tool automates visibility across multiple namespaces — showing where deployments or image versions differ and running basic configuration and vulnerability checks.  
It was developed as part of a DevOps practical project.

## TL;DR
Run:
```bash
python3 deploy_tool.py show ns-a
python3 deploy_tool.py diff ns-a ns-b
python3 deploy_tool.py scan ns-a
```

## Setup Instructions

1. Prerequisites

- Python 3.x
- microk8s + kubectl configured
- pip and kubernetes Python SDK
- Trivy (for vulnerability scanning)


2. Quick start 

> Tested on Ubuntu-based environments with MicroK8s.

- Install dependencies:

```bash
sudo apt update
sudo apt install python3-pip -y
pip install kubernetes
sudo apt install trivy -y

- Configure MicroK8s access
 microk8s config > ~/.kube/config
```

3. Clone this repo
```bash
git clone <https://github.com/Abhi2897/DevOps-Test-Project.git>
cd microservices-demo/CLI-inspection-tool
```
4. Show deployments
```bash
python3 deploy_tool.py show ns-a 
python3 deploy_tool.py show ns-b
- or can be execute 
./deploy_tool.py show ns-a 
./deploy_tool.py show ns-b
```
> Displays a table with:
  - Deployment name
  - Images used
  - Date updated

```bash
 Output
<!--
NAMESPACE: ns-a
--------------------------------------------
adservice       us-central1-docker.pkg.dev/google-samples/microservices-demo/adservice:v0.10.3 2025-11-07T15:38:47Z
cartservice     us-central1-docker.pkg.dev/google-samples/microservices-demo/cartservice:v0.10.3 2025-11-07T15:38:47Z
checkoutservice us-central1-docker.pkg.dev/google-samples/microservices-demo/checkoutservice:v0.10.3 2025-11-07T15:38:46Z
```

6. Compare two namespaces
```bash
python3 deploy_tool.py diff ns-a ns-b
- or can be execute 
./deploy_tool.py diff ns-a ns-b
```

> Compare and show Deployments between two namespaces
  - Deployments only in ns-a
  - Deployments only in ns-b
  - Deployments with different images

```bash Output
Comparing ns-a vs ns-b

Deployments only in ns-a: emailservice, checkoutservice
Deployments only in ns-b: (none)

Deployments with different images:
  - cartservice
      ns-a: us-central1-docker.pkg.dev/google-samples/microservices-demo/cartservice:v0.10.3  (updated: 2025-11-07T15:38:47Z)
```


7. Run Trivy security scan
```bash
python3 deploy_tool.py scan ns-a
- or can be execute 
./deploy_tool.py scan ns-a
```

> Performs basic security checks:
  - Image CVE scan via Trivy (HIGH/CRITICAL severity)
  - Pod security: privileged containers, root user, privilege escalation
  - Network checks: verifies if NetworkPolicies exist and Ingress 
  - RBAC checks

```bash Output 
Running Trivy scan for namespace: ns-a

2025-11-08T22:57:20Z    INFO    Node scanning is enabled
2025-11-08T22:57:20Z    INFO    If you want to disable Node scanning via an in-cluster Job, please try '--disable-node-collector' to disable the Node-Collector job.
2025-11-08T22:57:20Z    INFO    [vulndb] Need to update DB
2025-11-08T22:57:20Z    INFO    [vulndb] Downloading vulnerability DB...
2025-11-08T22:57:20Z    INFO    [vulndb] Downloading artifact...        repo="mirror.gcr.io/aquasec/trivy-db:2"
```

---------------------------------------------------------------------

## Troubleshooting

- Ensure microk8s config > ~/.kube/config are set.
- Verify namespaces exist: kubectl get ns.
- If Trivy fails due to disk space, clean /var/lib/snapd/cache or increase the volume.
- If no output appears, ensure your Python environment can access kubectl and trivy binaries.

## Project Structure
- CLI-inspection.py  
   - deploy_tool.py
   - requirements.txt
   - README.md

