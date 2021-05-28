---
layout: post
title: 使用filebeat+logstash+elasticsearch+kibana在k8s集群上进行日志采集
date: 2021-05-28
author: ZMY
header-img: ../img/2021-05-28/background.png
catalog : true
tags:
   - elfk
typora-root-url: ..
---

## <img class="original" src='/img/original.png'>使用filebeat+logstash+elasticsearch+kibana在k8s集群上进行日志采集

**环境描述**

| 主机名/功能 | ip地址/访问方式 | 操作系统                      | 版本    | 备注   |
| ----------- | --------------- | ----------------------------- | ------- | ------ |
| master      | 192.168.140.210 | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node1       | 192.168.140.211 | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node2       | 192.168.140.212 | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |
| node3       | 192.168.140.213 | CentOS Linux release 7.4.1708 | v1.20.2 | 物理机 |



**项目背景**

k8s集群搭建后，平时运维过程中不仅要观察监控平台，查看集群运行情况，还要在集群出现问题时，对问题点进行及时定位，由于集群内pod过多后，日志定位比较费时，因此一个集中式的日志文件系统成了运维人员的好帮手，本次实验采用的是filebeat+logstash+elasticsearch+kibana



**组件功能描述**

filebeat负责采集每个节点上宿主机和容器的日志，发送给logstash,logstash过滤不必要的信息后传递给elasticsearch进行储存，kibana展示储存在elasticsearch上的数据，并可以通过查询语句提取关键字

![](/img/2021-05-28/1.png)

这里说一下为什么需要filebeat+logstash而不是单独的logstash，因为logstash中的jvm消耗的资源比较多，性能没有filebeat好，其实也可以不使用logstash，单独使用filebeat,logstash主要作用是有很多插件可以使用，并且提供过滤功能

参考https://logz.io/blog/filebeat-vs-logstash/



**安装过程**

1.filebeat的安装

由于filebeat需要再每个节点上进行数据的收集，因此pod使用daemonset类，文件名为filebeat-kubernetes.yaml

可参考https://github.com/elastic/beats/blob/master/deploy/kubernetes/filebeat-kubernetes.yaml

```

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  labels:
    k8s-app: filebeat
data:
  filebeat.yml: |-
    filebeat.autodiscover:
      providers:
        - type: kubernetes
          node: ${NODE_NAME}
          hints.enabled: true
          hints.default_config:
            type: container
            paths:
              - /var/log/containers/*${data.kubernetes.container.id}.log
    filebeat.inputs:
    - type: log
      enabled: true
      paths:
        - /var/log/*.log
    processors:
      - add_cloud_metadata:
      - add_host_metadata:

    cloud.id: ${ELASTIC_CLOUD_ID}
    cloud.auth: ${ELASTIC_CLOUD_AUTH}

    output.logstash:
      hosts: ["logstash:9600"]
      enabled: true
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  labels:
    k8s-app: filebeat
spec:
  selector:
    matchLabels:
      k8s-app: filebeat
  template:
    metadata:
      labels:
        k8s-app: filebeat
    spec:
      serviceAccountName: filebeat
      terminationGracePeriodSeconds: 30
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
      containers:
      - name: filebeat
        image: docker.elastic.co/beats/filebeat:7.12.0
        args: [
          "-c", "/etc/filebeat.yml",
          "-e",
        ]
        env:
        - name: ELASTICSEARCH_HOST
          value: elasticsearch
        - name: ELASTICSEARCH_PORT
          value: "9200"
        - name: ELASTICSEARCH_USERNAME
          value: elastic
        - name: ELASTICSEARCH_PASSWORD
          value: changeme
        - name: ELASTIC_CLOUD_ID
          value:
        - name: ELASTIC_CLOUD_AUTH
          value:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        securityContext:
          runAsUser: 0
          # If using Red Hat OpenShift uncomment this:
          #privileged: true
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 100Mi
        volumeMounts:
        - name: config
          mountPath: /etc/filebeat.yml
          readOnly: true
          subPath: filebeat.yml
        - name: data
          mountPath: /usr/share/filebeat/data
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: varlog
          mountPath: /var/log
          readOnly: true
      volumes:
      - name: config
        configMap:
          defaultMode: 0640
          name: filebeat-config
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: varlog
        hostPath:
          path: /var/log
      # data folder stores a registry of read status for all files, so we don't send everything again on a Filebeat pod restart
      - name: data
        hostPath:
          # When filebeat runs as non-root user, this directory needs to be writable by group (g+w).
          path: /var/lib/filebeat-data
          type: DirectoryOrCreate
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: filebeat
subjects:
- kind: ServiceAccount
  namespace: default
  name: filebeat
roleRef:
  kind: ClusterRole
  name: filebeat
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: filebeat
  labels:
    k8s-app: filebeat
rules:
- apiGroups: [""] # "" indicates the core API group
  resources:
  - namespaces
  - pods
  - nodes
  verbs:
  - get
  - watch
  - list
- apiGroups: ["apps"]
  resources:
    - replicasets
  verbs: ["get", "list", "watch"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: filebeat
  labels:
    k8s-app: filebeat
---
```

