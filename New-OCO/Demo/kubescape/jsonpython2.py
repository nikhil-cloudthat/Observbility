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

def parse_resource_id(resource_id):
    """Parse resourceID to extract kind, namespace, and name."""
    parts = resource_id.strip('/').split('/')
    if len(parts) == 4:
        # /v1/<namespace>/<kind>/<name>
        api_group = '/v1'
        namespace = parts[1]
        kind = parts[2]
        name = parts[3]
    elif len(parts) == 5:
        if parts[2] == '':
            # <group>/<version>//<kind>/<name>
            api_group = f"{parts[0]}/{parts[1]}"
            namespace = None
            kind = parts[3]
            name = parts[4]
        else:
            # <group>/<version>/<namespace>/<kind>/<name>
            api_group = f"{parts[0]}/{parts[1]}"
            namespace = parts[2]
            kind = parts[3]
            name = parts[4]
    else:
        return {'api_group': 'Unknown', 'namespace': None, 'kind': 'Unknown', 'name': resource_id}
    return {
        'api_group': api_group,
        'namespace': namespace,
        'kind': kind,
        'name': name
    }

def map_score_to_severity(score_factor):
    """Map scoreFactor to severity level."""
    if score_factor <= 3:
        return "Low"
    elif score_factor <= 6:
        return "Medium"
    else:
        return "High"

def get_remediation(path_obj):
    """Extract remediation message from path object."""
    if 'fixPath' in path_obj and path_obj['fixPath'] and path_obj['fixPath'].get('path') and path_obj['fixPath'].get('value'):
        fix_path = path_obj['fixPath']['path']
        fix_value = path_obj['fixPath']['value']
        return f"Set {fix_path} to {fix_value}"
    if 'deletePath' in path_obj and path_obj['deletePath']:
        delete_path = path_obj['deletePath']
        return f"Delete {delete_path}"
    if 'failedPath' in path_obj and path_obj['failedPath']:
        failed_path = path_obj['failedPath']
        return f"Issue at {failed_path}, no fix provided"
    if 'reviewPath' in path_obj and path_obj['reviewPath']:
        review_path = path_obj['reviewPath']
        return f"Review {review_path}"
    return 'Unknown remediation'

def parse_json_and_update_metrics():
    """Parse JSON file and update Prometheus metrics."""
    json_file_path = '/app/data/resv2.json'
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return

    controls_summary = data.get('summaryDetails', {}).get('controls', {})
    resources = data.get('resources', [])

    # Clear previous metric values
    severity_gauge.clear()
    resource_issues_gauge.clear()
    remediation_gauge.clear()

    for resource in resources:
        resource_id = resource.get('resourceID', 'Unknown')
        parsed = parse_resource_id(resource_id)
        kind = parsed['kind']
        namespace = parsed['namespace']
        name = parsed['name']
        resource_label = f"{kind}/{name}"
        namespace_label = namespace if namespace else 'cluster-wide'

        controls = resource.get('controls', [])
        for control in controls:
            control_id = control.get('controlID', 'Unknown')
            issue_name = control.get('name', 'Unknown')
            score_factor = controls_summary.get(control_id, {}).get('scoreFactor', 0)
            severity = map_score_to_severity(score_factor)

            rules = control.get('rules', [])
            failed_rules = [rule for rule in rules if rule.get('status') == 'failed']
            if failed_rules:
                severity_gauge.labels(severity=severity).inc()
                resource_issues_gauge.labels(resource=resource_label, issue_name=issue_name).set(1)
                for rule in failed_rules:
                    paths = rule.get('paths', [])
                    for path in paths:
                        remediation = get_remediation(path)
                        remediation_url = f"https://hub.armosec.io/docs/controls/{control_id}"
                        remediation_gauge.labels(
                            resource=resource_label,
                            issue_name=issue_name,
                            remediation=remediation,
                            control_id=control_id,
                            remediation_url=remediation_url,
                            kind=kind,
                            namespace=namespace_label
                        ).set(1)

@app.route('/metrics')
def metrics():
    parse_json_and_update_metrics()
    data = generate_latest(registry)
    return Response(data, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)