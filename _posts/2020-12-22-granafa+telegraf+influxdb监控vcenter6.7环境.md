---
layout: post
title: granafa+telegraf+influxdb监控vcenter6.7环境
date: 2020-12-22
author: ZMY
header-img: ../img/monitor_alarm_background.jpg
catalog : true
tags:
   - vcenter6.7监控
   - granafa
   - telegraf
   - influxdb
typora-root-url: ..

---
## <img class="original" src='/img/original.png'> granafa+telegraf+influxdb监控vcenter6.7环境

## 目的
通过granafa平台展示vcenter6.7里面的数据
## 环境描述
- 1台vcenter appliance+3台esxi6.7+若干台虚拟机组成的vsan环境

- granafa+telegraf+influxdb所在环境为一台centos7.4虚拟机
  - granafa版本7.3.4  
  - telegraf版本1.16.3
  - influxdb版本1.8.3
  
## 安装并配置过程

1.安装granafa
- 添加yum库
```
# vim /etc/yum.repos.d/grafana.repo
```
```bash
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
```

- 启动grafana-server服务
```bash
sudo systemctl daemon-reload
sudo systemctl start grafana-server
sudo systemctl status grafana-server
```

- 设置开机自启动
```bash
systemctl enable grafana-server
```
开机浏览器访问http://ip:3000  
默认用户名和密码都是admin  
![](/img/2020-12-22/1.png)
首次登陆会要求更换密码
![](/img/2020-12-22/2.png)
官网文档[https://grafana.com/docs/grafana/latest/installation/rpm/](https://grafana.com/docs/grafana/latest/installation/rpm/)

2.安装并配置influxdb
- 创建influxdb yum配置文件
```
# cat <<EOF | sudo tee /etc/yum.repos.d/influxdb.repo
[influxdb]
name = InfluxDB Repository - RHEL \$releasever
baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
enabled = 1
gpgcheck = 1
gpgkey = https://repos.influxdata.com/influxdb.key
EOF
```

- 更新yum缓存
```
# sudo yum makecache fast
```

- 安装influxdb
```
# sudo yum -y install influxdb vim curl
```

- 开启influxdb服务并设置成开机自启动
```
# sudo systemctl start influxdb && sudo systemctl enable influxdb
```

[参考文档](https://computingforgeeks.com/install-grafana-and-influxdb-on-centos-7/)

3.安装并配置telegraf
- 安装telegraf并配置和influxdb连接方式
```
# sudo yum -y install telegraf
```

- 配置vsphere output插件
```
# sudo vim /etc/telegraf/telegraf.conf
# Configuration for sending metrics to InfluxDB
[[outputs.influxdb]]
    urls = ["http://127.0.0.1:8086"]
    database = "vmware"
    timeout = "0s"
```

- 配置vsphere input插件,将其中的vcenter信息换成你的  
```
##
[[inputs.vsphere]]
#### List of vCenter URLs to be monitored. These three lines must be uncommented
### and edited for the plugin to work.
  interval = "20s"
  vcenters = [ "https://10.10.90.165/sdk" ]
  username = "administrator@vsphere.local"
  password = "******"

  vm_metric_include = []
  host_metric_include = []
  cluster_metric_exclude = ["*"]
  datastore_metric_exclude = ["*"]

  max_query_metrics = 256
  timeout = "60s"
  insecure_skip_verify = true

## Historical instance
[[inputs.vsphere]]
  interval = "300s"
  vcenters = [ "https://10.10.90.165/sdk" ]
  username = "administrator@vsphere.local"
  password = "******"

  datastore_metric_include = [ "disk.capacity.latest", "disk.used.latest", "disk.provisioned.latest"]
  insecure_skip_verify = true
  force_discover_on_init = true
  cluster_metric_include = ["*"]
  datacenter_metric_include = ["*"]
  host_metric_exclude = ["*"] # Exclude realtime metrics
  vm_metric_exclude = ["*"] # Exclude realtime metrics

  max_query_metrics = 256
  collect_concurrency = 3
```

- 重新启动服务，加载刚修改的配置
```
sudo systemctl restart telegraf
sudo systemctl enable telegraf
```
验证是否有InfluxDB Metrics  
```
[root@localhost ~]# influx
Connected to http://localhost:8086 version 1.8.3
InfluxDB shell version: 1.8.3
> 
```
```
> USE vmware
Using database vmware 
```
```
> SHOW MEASUREMENTS
name: measurements
name
----
cpu
disk
diskio
kernel
mem
processes
swap
system
vsphere_cluster_clusterServices
vsphere_cluster_mem
vsphere_cluster_vmop
vsphere_datacenter_vmop
vsphere_datastore_datastore
vsphere_datastore_disk
vsphere_host_cpu
vsphere_host_disk
vsphere_host_mem
vsphere_host_net
vsphere_host_power
vsphere_host_storageAdapter
vsphere_host_sys
vsphere_vm_cpu
vsphere_vm_mem
vsphere_vm_net
vsphere_vm_power
vsphere_vm_sys
vsphere_vm_virtualDisk
> 
```

如查看到有以上metrics输出，说明telegraf能够正确获取vcenter数据并存入到influxdb中  

[参考文档](https://computingforgeeks.com/how-to-monitor-vmware-esxi-with-grafana-and-telegraf/)

4.添加influxdb数据源
![](/img/2020-12-22/3.png)
- 选择influxdb数据源
![](/img/2020-12-22/4.png)
- 添加influxdb信息
![](/img/2020-12-22/5.png)

5.添加granafa上关于vcenter6.7的dashboard

- 通过granafa官网dashboard库，下载对应的dashboard,并上传,dashboard[地址](https://grafana.com/grafana/dashboards/8159)

  - 下载dashboard

  ![](/img/2020-12-22/6.png)
  - 其他dashboard下载位置
  ![](/img/2020-12-22/7.png)
  - 通过granafa上传dashboard的json文件
![](/img/2020-12-22/8.png)
![](/img/2020-12-22/9.png)
- 添加influxdb数据源
![](/img/2020-12-22/10.png)


6.默认dashboard存在的问题及解决办法

- 安装后datastore dashboard报错

![](/img/2020-12-22/11.png)

解决办法:

```
# wget https://grafana.com/api/plugins/grafana-piechart-panel/versions/1.6.1/download
# unzip unzip grafana-piechart-panel-1.6.1.zip
# mv grafana-piechart-panel/ /var/lib/grafana/plugins/grafana-piechart-panel/
```

[参考文档](https://grafana.com/grafana/plugins/grafana-piechart-panel)

- dashboard上cpu使用率不正确

  解决办法

  - 找到需要修改cpu usages的面板,进行编辑

  ![](/img/2020-12-22/12.png)

  - 增加cpu=total-instance键值对cpu:instance-total

  ![](/img/2020-12-22/14.png)

  ![](/img/2020-12-22/15.png)

  ![](/img/2020-12-22/16.png)

  - 应用后进行保存

  ![](/img/2020-12-22/17.png)

  ![](/img/2020-12-22/18.png)



[参考文档](https://grafana.com/grafana/dashboards/8159/reviews)

## 监控界面展示

添加后一共四个模板，分别对应全局dashboard，esxi主机dashboard，vm虚拟机dashboard和数据存储dashboard

- vmware vsphere全局dashboard

![](/img/2020-12-22/19.png)

- vmware vsphere主机界面展示

![](/img/2020-12-22/20.png)

- vmware vm虚拟机界面展示

![](/img/2020-12-22/21.png)

- vmware datastore界面展示

![](/img/2020-12-22/22.png)



声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。