创建filebeat

```
# kubectl create -f filebeat-kubernetes.yaml
```



2.elasticsearch的安装

2.1 因为elasticsearch是有状态的服务，因此创建一个headless service，并且将clusterIP设置为None，创建一个文件es_service.yaml,文件内容如下

```
  kind: Service
  apiVersion: v1
  metadata:
    name: elasticsearch
    labels:
      app: elasticsearch
  spec:
    selector:
      app: elasticsearch
    clusterIP: None
    ports:
      - port: 9200
        name: rest
      - port: 9300
        name: inter-node
```

2.2 创建service

```
[root@master elfk]# kubectl create -f es_service.yaml 
service/elasticsearch created
```

2.3 storageclass、pv和pvc的创建，内容如下文件命名为es_pvc.yaml

```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: default
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
# Supported policies: Delete, Retain
reclaimPolicy: Delete

---
kind: PersistentVolume
apiVersion: v1
metadata:
  name: datadir1
  labels:
    type: local
spec:
  storageClassName: default
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/data/data1"

---
kind: PersistentVolume
apiVersion: v1
metadata:
  name: datadir2
  labels:
    type: local
spec:
  storageClassName: default
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/data/data2"

---
kind: PersistentVolume
apiVersion: v1
metadata:
  name: datadir3
  labels:
    type: local
spec:
  storageClassName: default
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: "/data/data3"

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: es-cluster
spec:
  serviceName: elasticsearch # provides association with our previously created elasticsearch Service.
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:7.5.0
        resources:
            limits:
              cpu: 1000m
              memory: "2Gi"
            requests:
              cpu: 100m
              memory: "1Gi"
        ports:
        - containerPort: 9200 # for REST API.
          name: rest
          protocol: TCP
        - containerPort: 9300 # for inter-node communication.
          name: inter-node
          protocol: TCP
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
        env:
          - name: cluster.name
            value: k8s-logs
          - name: node.name
            valueFrom:
              fieldRef:
                fieldPath: metadata.name
          - name: discovery.seed_hosts
            value: "es-cluster-0.elasticsearch, es-cluster-1.elasticsearch,es-cluster-2.elasticsearch"
          - name: cluster.initial_master_nodes
            value: "es-cluster-0,es-cluster-1,es-cluster-2"
          - name: ES_JAVA_OPTS
            value: "-Xms1g -Xmx1g"
      initContainers:
      - name: fix-permissions
        image: busybox
        command: ["sh", "-c", "chown -R 1000:1000 /usr/share/elasticsearch/data"]
        securityContext:
          privileged: true
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
      - name: increase-vm-max-map
        image: busybox
        command: ["sysctl", "-w", "vm.max_map_count=262144"]
        securityContext:
          privileged: true
      - name: increase-fd-ulimit
        image: busybox
        command: ["sh", "-c", "ulimit -n 65536"]
        securityContext:
          privileged: true
  volumeClaimTemplates:
  - metadata:
      name: data
      labels:
        app: elasticsearch
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: default
      resources:
        requests:
          storage: 2Gi

```

2.4创建动态存储

```
# kubectl create -f es_pvc.yaml
```

2.5 创建StatefulSet资源，关联之前创建的elasticsearch service，这里创建一个叫es_statefulset.yaml的文件

```
# kubectl create -f es_statefulset.yaml
```

文件内容如下

```
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: es-cluster
spec:
  serviceName: elasticsearch # provides association with our previously created elasticsearch Service.
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:7.5.0
        resources:
            limits:
              cpu: 1000m
              memory: "2Gi"
            requests:
              cpu: 100m
              memory: "1Gi"
        ports:
        - containerPort: 9200 # for REST API.
          name: rest
          protocol: TCP
        - containerPort: 9300 # for inter-node communication.
          name: inter-node
          protocol: TCP
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
        env:
          - name: cluster.name
            value: k8s-logs
          - name: node.name
            valueFrom:
              fieldRef:
                fieldPath: metadata.name
          # sets a list of master-eligible nodes in the cluster.
          - name: discovery.seed_hosts
            value: "es-cluster-0.elasticsearch, es-cluster-1.elasticsearch,es-cluster-2.elasticsearch"
          # specifies a list of master-eligible nodes that will participate in the master election process.
          - name: cluster.initial_master_nodes
            value: "es-cluster-0,es-cluster-1,es-cluster-2"
          - name: ES_JAVA_OPTS
            value: "-Xms1g -Xmx1g"
      # Each init containers run to completion in the specified order.
      initContainers:
      # By default k8s mounts the data directory as root, which renders it inaccessible to Elasticsearch.
      - name: fix-permissions
        image: busybox
        command: ["sh", "-c", "chown -R 1000:1000 /usr/share/elasticsearch/data"]
        securityContext:
          privileged: true
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
      # To prevent OOM errors.
      - name: increase-vm-max-map
        image: busybox
        command: ["sysctl", "-w", "vm.max_map_count=262144"]
        securityContext:
          privileged: true
      # Increase the max number of open file descriptors. 
      - name: increase-fd-ulimit
        image: busybox
        command: ["sh", "-c", "ulimit -n 65536"]
        securityContext:
          privileged: true
  # PersistentVolumes for the Elasticsearch pods.
  volumeClaimTemplates:
  - metadata:
      name: data
      labels:
        app: elasticsearch
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: default
      resources:
        requests:
          storage: 10Gi
```



