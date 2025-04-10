## One-Click Observability 

One-Click Observability is a simplified approach to setting up monitoring, logging, and tracing for applications with minimal manual configuration. It typically involves automated instrumentation, pre-configured dashboards, and seamless integration with observability tools like Grafana, Prometheus, Loki, and OpenTelemetry.

For more details about the tools and configuration, [Refer](./Observability/README.md)

# Architecture Diagram

![OAC Architecture](https://raw.githubusercontent.com/gokulraj-ct/Images/main/OAC-architecture-diagram.png)

To deploy monitoring tools, 

prerequisites,

- [ ] AWS CLI 
- [ ] Kubectl 
- [ ] EKSctl
- [ ] EKS Cluster
- [ ] helm & helmfile

**Install helm**

```
sudo apt update && sudo apt upgrade
sudo apt install wget -y
wget -O helm.tar.gz https://get.helm.sh/helm-v3.17.0-linux-amd64.tar.gz 
sudo tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
helm version
```

**Install helmfile**

```
sudo apt update && sudo apt upgrade
sudo apt install wget -y
wget -O helmfile.tar.gz https://github.com/helmfile/helmfile/releases/download/v1.0.0-rc.11/helmfile_1.0.0-rc.11_linux_amd64.tar.gz
sudo tar -zxvf helmfile.tar.gz
chmod +x helmfile
sudo mv linux-amd64/helmfile /usr/local/bin/helmfile
helmfile version
```


**Install using helm charts**

Below the command for install monitoring tools using helm charts,

1. Run the command,
```
helm dependency update
helm install <Release_name> </path/to/helm_chart> --values /path/to/grafana_values.yaml --values /path/to/alloy_values.yaml --values /pathto/tempo_values.yaml --values /path/to/prometheus_values.yaml --values /path/to/fluentbit_values.yaml --values /path/toloki-distributed_values.yaml --values /path/to/prometheus-msteams-values.yaml --values /path/to/alertmanager_values.yaml --values /path/tokubescape_values.yaml --values /path/to/custom_install.yaml
```
For custom deployment of monitoring tools using helm file, edit this [file](./Observability/helm-chart/custom-deploy_values.yaml)

__Note:__ Adjust the path of values files.
    
**Install via helmfile**

1. Run the following command
```
helmfile init
helmfile apply
```

2. For custom deployment of monitoring tools using helm file, use below command
```
helmfile -l tool=prometheus apply
```
