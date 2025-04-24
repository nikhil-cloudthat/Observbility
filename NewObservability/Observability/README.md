## 🚀 one-click-observability

**One-Click Observability** is a simplified approach to setting up monitoring, logging, and tracing for applications with minimal manual configuration. It typically involves automated instrumentation, pre-configured dashboards, and seamless integration with observability tools like Grafana, Prometheus, Loki, and OpenTelemetry.

**How One-Click Observability Works,**

- **Automatic Instrumentation –** The system automatically detects your application and injects the required telemetry collectors (metrics, logs, and traces).
- **Preconfigured Dashboards & Alerts –** Once data is collected, pre-built dashboards and alerting rules are provided.
- **Seamless Backend Integration –** The telemetry data is sent to platforms like Grafana, Prometheus, Loki, and Tempo for visualization and analysis.
- **Minimal Manual Effort –** Users don't need to manually configure exporters, dashboards, or alerting rules.

Tools used and deployed in EKS Cluster using helm charts,

1. Instrumentation
2. Grafana Alloy
3. Loki-distributed
4. Grafana Tempo
5. Prometheus
6. Alert Manager
7. Promethues-msteams
8. Grafana 
9. Fluent-bit
10. Kubescape

## 1️⃣ Instrumentation

Instrumentation is the process of adding code or configurations to an application to collect telemetry data (metrics, logs, and traces). This data helps in monitoring, debugging, and optimizing the application.

If your application is instrumented to send telemetry data to Grafana Alloy, it means your app is configured to export metrics, logs, and traces using protocols like OpenTelemetry, Prometheus, or Fluent Bit.

Types of Instrumentation

Manual Instrumentation – Developers add explicit code (e.g., SDKs or libraries) to collect telemetry data.

Automatic Instrumentation – Uses agent-based solutions that inject observability without modifying application code.

| Telemetry  | Description                                    | How to Instrument                              |
|------------|----------------------------------------------|-----------------------------------------------|
| **Metrics** | Numeric data like request count, latency, memory usage | Use Prometheus SDKs, OpenTelemetry Metrics SDK |
| **Logs**    | Text-based event records                    | Use Fluent Bit, Loki clients, or OpenTelemetry Logging SDK |
| **Traces**  | Tracks a request’s lifecycle across services | Use OpenTelemetry Tracing SDK                 |


## 2️⃣ Grafana Alloy

**Grafana Alloy** is an open-source telemetry agent designed to collect, process, and export observability data (metrics, logs, and traces). It is a unified and extensible tool that combines the capabilities of various telemetry collectors, including Prometheus, OpenTelemetry Collector, and Fluent Bit. Grafana Alloy allows you to manage your observability pipeline more efficiently by acting as a single agent for handling multiple data sources and backends.

Alloy is more than just observability signals like metrics, logs, and traces. It provides many features that help you quickly find and process your data in complex environments. Some of these features include custom components, GitOps compatibility, clustering support, security, and debugging utilities.

__Comparison with Other Tools__

| Feature         | Grafana Alloy | Prometheus | OpenTelemetry Collector | Fluent Bit |
|---------------|--------------|------------|-------------------------|------------|
| **Metrics**    | ✅           | ✅         | ✅                      | ❌         |
| **Logs**       | ✅           | ❌         | ✅                      | ✅         |
| **Traces**     | ✅           | ❌         | ✅                      | ❌         |
| **OpenTelemetry** | ✅       | ❌         | ✅                      | ❌         |
| **Remote Write** | ✅       | ✅         | ❌                      | ❌         |


## 3️⃣ Loki-Distributed

__Loki-Distributed__ is a horizontally scalable, highly available deployment of Grafana Loki, designed to handle logs at large scale across multiple instances. Unlike single-node Loki, the distributed architecture enables better performance, redundancy, and fault tolerance, making it ideal for Kubernetes, cloud, and enterprise deployments.

**🚀 Benefits of Loki-Distributed**

