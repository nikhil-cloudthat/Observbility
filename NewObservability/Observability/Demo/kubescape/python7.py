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
framework_compliance_gauge = Gauge(
    'framework_compliance_score',
    'Compliance score for each framework',
    ['framework'],
    registry=registry
)
total_compliance_gauge = Gauge(
    'total_compliance_score',
    'Total compliance score',
    registry=registry
)

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
        if len(parts) == 5:
            namespace = parts[2]
            kind = parts[3]
            name = parts[4]
        elif len(parts) == 4:
            namespace = parts[1]
            kind = parts[2]
            name = parts[3]
        else:
            namespace = 'Unknown'
            kind = 'Unknown'
            name = resource_id
    return kind, namespace, name

def parse_json_and_update_metrics():
    """Parse the JSON report and update Prometheus metrics."""
    json_file_path = '/app/data/resv3.json'
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file_path}")
        return

    # Set framework compliance scores
    frameworks = data.get('summaryDetails', {}).get('frameworks', [])
    for framework in frameworks:
        name = framework.get('name', 'Unknown')
        score = framework.get('complianceScore', 0)
        framework_compliance_gauge.labels(framework=name).set(score)
        if name == 'AllControls':
            total_compliance_gauge.set(score)

    # Set severity counts from controlsSeverityCounters
    severity_counters = data.get('summaryDetails', {}).get('controlsSeverityCounters', {})
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counters.get(f'{severity}Severity', 0)
        severity_gauge.labels(severity=severity.capitalize()).set(count)

    # Iterate through results for resource-specific metrics
    for resource in data.get('results', []):
        resource_id = resource.get('resourceID', 'Unknown')
        kind, namespace, name = parse_resource_id(resource_id)

        for control in resource.get('controls', []):
            if control.get('status', {}).get('status') == 'failed':
                control_id = control.get('controlID', 'Unknown')
                issue_name = control.get('name', 'Unknown')

                # Set resource issues gauge
                resource_issues_gauge.labels(resource=name, issue_name=issue_name).set(1)

                # Get remediations
                remediations = []
                for rule in control.get('rules', []):
                    if rule.get('status') == 'failed':
                        for path in rule.get('paths', []):
                            fix_path = path.get('fixPath', {})
                            if fix_path and fix_path.get('path'):
                                remediation = f"Set {fix_path['path']} to {fix_path.get('value', 'YOUR_VALUE')}"
                            elif 'deletePath' in path:
                                remediation = f"Delete the configuration at {path['deletePath']}"
                            elif 'failedPath' in path:
                                remediation = f"Check and fix the configuration at {path['failedPath']}"
                            elif 'reviewPath' in path:
                                remediation = f"Review the configuration at {path['reviewPath']}"
                            else:
                                remediation = 'No specific remediation provided'
                            remediations.append(remediation)

                # Set remediation gauge
                for remediation in remediations:
                    remediation_url = f"https://hub.armosec.io/docs/{control_id.lower()}"
                    remediation_gauge.labels(
                        resource=name,
                        issue_name=issue_name,
                        remediation=remediation,
                        control_id=control_id,
                        remediation_url=remediation_url,
                        kind=kind,
                        namespace=namespace
                    ).set(1)

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics endpoint."""
    parse_json_and_update_metrics()
    data = generate_latest(registry)
    return Response(data, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)