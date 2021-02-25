---
layout: post
title: 分析harbor容器的docker-compose.yml文件生成过程
date: 2021-02-24
author: ZMY
header-img: ../img/2021-02-24/background.png
catalog : true
tags:
   - harbor
   - prepare
typora-root-url: ..
---

## <img class="original" src='/img/original.png'>分析harbor容器的docker-compose.yml文件生成过程


根据官网文档安装harbor的过程中发现，harbor容器的安装过程极为简单，主要涉及几个操作
- 解压缩harbor-online压缩包
- 修改barbor.yml配置文件
- 执行install.sh脚本

项目执行前目录结构如下 
```
harbor
├── common.sh
├── harbor.yml.tmpl
├── install.sh
├── LICENSE
└── prepare
```
项目执行后目录结构如下
```
.
├── common
│   └── config
│       ├── core
│       │   ├── app.conf
│       │   ├── certificates
│       │   └── env
│       ├── db
│       │   └── env
│       ├── jobservice
│       │   ├── config.yml
│       │   └── env
│       ├── log
│       │   ├── logrotate.conf
│       │   └── rsyslog_docker.conf
│       ├── nginx
│       │   ├── conf.d
│       │   └── nginx.conf
│       ├── registry
│       │   ├── config.yml
│       │   ├── passwd
│       │   └── root.crt
│       ├── registryctl
│       │   ├── config.yml
│       │   └── env
│       └── shared
│           └── trust-certificates
├── common.sh
├── docker-compose.yml
├── harbor.yml
├── harbor.yml.tmpl
├── install.sh
├── LICENSE
└── prepare
```
可以看到项目执行前并不存在docker-compose.yml文件，项目执行后就生成了一些配置文件，其中包括了docker-compose.yml,那么docker-compose.yml是如何生成的呢。查看install.sh脚本并未找到docker-compose.yml和其他配置文件的生成过程。但是其中 87行 ./prepare $prepare_para 引起了我的注意，显然install.sh脚本在执行docker-compose up 之前执行了prepare 命令来生成了一些东西，那有可能是prepare脚本生成的docker-compose.yml这个文件，打开prepare看看。很遗憾没有找到docker-compose.yml生成的相关信息，但是却找到了一个 docker run命令生成了一个prepare容器，并且该容器运行后立刻删除
```
# docker run --rm -v $input_dir:/input:z \
                    -v $data_path:/data:z \
                    -v $harbor_prepare_path:/compose_location:z \
                    -v $config_dir:/config:z \
                    -v /:/hostfs:z \
                    goharbor/prepare:v2.0.6 prepare $@
```
显然答案就在这个容器中了,使用如下命令创建prepare容器，查看一下入口命令
```
# docker run -it goharbor/prepare:v2.0.6 prepare
# docker ps -a --no-trunc | grep prepare
```

容器最后入口命令是python main.py prepare，显然那些不存在的配置文件就是由这个命令搞出来的，接下来创建prepare容器并copy出main.py所在项目程序到本地进行分析
```
# docker run -it --entrypoint /bin/bash goharbor/prepare:v2.0.6
# docker cp `docker ps -a | grep prepare | awk '{print $1}'`:/usr/src/app ./
# cd app
```

列出main.py脚本所在目录结构，其中不必要的文件已删除