- ✅ Scalability – Handles massive log volumes efficiently.
- ✅ High Availability – Ensures redundancy and fault tolerance.
- ✅ Cost-Efficient – Uses index-free architecture, storing logs in cheap object storage.
- ✅ Optimized Queries – Uses a parallelized query engine for faster searches.
- ✅ Multi-Tenancy Support – Isolates logs per team, service, or environment.

__Note:__ Update storage configuration to Amazon S3 if needed, at line 232

## 4️⃣ Grafana Tempo: Distributed Tracing Backend

Grafana Tempo is a highly scalable, cost-efficient distributed tracing backend designed to store and query traces without requiring a full index. It is part of the Grafana observability stack, alongside Loki (logs), Mimir (metrics), and Alloy (telemetry processing).

__🔹 Why Use Grafana Tempo?__

- ✅ No Indexing → Low Cost → Uses cheap object storage (S3, GCS, Azure Blob, etc.).
- ✅ Scalable → Can handle massive traces without increasing indexing costs.
- ✅ Integrates with Logs & Metrics → Seamlessly connects traces to Loki logs and Prometheus metrics in Grafana.
- ✅ Multi-Tenant Support → Ideal for shared environments (multi-team tracing).
- ✅ Supports OpenTelemetry & Jaeger → Easily ingests traces from existing sources.

__🔄 Tempo vs. Other Tracing Tools__

| Feature                    | Grafana Tempo  | Jaeger      | Zipkin      |
|----------------------------|---------------|------------|------------|
| **Index-Free**             | ✅ Yes        | ❌ No      | ❌ No      |
| **Storage Cost**           | 💰 Low (Object Storage) | 💰 High (DB-based) | 💰 High (DB-based) |
| **OpenTelemetry Support**  | ✅ Yes        | ✅ Yes     | ✅ Yes     |
| **Scalability**            | 🚀 High       | 🚀 Medium  | 🛑 Limited  |
| **Integration with Grafana** | ✅ Native   | ⚠️ Limited | ⚠️ Limited |

__Note:__ No major configuration changes to tempo

## 5️⃣ Prometheus: Open-Source Monitoring & Alerting System

Prometheus is a highly scalable, open-source monitoring system used for collecting, storing, querying, and alerting on time-series data. It is part of the Cloud Native Computing Foundation (CNCF) and is widely used in Kubernetes, cloud, and microservices environments.

__🔹 Key Features of Prometheus__
- ✅ Time-Series Data Storage → Stores metrics with timestamps, labels, and values.
- ✅ Pull-Based Model → Prometheus scrapes metrics from endpoints via HTTP.
- ✅ Powerful Querying → Uses PromQL (Prometheus Query Language) for data analysis.
- ✅ Built-in Alerting → Alerts via Alertmanager (Slack, PagerDuty, Email, etc.).
- ✅ Service Discovery → Auto-discovers targets in Kubernetes, EC2, Consul, etc.
- ✅ Multi-Dimensional Data Model → Uses labels (e.g., app="nginx", env="prod") for flexible filtering.
- ✅ Scalability & Federation → Supports sharding, remote storage, and multi-cluster setups.

__🔄 How Prometheus Integrates with Other Tools__

| Tool            | Integration Purpose                                   |
|----------------|------------------------------------------------------|
| **Grafana**     | Visualizes Prometheus metrics                        |
| **Alertmanager** | Handles alerts from Prometheus                      |
| **Node Exporter** | Collects Linux/Windows host metrics               |
| **Kubernetes**  | Monitors cluster metrics (CPU, memory, etc.)        |
| **Loki**        | Links logs with metrics for better debugging         |
| **OpenTelemetry** | Collects and exports application telemetry         |


__🚀 When to Use Prometheus?__
- ✅ Kubernetes Monitoring – Track pod resource usage and node health.
- ✅ Application Monitoring – Observe response times, error rates, and API performance.
- ✅ Infrastructure Monitoring – Monitor CPU, memory, disk, network traffic.
- ✅ Alerting & Incident Response – Get notified when systems fail or degrade.
- ✅ Scalability – Handle large-scale, multi-region setups.