2.6 查看elasticsearch pod是否创建成功

>[root@node1 ~]# kubectl get pods -o wide
>NAME               READY   STATUS    RESTARTS   AGE   IP            NODE    NOMINATED NODE   READINESS GATES
>es-cluster-0       1/1     Running   0          24h   10.244.2.73   node2   <none>           <none>
>es-cluster-1       1/1     Running   0          24h   10.244.3.66   node3   <none>           <none>
>es-cluster-2       1/1     Running   0          24h   10.244.2.74   node2   <none>           <none>

2.7 测试9200端口是否可用

```
# kubectl port-forward svc/elasticsearch 9200
```

2.8 重新开一个终端，测试elasticsearch集群是否部署成功，返回如下，表明成功

>[root@node1 ~]# curl http://localhost:9200/_cat/health?v
>epoch      timestamp cluster  status node.total node.data shards pri relo init unassign pending_tasks max_task_wait_time active_shards_percent
>1621480045 03:07:25  k8s-logs green           3         3      0   0    0    0        0             0                  -                100.0%



3.部署logstash

3.1 ConfigMap文件内容如下

```
[root@master elfk]# cat ls_cm.yaml 
apiVersion: v1
kind: ConfigMap
metadata:
  name: logstash-config
data:
  logstash.conf: |-
      input {
        beats {
            port => "9600"
        }
      }
      output {
        elasticsearch {
            hosts => "elasticsearch:9200"
            index => "k8s-system-log-%{+YYYY.MM.dd}"
        }
      }
```

3.2 deployment内容如下

```
[root@master elfk]# cat ls_dp.yaml 
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: logstash
spec:
  selector:
    matchLabels:
      app: logstash
  template:
    metadata:
      labels:
        app: logstash
    spec:
      hostname: logstash
      containers:
      - name: logstash
        ports:      
          - containerPort: 9600
            name: logstash
        image: docker.elastic.co/logstash/logstash:7.5.0
        volumeMounts:
        - name: logstash-config
          mountPath: /usr/share/logstash/pipeline/
        command:
        - logstash
      volumes:
      # Previously defined ConfigMap object.
      - name: logstash-config
        configMap:
          name: logstash-config
          items:
          - key: logstash.conf
            path: logstash.conf
---
kind: Service
apiVersion: v1
metadata:
  name: logstash
spec:
  type: NodePort
  selector:
    app: logstash
  ports:  
  - protocol: TCP
    port: 9600
    targetPort: 9600
    name: logstash
---
```

3.3 分别对上列文件进行创建操作,完成logstash的部署

```
# kubectl create -f ls_cm.yaml 
# kubectl create -f ls_dp.yaml
```



4.部署kibana

4.1 deployment文件内容如下

```
[root@master elfk]# cat kibana.yaml 
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana
  labels:
    k8s-app: kibana
spec:
  selector:
    matchLabels:
      k8s-app: kibana
  template:
    metadata:
      labels:
        k8s-app: kibana
    spec:
      containers:
      - name: kibana
        image: docker.elastic.co/kibana/kibana:7.5.0
        resources:
          requests:
            cpu: 100m
          limits:
            cpu: 1000m
        env:
          - name: ELASTICSEARCH_URL
            value: http://elasticsearch.operations:9200
          - name: SERVER_MAXPAYLOADBYTES
            value: '1024000000'
        ports:
        - containerPort: 5601
          name: ui
          protocol: TCP
---
apiVersion: v1
kind: Service
metadata:
  name: kibana
  labels:
    k8s-app: kibana
spec:
  ports:
  - port: 5601
    protocol: TCP
    targetPort: ui
  selector:
    k8s-app: kibana
  type: NodePort
```

4.2 建kibana的pod

```
# kubectl create -f kibana.yaml
```

4.3 查看kibana服务映射的端口号

```
[root@master elfk]# kubectl get svc kibana
NAME     TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
kibana   NodePort   10.99.187.167   <none>        5601:50050/TCP   22h
```

4.4 通过50050端口号访问kibana

![](/img/2021-05-28/2.png)

添加elasticsearch

![](/img/2021-05-28/3.png)

自动发现elasticsearch

![](/img/2021-05-28/4.png)



添加索引

![](/img/2021-05-28/5.png)



![](/img/2021-05-28/6.png)

如果添加正确，会有日志显现

![](/img/2021-05-28/7.png)



输入个关键字查看是否能够检索到

![](/img/2021-05-28/8.png)

---







声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。