```
├── commands
│   ├── gencerts.py
│   ├── __init__.py
│   ├── migrate.py
│   ├── prepare.py
├── g.py
├── __init__.py
├── main.py
├── migrations
│   ├── __init__.py
│   └── version_2_0_0
│       ├── harbor.yml.jinja
│       └── __init__.py
├── models.py
├── scripts
│   └── gencert.sh
├── templates
│   ├── chartserver
│   │   └── env.jinja
│   ├── clair
│   │   ├── clair_env.jinja
│   │   ├── config.yaml.jinja
│   │   ├── postgres_env.jinja
│   │   └── postgresql-init.d
│   │       └── README.md
│   ├── clair-adapter
│   │   └── env.jinja
│   ├── core
│   │   ├── app.conf.jinja
│   │   └── env.jinja
│   ├── db
│   │   └── env.jinja
│   ├── docker_compose
│   │   └── docker-compose.yml.jinja
│   ├── jobservice
│   │   ├── config.yml.jinja
│   │   └── env.jinja
│   ├── log
│   │   ├── logrotate.conf.jinja
│   │   └── rsyslog_docker.conf.jinja
│   ├── nginx
│   │   ├── nginx.http.conf.jinja
│   │   ├── nginx.https.conf.jinja
│   │   ├── notary.server.conf.jinja
│   │   └── notary.upstream.conf.jinja
│   ├── notary
│   │   ├── server-config.postgres.json.jinja
│   │   ├── server_env.jinja
│   │   ├── signer-config.postgres.json.jinja
│   │   └── signer_env.jinja
│   ├── registry
│   │   └── config.yml.jinja
│   ├── registryctl
│   │   ├── config.yml.jinja
│   │   └── env.jinja
│   └── trivy-adapter
│       └── env.jinja
├── tests
│   └── migrations
│       └── utils_test.py
├── utils
│   ├── cert.py
│   ├── chart.py
│   ├── clair_adapter.py
│   ├── clair.py
│   ├── configs.py
│   ├── core.py
│   ├── db.py
│   ├── docker_compose.py
│   ├── __init__.py
│   ├── internal_tls.py
│   ├── jinja.py
│   ├── jobservice.py
│   ├── log.py
│   ├── migration.py
│   ├── misc.py
│   ├── nginx.py
│   ├── notary.py
│   ├── proxy.py
│   ├── redis.py
│   ├── registry_ctl.py
│   ├── registry.py
│   └── trivy_adapter.py
└── versions
```

下面以docker-compose.yml文件生成为例，分析一下文件生成过程，其他文件同理  

1.程序主入口main.py  

2.click装饰器分析命令行参数  

3.prepare函数一阶段根据harbor.yml获取config_dict中必要参数  

4.prepare函数二阶段根据config_dict值使用jinjia2模块渲染docker-compose.yml.jinja文件生成docker-compose.yml文件用于部署harbor容器

因为这里只分析prepare执行过程，因此将不必要的代码注释掉    

 main.py内容如下

>```
>from commands.prepare import prepare
>#from commands.gencerts import gencert
>#from commands.migrate import migrate
>import click
>
>@click.group()
>def cli():
>    pass
>
>cli.add_command(prepare)
>#cli.add_command(gencert)
>#cli.add_command(migrate)
>
>if __name__ == '__main__':
>    cli()
>```

from commands.prepare import prepare

---->prepare.py :29-35行

>```
>29 @click.command()
>30 @click.option('--conf', default=input_config_path, help="the path of Harbor configuration file")
>31-34 ******
>35 def prepare(conf, with_notary, with_clair, with_trivy, with_chartmuseum):
>```

以上代码相当于prepare=click.command(click.option(prepare))，下面分成2段解析代码执行过程  

1）第一段如下，这里涉及到了装饰器，对装饰器有疑问的可以查看官方文档进行解读

f=click.option('--conf', default=input_config_path, help="the path of Harbor configuration file")(prepare)

--->decorators.py:175行

跳进option函数开始，这一阶段主要功能是将conf参数包装成Option类实例，保存到f的__click_params__属性中

f代指prepare函数

```
def option(*param_decls, **attrs): # param_decls: --conf attrs: {default=input_config_path, help="the path of Harbor configuration file"}
```

--->decorators.py:186行

```
def decorator(f):     #params: f:<function prepare>
```

--->decorators.py:196行

```
return decorator
```

---->decorator.py:192行  

设置OptionClass为Option类

```
OptionClass = option_attrs.pop("cls", Option)  #OptionClass: <class Option>
```

---->decorator.py:193行

```
_param_memo(f, OptionClass(param_decls, **option_attrs))
```

调用OptionClass(param_decls, **option_attrs)，即调用Option()

​        ---->core.py:1654行

```
class Option(Parameter):
```

​               ---->core.py:1715行

```
Parameter.__init__(self, param_decls, type=type, **attrs)  
```

​                       ---->core.py:1483行

设置self.name self.opts属性值

```
self.name, self.opts, self.secondary_opts = self._parse_decls(
            param_decls or (), expose_value)     # self:<class Option: conf>  self.name: conf  self.opts: '--conf'
```

​                              ---->core.py:1782行

```
def _parse_decls(self, decls, expose_value):   
```