__Note:__ Node Exporter is disabled, all the telemetry data's collect using alloy agent only.

## 6️⃣ 🔔 Alertmanager: Prometheus Alerting System

Alertmanager is a centralized alerting system used with Prometheus to manage and dispatch alerts based on predefined rules. It ensures that alerts are deduplicated, grouped, silenced, and routed to the right notification channels.

__Note:__ By direct, cannot send alerts to Microsoft Teams 

__🔹 Why Use Alertmanager?__
- ✅ Deduplication → Prevents duplicate alerts from spamming notifications.
- ✅ Grouping → Combines related alerts (e.g., all failing pods in a namespace).
- ✅ Silencing → Temporarily mutes alerts during maintenance.
- ✅ Routing → Sends alerts to the correct teams based on labels.
- ✅ Multiple Notification Channels → Supports Slack, Email, PagerDuty, Webhooks, etc.

__⚙️ How Alertmanager Works__
- 1️⃣ Prometheus generates alerts based on metrics and alerting rules.
- 2️⃣ Alertmanager receives alerts and processes them.
- 3️⃣ Grouping & Deduplication → Merges similar alerts into a single notification.
- 4️⃣ Routing & Dispatching → Sends alerts to the correct destination based on rules.
- 5️⃣ Silencing (Optional) → Suppresses alerts for a set time.


## 7️⃣ 🔔 Prometheus MS Teams Integration
Prometheus MS Teams refers to the integration between Prometheus Alertmanager and Microsoft Teams to send alerts directly to Teams channels. Since Alertmanager does not have native support for MS Teams, we use a webhook-based integration.

__🔹 How Prometheus Sends Alerts to MS Teams__
- 1️⃣ Prometheus triggers an alert based on a metric condition.
- 2️⃣ Alertmanager processes the alert and formats it.
- 3️⃣ Alertmanager sends the alert to an MS Teams Incoming Webhook URL.
- 4️⃣ MS Teams displays the alert in a specified channel.

__📦 Setting Up Prometheus Alertmanager with MS Teams__

**Step 1: Create an Incoming Webhook in MS Teams**

