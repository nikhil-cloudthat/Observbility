In observability, the collection of telemetry data (metrics, logs, and traces) using the mentioned tools should focus solely on fetching data and generating alerts. Below are the changes and configurations for each tool.

Flow of monitoring,
- [ ] Metrics
- [ ] Traces
- [ ] Logs
- [ ] Visualization

## Metrics
1. Prometheus

If you are using separate alertmanager, use below mentioned configuration of alertmanager 
```
prometheus.yml:  
  rule_files:  # Specifies the rule files to load  
    - /etc/config/recording_rules.yml  # Path to the recording rules file  
    - /etc/config/alerting_rules.yml  # Path to the alerting rules file  

  alerting:  
      alertmanagers:  # Defines the Alertmanager configuration  
        - static_configs:  
            - targets:  
                - 'alertmanager.default.svc.cluster.local:9093'  # Address of the Alertmanager instance in the cluster  
          tls_config:  
            ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt  # TLS certificate for secure communication with Alertmanager  

  scrape_configs:  # Defines targets for Prometheus to scrape metrics from  
    - job_name: prometheus  # Job name for scraping Prometheus itself  
      static_configs:  
        - targets: ['prometheus-server:9090']  # Prometheus server target address for scraping metrics  
```
This configuration is used in Prometheus to define its behavior for collecting and managing metrics.

1. Rule Files:

    - ```recording_rules.yml```: Used for precomputing frequently used or complex queries.

    - ```alerting_rules.yml```: Defines alerting conditions that trigger notifications when specific conditions are met.

2. Alerting Configuration:

    - Sends alerts to **Alertmanager**, which handles routing and notification delivery (e.g., Slack, Microsoft Teams).
    
    -Uses TLS configuration for secure communication within a **Kubernetes cluster**.

3. Scrape Configuration:

    - Prometheus is set to scrape metrics from itself at ```prometheus-server:9090``` for **self-monitoring**.
    
    - Other scrape jobs (like application metrics) can be added in this section.

This setup ensures **Prometheus collects and evaluates metrics, triggers alerts when necessary**, and **sends them to Alertmanager for processing**.

Define alerts when metrics reached limits, below mentioned one for example
```
serverFiles:
  ## Alerts configuration  
  alerting_rules.yml:  
    groups:  
      - name: example  # Name of the alert group  
        rules:  
          - alert: HighRequestRate  # Name of the alert  
            expr: otel_request_counter_total{job="my-python-service"} > 10  # Condition to trigger the alert  
            for: 10s  # Duration the condition must hold before triggering the alert  
            labels:  
              severity: warning  # Label to indicate the alert severity  
            annotations:  
              summary: "Website request rate is high"  # Short description of the alert  
              description: "Something happened, go and check."  # Detailed alert message  

```
This configuration is used in Prometheus to define alerting rules. The alert HighRequestRate is triggered when the otel_request_counter_total metric for the my-python-service job exceeds 10 requests. If the condition persists for 10 seconds, an alert is sent with the label severity: warning and a notification is generated with a summary and description. This is useful for monitoring high traffic issues in a service and integrating with alerting tools like Alertmanager to send notifications via Slack, Microsoft Teams, or other channels.

2. Alertmanager

```
config:  
  enabled: true  # Enables the configuration  
  global:  
    resolve_timeout: 5m  # Time to wait before resolving an alert  
    # slack_api_url: ${your_slack_hook}  # Slack webhook URL (commented out)  
  templates:  
    - '/etc/alertmanager/*.tmpl'  # Path to template files for alert formatting  

  route:  
    group_by: ['alertname']  # Groups alerts by 'alertname'  
    group_wait: 5s  # Time to wait before sending the first alert in a group  
    group_interval: 5s  # Time interval between alert groups  
    receiver: 'msteams'  # Default receiver for alerts  
    repeat_interval: 1h  # Time interval before resending an alert  

    routes:  
    - receiver: 'msteams'  # Specifies that alerts will be sent to the 'msteams' receiver  

  receivers:  
    - name: 'null'  # A receiver that discards alerts (used for silencing)  
    - name: 'msteams'  # Receiver name for Microsoft Teams  
      webhook_configs:  
      - url: 'http://prometheus-msteams:2000/bar'  # Webhook URL for Microsoft Teams integration  
        send_resolved: true  # Sends notifications when an alert is resolved  

```
This is an Alertmanager configuration used for handling alerts from Prometheus. The alerts are grouped by alertname, and if multiple alerts arise, they are sent together after 5s. The main notification channel here is Microsoft Teams, which is configured through a webhook URL (http://prometheus-msteams:2000/bar). Alerts will repeat every 1 hour if they remain active. Additionally, a dummy receiver (null) is present, which can be used to discard specific alerts.

3. Prometheus-msteams
```
connectors:  
  - bar: https://cloud...  # Defines a connector named 'bar' that forwards alerts to the specified URL of msteams webhook  
```

This configuration is part of Prometheus-MSTeams, which is used to send Prometheus alerts to Microsoft Teams.

- The connectors section defines webhook endpoints for different channels in Microsoft Teams.
- The key (bar) is the connector name, and the URL (https://cloud) is the webhook endpoint where alerts will be sent.
- When an alert is triggered in Prometheus and sent to Alertmanager, Prometheus-MSTeams processes it and forwards it to the defined         Microsoft Teams channel.

## Visualization

**Grafana**

All collected datas are viualize using 

```
# Administrator credentials when not using an existing secret (see below)
adminUser: admin  # Sets the default admin username for Grafana
adminPassword: "ggr"  # Sets the default admin password for Grafana

# Use an existing secret for the admin user.
admin:
  ## Name of the secret. Can be templated.
  existingSecret: "grafana-secret"  # Uses an existing Kubernetes secret named 'grafana-secret' for authentication  
  userKey: userKey  # The key in the secret that stores the admin username  
  passwordKey: passwordKey  # The key in the secret that stores the admin password  
```

By using this configuration,

- If adminUser and adminPassword are provided, Grafana will use these credentials for the admin login.
- If existingSecret is set, Grafana will fetch credentials from the specified Kubernetes secret instead.
- This is useful for storing sensitive credentials securely in Kubernetes instead of hardcoding them in configuration files.

```
datasources:  # Defines data sources for Grafana  
  datasources.yaml:  # YAML file containing the data source configurations  
    apiVersion: 1  # API version for Grafana data source configuration  
    datasources:  # List of data sources  
      - name: Prometheus  # Name of the data source  
        type: prometheus  # Specifies that the data source is Prometheus  
        access: proxy  # Grafana will act as a proxy and route requests to Prometheus  
        url: http://prometheus-server.{{.Release.Namespace}}.svc.cluster.local  # Prometheus service URL inside the Kubernetes cluster  
        isDefault: true  # Sets Prometheus as the default data source in Grafana  
```
This configures Grafana to use Prometheus as its data source.

- The url uses Kubernetes service discovery (svc.cluster.local) to connect to Prometheus running in the same cluster.
- Since access: proxy is used, Grafana proxies requests instead of making them directly from the user’s browser.
- Setting isDefault: true ensures that Prometheus is pre-selected in Grafana dashboards.

This is crucial for visualizing metrics collected by Prometheus in Grafana dashboards for monitoring system performance, alerts, and application health.

__Note:__ By grafana itself, can able to mention alerts and notification to ms-teams.