​                              ---->core.py:1824行

```
return name, opts, secondary_opts    # name:{str} 'conf'   opts:{list} ['--conf']
```

​        ---->decorator.py:147行

```
def _param_memo(f, param):
```

​        ---->decorator.py:153行

```
f.__click_params__.append(param)
```

给f的__click_params__属性添加 conf参数，conf为被装饰的Option类  

2）prepare=click.command(f)  

这段代码主要是将prepare包装成Command实例，并附加conf参数  

---->decorators.py:108行

```
def command(name=None, cls=None, **attrs):
```

---->decorators.py:129行

对cls赋值为Command类

```
cls = Command 
```

---->decorators.py:132行

```
cmd = _make_command(f, name, attrs, cls)
```

​      ---->decorators.py:84行 

"__click_params__" 保存着之前option()命令添加的 Option类的实例conf

```
params = f.__click_params__
```

---->decorators.py:99-104行

返回实例化Command类后的值

```
return cls(
    name=name or f.__name__.lower().replace("_", "-"),
    callback=f,
    params=params,
    **attrs
)
```

​      ---->core.py:833行

```
class Command(BaseCommand):
```

​      ---->core.py:881行

```
BaseCommand.__init__(self, name, context_settings)
```

3）

>@click.group()
>def cli():
>pass

---->decorators.py: 139行

```
def group(name=None, **attrs):
```

---->decorators.py: 144行

将cls设置为Group类

```
attrs.setdefault("cls", Group)
```

---->decorators.py: 145行

```
return command(name, **attrs)
```

​      ---->decorators.py: 108行

```
def command(name=None, cls=None, **attrs):
```

​      ---->decorators.py: 136行

```
return decorator
```

---->group(cli)

---->decorators.py: 132行

```
cmd = _make_command(f, name, attrs, cls)
```

​      ---->decorators.py: 100-105行

cls为Group，实例化Group对象

```
return cls(
    name=name or f.__name__.lower().replace("_", "-"),
    callback=f,
    params=params,
    **attrs
)
```

​            ---->core.py：1340行

```
MultiCommand.__init__(self, name, **attrs)
```

​                  ---->core.py: 1107行

```
Command.__init__(self, name, **attrs)
```

​                        ---->core.py: 881行

```
BaseCommand.__init__(self, name, context_settings)
```

----> decorators.py: 134行  

cmd值为Group类实例 

```
return cmd   #<Group cli>
```

4）

>cli.add_command(prepare)

---->decorators.py: 1344行

```
def add_command(self, cmd, name=None):
```

---->decorators.py: 1351行

```
_check_multicommand(self, name, cmd, register=True)
```

主要作用是向cli.commands添加prepare实例

5）

>if __name__ == '__main__':
>
>​    cli()

---->core.py: 828行

实例cli直接调用执行BaseCommand类的__call__方法

```
def __call__(self, *args, **kwargs):
```

---->core.py: 830行

```
return self.main(*args, **kwargs)
```

​      ---->core.py: 716行

```
def main(
```

​      ---->core.py:766行

得到用户输入的命令行参数

```
args = get_os_args()
```

---->core.py: 782行

保存上下文环境ctx

```
with self.make_context(prog_name, args, **extra) as ctx:
```

---->core.py: 783行

```
rv = self.invoke(ctx)
```

​      ---->core.py: 1260行

```
return _process_result(sub_ctx.command.invoke(sub_ctx))
```

​            ---->core.py: 1067行

```
return ctx.invoke(self.callback, **ctx.params)
```

​                  ---->core.py:610行

callback为prepare

```
return callback(*args, **kwargs)
```

---->prepare.py: 35行

```
def prepare(conf, with_notary, with_clair, with_trivy, with_chartmuseum):
```

至此进入prepare函数中，根据命令行参数和预配置执行创建文件，最后合成一个docker-compose.yml配置文件

这里一样，单独分析其中一个redis组件配置过程，将其他的相同类型的注释掉