- Open Microsoft Teams.
- Go to the desired Channel.
- Click on "More options (⋮)" → "Connectors".
- Search for "Incoming Webhook" and click "Configure".
- Enter a name (e.g., "Prometheus Alerts").
- Upload an icon (optional).
- Copy the Webhook URL (e.g., https://outlook.office.com/webhook/...).


## 8️⃣ 📊 Grafana: Open-Source Data Visualization & Monitoring

Grafana is a powerful open-source analytics and monitoring platform used to visualize and analyze time-series data. It integrates with various data sources, including Prometheus, Loki, Tempo, MySQL, Elasticsearch, InfluxDB, AWS CloudWatch, and more.

__🔹 Key Features of Grafana__
- ✅ Beautiful Dashboards → Create interactive and real-time visualizations.
- ✅ Multi-Source Support → Connect to multiple data sources at once.
- ✅ Alerts & Notifications → Set up alerts with Slack, Teams, PagerDuty, etc.
- ✅ Templating & Variables → Dynamic dashboards with dropdown filters.
- ✅ Role-Based Access Control (RBAC) → Manage user access levels.
- ✅ Plugins & Extensions → Extend capabilities with additional plugins.
- ✅ Multi-Tenancy → Organize users and teams efficiently.

__🛠 Grafana Components__
- 📈 Dashboards – Visual representations of metrics (graphs, tables, heatmaps).
- 🔎 Data Sources – External systems (Prometheus, Loki, Tempo, databases).
- 📢 Alerting – Trigger notifications when metrics cross thresholds.
- 📊 Panels & Queries – Custom charts, graphs, and query editors.
- 🔑 Authentication – Supports LDAP, OAuth, SSO (AWS Identity Center, etc.).

__🚀 How Grafana Works__
- 1️⃣ Connects to a data source (e.g., Prometheus for Kubernetes metrics).
- 2️⃣ Fetches real-time data using queries.
- 3️⃣ Displays data in dashboards with customizable panels.
- 4️⃣ Triggers alerts based on thresholds.
- 5️⃣ Notifies teams via email, Slack, Teams, PagerDuty, etc.

__🌐 How to access Grafana__

Step 1: Create Secret for login and password / directly add adminUser and adminPassword

Step 2: Use Ingress / expose service type as Load Balancer to access

step 3: Use adminUser and adminPassword

## 9️⃣🔥 Fluent Bit: Lightweight Log Processor & Forwarder

Fluent Bit is a fast, lightweight, and highly scalable log processor and forwarder used for collecting, filtering, transforming, and shipping logs from various sources to multiple destinations. It is commonly used in Kubernetes, cloud-native environments, and IoT applications to manage logs efficiently.

Fluent Bit is part of the Fluentd ecosystem, but it is much lighter and faster, making it ideal for resource-constrained environments.

__🔹 Key Features of Fluent Bit__
- ✅ Low CPU & Memory Usage → Designed for high performance with minimal resource consumption.
- ✅ Multi-Platform Support → Works on Linux, Windows, macOS, and Kubernetes.
- ✅ Supports Various Log Sources & Destinations → Reads logs from files, systemd, Docker, Kubernetes, etc., and forwards them to Elasticsearch, Loki, Splunk, Prometheus, etc.
- ✅ Log Parsing & Filtering → Can structure logs (JSON, regex parsing), enrich data, and drop unnecessary logs.
- ✅ Kubernetes Native → Can collect pod logs, enrich them with Kubernetes metadata, and send them to centralized storage.
- ✅ Built-in Metrics & Observability → Supports Prometheus and OpenTelemetry for monitoring Fluent Bit itself.

__ 🛠 Fluent Bit Architecture__

Fluent Bit operates in a three-step pipeline:

- 1️⃣ Input Plugins → Collect logs from sources (e.g., Kubernetes logs, system logs, Docker logs).
- 2️⃣ Filter Plugins → Process and modify logs (e.g., drop unnecessary logs, restructure JSON).
- 3️⃣ Output Plugins → Send logs to destinations (e.g., Elasticsearch, Loki, Prometheus, AWS S3, Kafka).

__🔗 Popular Fluent Bit Integrations__
- 🚀 Grafana Loki – Store and query logs in a structured way.
- 🚀 Elasticsearch – Centralized log storage for analysis.
- 🚀 Amazon CloudWatch – Forward logs to AWS CloudWatch.
- 🚀 Kafka – Stream logs for real-time processing.
- 🚀 Splunk – Enterprise-grade log analysis.
- 🚀 OpenTelemetry – Collect and forward logs for distributed tracing.

## 1️⃣0️⃣ 🛡️Kubescape: Kubernetes Security Scanner

Kubescape is an open-source Kubernetes security tool used to scan Kubernetes clusters, YAML files, and Helm charts for security risks, misconfigurations, and compliance violations. It helps DevOps, SREs, and security teams identify vulnerabilities and ensure security best practices in Kubernetes environments.

Kubescape is developed by ARMO and supports standards like NSA-CISA Hardening Guide, MITRE ATT&CK®, CIS Benchmarks, and custom security frameworks.

__🔹 Key Features of Kubescape__
- ✅ Kubernetes Misconfiguration Scanning → Detects security issues in clusters, YAML, and Helm charts.
- ✅ Compliance Checks → Validates against industry standards (NSA-CISA, MITRE ATT&CK, CIS, etc.).
- ✅ RBAC Visualization & Analysis → Analyzes Kubernetes Role-Based Access Control (RBAC) permissions to detect overprivileged users.
- ✅ CI/CD Security Integration → Can be integrated into Jenkins, GitHub Actions, ArgoCD, Terraform, and Helm.
- ✅ Continuous Monitoring → Monitors security posture over time and provides alerts.
- ✅ Offline & On-Prem Deployment → Can run without internet access for private clusters.
- ✅ Built-in Security Frameworks → Supports predefined and custom security rules.

__Note:__ No major configuration changes.