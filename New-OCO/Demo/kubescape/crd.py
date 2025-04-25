import json
import time
from flask import Flask, Response
from prometheus_client import Gauge, CollectorRegistry, generate_latest
from kubernetes import client, config
from kubernetes.client.rest import ApiException

app = Flask(__name__)
registry = CollectorRegistry()

# Define Prometheus gauges
severity_gauge = Gauge(
    'failed_resources_severity',
    'Count of failed issues by severity',
    ['severity'],
    registry=registry
)
resource_issues_gauge = Gauge(
    'failed_resource_issues',
    'Issues for failed resources',
    ['resource', 'issue_name'],
    registry=registry
)
remediation_gauge = Gauge(
    'failed_resource_remediations',
    'Remediations for failed resource issues',
    ['resource', 'issue_name', 'remediation', 'control_id', 'remediation_url', 'kind', 'namespace'],
    registry=registry
)

def map_score_to_severity(score_factor):
    """Map scoreFactor to severity level."""
    if score_factor <= 3:
        return "Low"
    elif score_factor <= 6:
        return "Medium"
    else:
        return "High"

def parse_resource_id(resource_id):
    """Parse resourceID to extract kind, namespace, and name."""
    if '//' in resource_id:
        _, right = resource_id.split('//', 1)
        parts = right.split('/')
        kind = parts[0]
        name = '/'.join(parts[1:])
        namespace = "cluster-wide"
    else:
        parts = resource_id.strip('/').split('/')
        if len(parts) >= 4:
            namespace = parts[2]
            kind = parts[3]
            name = '/'.join(parts[4:])
        else:
            kind = 'Unknown'
            namespace = 'Unknown'
            name = resource_id
    return kind, namespace, name

def fetch_and_parse_crds():
    """Fetch workloadconfigurationscans CRDs and update Prometheus metrics."""
    try:
        config.load_incluster_config()
        v1 = client.CustomObjectsApi()
        group = "spdx.softwarecomposition.kubescape.io"
        version = "v1beta1"
        plural = "workloadconfigurationscans"
        scans = v1.list_cluster_custom_object(group, version, plural)
    except ApiException as e:
        print(f"Exception when fetching CRDs: {e}")
        return
    except Exception as e:
        print(f"Error loading in-cluster config: {e}")
        return

    # Clear previous metric values
    severity_gauge.clear()
    resource_issues_gauge.clear()
    remediation_gauge.clear()

    # Parse scan results
    for scan in scans.get("items", []):
        for result in scan.get("status", {}).get("results", []):
            resource_id = result.get("resourceID", "Unknown")
            kind, namespace, name = parse_resource_id(resource_id)
            resource_name = f"{kind}/{name}"

            for control in result.get("controls", []):
                if control.get("status") == "failed":
                    control_id = control.get("controlID", "Unknown")
                    issue_name = control.get("name", "Unknown")
                    score_factor = control.get("scoreFactor", 0)
                    severity = map_score_to_severity(score_factor)

                    # Update Prometheus metrics
                    severity_gauge.labels(severity=severity).inc()
                    resource_issues_gauge.labels(resource=resource_name, issue_name=issue_name).set(1)

                    # Extract remediations
                    remediations = []
                    for rule in control.get("rules", []):
                        if rule.get("status") == "failed":
                            for path in rule.get("paths", []):
                                fix_path = path.get("fixPath", {})
                                if fix_path:
                                    remediation = f"Set {fix_path.get('path', 'Unknown')} to {fix_path.get('value', 'Unknown')}"
                                else:
                                    remediation = "No fix path provided"
                                remediations.append(remediation)

                    for remediation in remediations:
                        remediation_url = f"https://hub.armosec.io/docs/controls/{control_id.lower()}"
                        remediation_gauge.labels(
                            resource=resource_name,
                            issue_name=issue_name,
                            remediation=remediation,
                            control_id=control_id,
                            remediation_url=remediation_url,
                            kind=kind,
                            namespace=namespace
                        ).set(1)

@app.route('/metrics')
def metrics():
    fetch_and_parse_crds()
    data = generate_latest(registry)
    return Response(data, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)