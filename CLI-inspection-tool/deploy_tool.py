#!/usr/bin/env python3
"""
Kubernetes deployment inspection tool.

Features:
 - List deployments in a namespace with image & timestamp
 - Compare two namespaces for drift (image/version)
 - Trigger optional Trivy scan for security checks

Author: Abhishek Sharma
"""

import sys
import json
import subprocess
from kubernetes import client, config

# Connect to Kubernetes cluster
try:
    config.load_kube_config()
    apps = client.AppsV1Api()
except Exception as err:
    print(f"Failed to load kube config: {err}")
    sys.exit(1)


# Utility: get deployments info
def get_deployments(namespace: str) -> dict:

    """
    Fetch all deployments in a namespace and return
    a dict of {name: {image, updated}}.
    """
    try:
        deployments = apps.list_namespaced_deployment(namespace)
    except client.exceptions.ApiException as e:
        print(f"⚠️  Unable to list deployments in {namespace}: {e}")
        return {}

    data = {}
    for d in deployments.items:
        name = d.metadata.name
        image = d.spec.template.spec.containers[0].image
        updated = d.metadata.creation_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        data[name] = {"image": image, "updated": updated}
    return data



# show command
def show(namespace: str):
    """Display deployments in a namespace."""
    info = get_deployments(namespace)
    print(f"\nNAMESPACE: {namespace}")
    print("--------------------------------------------")
    if not info:
        print("(no deployments found)")
        return
    for name, data in info.items():
        print(f"{name:15} {data['image']:70} {data['updated']}")


# diff command
def diff(ns1: str, ns2: str):
    """Compare two namespaces and show differences."""
    d1 = get_deployments(ns1)
    d2 = get_deployments(ns2)

    print(f"\nComparing {ns1} vs {ns2}\n")

    only_in_ns1 = set(d1) - set(d2)
    only_in_ns2 = set(d2) - set(d1)

    print(f"Deployments only in {ns1}: {', '.join(only_in_ns1) or '(none)'}")
    print(f"Deployments only in {ns2}: {', '.join(only_in_ns2) or '(none)'}\n")

    print("Deployments with different images:")
    diffs = [n for n in d1 if n in d2 and d1[n]['image'] != d2[n]['image']]
    if not diffs:
        print("  - (none)")
    else:
        for name in diffs:
            print(f"  - {name}")
            print(f"      {ns1}: {d1[name]['image']}  (updated: {d1[name]['updated']})")
            print(f"      {ns2}: {d2[name]['image']}  (updated: {d2[name]['updated']})")

    same = [n for n in d1 if n in d2 and d1[n]['image'] == d2[n]['image']]
    print("\nDeployments identical in both namespaces:")
    print("  - " + "\n  - ".join(same) if same else "  - (none)")



# scan command (Trivy)
def scan(namespace: str):
    """
    Run a Trivy scan for container/config/network issues in a namespace.
    Uses the system-installed Trivy CLI.
    """
    cmd = ["trivy", "k8s", "--include-namespaces", namespace, "--report", "summary"]
    print(f"\nRunning Trivy scan for namespace: {namespace}\n")

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print("Trivy not found. Install with: sudo apt install trivy -y")
    except subprocess.CalledProcessError as e:
        print("Trivy scan failed:", e)


# main 
def main():
    if len(sys.argv) < 3:
        print(
            "\nUsage:\n"
            "  python3 k8s_deploy_tool.py show <namespace>\n"
            "  python3 k8s_deploy_tool.py diff <ns1> <ns2>\n"
            "  python3 k8s_deploy_tool.py scan <namespace>\n"
        )
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "show":
        show(sys.argv[2])
    elif cmd == "diff":
        if len(sys.argv) < 4:
            print("Need two namespaces for diff")
            sys.exit(1)
        diff(sys.argv[2], sys.argv[3])
    elif cmd == "scan":
        scan(sys.argv[2])
    else:
        print("Unknown command. Use show / diff / scan.")


if __name__ == "__main__":
    main()