```
delfile(config_dir)
config_dict = parse_yaml_config(conf, with_notary=with_notary, with_clair=with_clair, with_trivy=with_trivy, with_chartmuseum=with_chartmuseum)
try:
    validate(config_dict, notary_mode=with_notary)
except Exception as e:
    click.echo('Error happened in config validation...')
    logging.error(e)
    sys.exit(-1)

#prepare_log_configs(config_dict)
#prepare_nginx(config_dict)
#prepare_core(config_dict, with_notary=with_notary, with_clair=with_clair, #with_trivy=with_trivy, with_chartmuseum=with_chartmuseum)
#prepare_registry(config_dict)
#prepare_registry_ctl(config_dict)
#prepare_db(config_dict)
#prepare_job_service(config_dict)
prepare_redis(config_dict)
#prepare_tls(config_dict)
#prepare_trust_ca(config_dict)

#get_secret_key(secret_key_dir)

#  If Customized cert enabled
#prepare_registry_ca(
#    private_key_pem_path=private_key_pem_path,
#    root_crt_path=root_crt_path,
#    old_private_key_pem_path=old_private_key_pem_path,
#    old_crt_path=old_crt_path)

#if with_notary:
#    prepare_notary(config_dict, nginx_confd_dir, SSL_CERT_PATH, SSL_CERT_KEY_PATH)

#if with_clair:
#    prepare_clair(config_dict)
#    prepare_clair_adapter(config_dict)

#if with_trivy:
#    prepare_trivy_adapter(config_dict)

#if with_chartmuseum:
#    prepare_chartmuseum(config_dict)

prepare_docker_compose(config_dict, with_clair, with_trivy, with_notary, with_chartmuseum)
```

----> prepare.py: 38行  

这里conf为harbor.yml  

```
 config_dict = parse_yaml_config(conf, with_notary=with_notary, with_clair=with_clair, with_trivy=with_trivy, with_chartmuseum=with_chartmuseum)

```

---->configs.py: 99行

分析harbor.yml文件，最终返回一个dict类型的变量config_dict，里面包含预定义的参数和从yml文件匹配的的参数,比较简单，我这里直接输出config_dict最终结果

```
def parse_yaml_config(config_file_path, with_notary, with_clair, with_trivy, with_chartmuseum):

```

这里由于启动脚本的时候没有附带--with-notary、--with-clair、--with-trivy、--with-chartmuseum参数所以根据click定义，这四个参数在命令行中没有给出，都为False

>config_dict = {
>         'registry_url': 'http://registry:5000',
>         'registry_controller_url': 'http://registryctl:8080',
>         'core_url': 'http://core:8080',
>         'core_local_url': 'http://127.0.0.1:8080',
>         'token_service_url': 'http://core:8080/service/token',
>         'jobservice_url': 'http://jobservice:8080',
>         'clair_url': 'http://clair:6060',
>         'clair_adapter_url': 'http://clair-adapter:8080',
>         'trivy_adapter_url': 'http://trivy-adapter:8080',
>         'notary_url': 'http://notary-server:4443',
>         'chart_repository_url': 'http://chartmuseum:9999',
>         'public_url':'http://192.168.140.210',
>         'harbor_db_host:'postgresql',
>         'harbor_db_port':5432,
>         'harbor_db_name':'registry',
>         'harbor_db_username':'postgres',
>         'harbor_db_password':'root123',
>         'harbor_db_sslmode':'disable' ,
>         'harbor_db_max_idle_conns':50,
>         'harbor_db_max_open_conns':1000,
>         'harbor_db_host:'postgresql',
>         'data_volume':'/data',
>         'harbor_admin_password':'Harbor12345',
>         'registry_custom_ca_bundle_path':'',
>         'core_http_proxy':'',
>         'core_https_proxy':'',
>         'clair_db':'postgres',
>         'clair_updaters_interval':12,
>         'trivy_github_token':'',
>         'trivy_skip_update':False,
>         'trivy_skip_update':False,
>         'trivy_skip_update':False,
>         'trivy_skip_update':False,
>         'trivy_skip_update':10,
>         'jobservice_secret':jsde24f3w4df342n,
>         'webhook_job_max_retry':10,
>         'log_level':'info',
>         'log_location':'/var/log/harbor',
>         'log_rotate_count':50,
>         'log_rotate_size':'200M',
>         'log_external':False,
>         'external_database':False,
>         'redis_host':'redis',
>         'redis_port':6379,
>         'redis_password':'',
>         'redis_db_index_reg':1,
>         'redis_db_index_js':2,
>         'redis_db_index_chart':3,
>         'redis_db_index_chart':30,
>         'redis_url_js':'redis://redis:6379/2',
>         'redis_url_reg':'redis://redis:6379/1',
>         'core_secret':'ddwwe243d2de3d23',
>         'uaa':'',
>         'registry_username':'harbor_registry_user',
>         'registry_password':'y4h7dd6ff3lmn23bh7g4vvd349jgd3s4',
>         'internal_tls':'InternalTLS()'
>
>​     }

