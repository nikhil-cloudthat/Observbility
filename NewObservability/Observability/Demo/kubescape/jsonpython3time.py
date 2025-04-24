import os
import glob
import json
from flask import Flask, Response
from prometheus_client import Gauge, CollectorRegistry, generate_latest

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

def find_latest_report(dir_path='/app/data', prefix='resv2_'):
    """
    Return the most recently created JSON file matching <prefix>*.json
    in the given directory, or None if no such file exists.
    """
    pattern = os.path.join(dir_path, f"{prefix}*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def parse_json_and_update_metrics():
    """Parse the latest JSON report and update Prometheus metrics."""
    json_file_path = find_latest_report()
    if not json_file_path:
        print("Error: no report file found in /app/data")
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError:
        print(f"Error: invalid JSON in {json_file_path}")
        return

    # Extract control score factors
    control_score_factors = {
        control['controlID']: control['scoreFactor']
        for control in data.get('summaryDetails', {}).get('controls', {}).values()
    }

    # Clear previous metric values
    severity_gauge.clear()
    resource_issues_gauge.clear()
    remediation_gauge.clear()

    # Iterate through results
    for resource in data.get('results', []):
        resource_id = resource.get('resourceID', 'Unknown')
        kind, namespace, name = parse_resource_id(resource_id)
        resource_name = f"{kind}/{name}"

        for control in resource.get('controls', []):
            if control.get('status', {}).get('status') == 'failed':
                control_id = control.get('controlID', 'Unknown')
                issue_name = control.get('name', 'Unknown')
                score_factor = control_score_factors.get(control_id, 0)
                severity = map_score_to_severity(score_factor)

                # Increment severity gauge
                severity_gauge.labels(severity=severity).inc()

                # Set resource issues gauge
                resource_issues_gauge.labels(
                    resource=resource_name, 
                    issue_name=issue_name
                ).set(1)

                # Collect remediations
                remediations = []
                for rule in control.get('rules', []):
                    if rule.get('status') == 'failed':
                        for path in rule.get('paths', []):
                            fix_path = path.get('fixPath', {})
                            if fix_path:
                                remediations.append(
                                    f"Set {fix_path.get('path', 'Unknown')} "
                                    f"to {fix_path.get('value', 'Unknown')}"
                                )
                            else:
                                remediations.append('No fix path provided')

                # Set remediation gauge for each remediation
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
    # On each scrape, parse the latest JSON and update metrics
    parse_json_and_update_metrics()
    data = generate_latest(registry)
    return Response(data, mimetype='text/plain')

if __name__ == '__main__':
    # Listen on all interfaces, port 8000
    app.run(host='0.0.0.0', port=8000)