jobservice_secret、core_secret、registry_password是通过secrets模块得到的16位和32位随机生成数，internal_tls.enabled值为False,然后其中关于redis参数是通过下面这个332行代码得到的

```
config_dict.update(get_redis_configs(configs.get("external_redis", None), with_clair, with_trivy))
```

这个函数得到的内容为dict，值更新到上面的config_dict中

>configs={
>
>'redis_host':'redis',
>'redis_port':6379,
>'redis_password':'',
>'redis_db_index_reg':1,
>'redis_db_index_js':2,
>'redis_db_index_chart':3,
>'redis_db_index_chart':30,
>'redis_url_js':'redis://redis:6379/2',
>'redis_url_reg':'redis://redis:6379/1',
>
>}

--->prepare.py: 40行  

验证config_dict生成的键值对是否存在错误值，如存在错误值根据相应raise进行错误警告

```
 validate(config_dict, notary_mode=with_notary)
```

---->prepare.py: 53行

```
prepare_redis(config_dict)
```

​      ---->redis.py: 8行

```
def prepare_redis(config_dict):
```

​            ---->misc.py: 81行  

创建redis目录(在prepare容器中执行)，并赋值权限，根据uid,gid更改所有者  uid,gid值从/utils/g.py中获取

```
def prepare_dir(root: str, *args, **kwargs) -> str:
```

----> prepare.py: 79行  

最终目的是生成docker-compose.yml文件使用docker-compose部署harbor容器  
模板文件:docker-compose.yml.jinja  
生成yml:/compose_location/docker-compose.yml

```
prepare_docker_compose(config_dict, with_clair, with_trivy, with_notary, with_chartmuseum)

```

​      ---->docker_compose.py: 11行  
config为之前生成的config_dict  

```
def prepare_docker_compose(configs, with_clair, with_trivy, with_notary, with_chartmuseum):
```

​      ---->docker_compose.py: 15-34行  
VERSION_TAG值为versions文件中VERSION_TAG的值，configs对应的值可以在config_dict找到

```
 15     rendering_variables = {
 16         'version': VERSION_TAG,
 17         'reg_version': VERSION_TAG,
 18         'redis_version': VERSION_TAG,
 19         'notary_version': VERSION_TAG,
 20         'clair_version': VERSION_TAG,
 21         'clair_adapter_version': VERSION_TAG,
 22         'trivy_adapter_version': VERSION_TAG,
 23         'chartmuseum_version': VERSION_TAG,
 24         'data_volume': configs['data_volume'],
 25         'log_location': configs['log_location'],
 26         'protocol': configs['protocol'],
 27         'http_port': configs['http_port'],
 28         'external_redis': configs['external_redis'],
 29         'external_database': configs['external_database'],
 30         'with_notary': with_notary,
 31         'with_clair': with_clair,
 32         'with_trivy': with_trivy,
 33         'with_chartmuseum': with_chartmuseum
 34     }
```

​      ---->docker_compose.py: 64行

```
 render_jinja(docker_compose_template_path, docker_compose_yml_path,  mode=0o644, **rendering_variables)
```

​            ---->jinja.py: 6行

```
def render_jinja(src, dest,mode=0o640, uid=0, gid=0, **kw):
```

​            ---->jinja.py: 9行  
kw为rendering_variables

```
f.write(t.render(**kw))
```

​                  ---->misc.py: 10行  
更改文件权限，设置uid和gid

```
def mark_file(path, mode=0o600, uid=DEFAULT_UID, gid=DEFAULT_GID):
```

至此docker-compose.yml文件生成完毕





声明：本博客的<img class="original" src='/img/original.png'>原创文章，都是本人平时学习所做的笔记，转载请标注出处，谢谢合作。
