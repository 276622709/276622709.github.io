---
layout: post
title: 使用tkinter模拟windows计算器程序
date: 2020-08-21
author: ZMY
header-img: img/post-bg-desk.jpg
catalog : true
tags:
    - python 
    - tkinter 
    - 计算器
---

## <img class="original" src='https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/original.png'>使用tkinter模拟windows计算器程序

## 背景
最近用计算器比较频繁，随合计用python做一个图形化程序，后用pyinstaller打包做成exe文件，可以在win7上直接运行  
## 前提条件
+ python3.7环境
+ win7环境
+ pyinstaller打包程序

## 1.计算器程序设计思路
tkinter是python里自带的模块，可以直接使用
tkinter设计思路
1.创建按钮
2.按钮布局
3.逻辑函数处理
## 2.程序说明
```
# -*- coding:utf-8 -*-
from tkinter import *
root=Tk()
#主屏幕设计
screenwidth=root.winfo_screenwidth()
screenheight=root.winfo_screenheight()
x=screenwidth-400
y=screenheight-600
root.geometry("220x270+%d+%d" %(x/2,y/2))
root.resizable(0,0)
root.title("calculate")
content=""
#show函数，变化显示屏内容
def show(arg):
    global content
    content+=arg
    label["text"]=content
#eq函数，按=计算结构
def eq(arg):
    global content
    label["text"] = (content + "=\n" + str(eval(content)))
#clear函数，清空输入
def clear():
    global content
    label["text"]="0"
    content=""
#bdel函数，删除错误输入
def bdel():
    global content
    content = content[:-1]
    label["text"]=content

#display calculate value
label=Label(root,text="0",width=30,height=3,anchor=SE,relief="raised")
label.grid(row=0,columnspan=4)
#button setup
c=Button(root,text='C',width=6,height=2,command=lambda:clear())
bdel=Button(root,text='DEL',width=6,height=2,command=bdel)
bai=Button(root,text='%',width=6,height=2,command=lambda:show("%"))
div=Button(root,text='/',width=6,height=2,command=lambda:show("/"))
b7=Button(root,text='7',width=6,height=2,command=lambda:show("7"))
b8=Button(root,text='8',width=6,height=2,command=lambda:show("8"))
b9=Button(root,text='9',width=6,height=2,command=lambda:show("9"))
mul=Button(root,text='*',width=6,height=2,command=lambda:show("*"))
b4=Button(root,text='4',width=6,height=2,command=lambda:show("4"))
b5=Button(root,text='5',width=6,height=2,command=lambda:show("5"))
b6=Button(root,text='6',width=6,height=2,command=lambda:show("6"))
sub=Button(root,text='-',width=6,height=2,command=lambda:show("-"))
b1=Button(root,text='1',width=6,height=2,command=lambda:show("1"))
b2=Button(root,text='2',width=6,height=2,command=lambda:show("2"))
b3=Button(root,text='3',width=6,height=2,command=lambda:show("3"))
add=Button(root,text='+',width=6,height=2,command=lambda:show("+"))
b0=Button(root,text='0',width=14,height=2,command=lambda:show("0"))
bdot=Button(root,text='.',width=6,height=2,command=lambda:show("."))
bcal=Button(root,text='=',width=6,height=2,command=lambda:eq("="))
#各按钮在屏幕上布局
c.grid(row=1,column=0,padx=1,pady=1)
bdel.grid(row=1,column=1,padx=1,pady=1)
bai.grid(row=1,column=2,padx=1,pady=1)
div.grid(row=1,column=3,padx=1,pady=1)
b7.grid(row=2,column=0,padx=1,pady=1)
b8.grid(row=2,column=1,padx=1,pady=1)
b9.grid(row=2,column=2,padx=1,pady=1)
mul.grid(row=2,column=3,padx=1,pady=1)
b4.grid(row=3,column=0,padx=1,pady=1)
b5.grid(row=3,column=1,padx=1,pady=1)
b6.grid(row=3,column=2,padx=1,pady=1)
sub.grid(row=3,column=3,padx=1,pady=1)
b1.grid(row=4,column=0,padx=1,pady=1)
b2.grid(row=4,column=1,padx=1,pady=1)
b3.grid(row=4,column=2,padx=1,pady=1)
add.grid(row=4,column=3,padx=1,pady=1)
b0.grid(row=5,column=0,columnspan=2,padx=1,pady=1)
bdot.grid(row=5,column=2,padx=1,pady=1)
bcal.grid(row=5,column=3,padx=1,pady=1)


root.mainloop()
```
## 3.安装打包工具pyinstaller  
```
#pip3 install pyinstaller
```
## 4.制作exe程序
其中sitemap_gen_baidu_auto_push.py是自己修改的，你需要修改脚本中的变量curloption,变量值为百度站长中你自己拥有的curl命令脚本  
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-23/1.png)

项目参考地址<http://toncar.cz/opensource/sitemap_gen.html>  
## 2.执行脚本命令生成sitemap.xml,并将博客网址主动推送给百度站长平台
```
#python sitemap_gen_baidu_auto_push.py -o sitemap.xml -c always http://www.zmy024.cn
```
如下图所示出现success即为成功   
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-23/2.png)
## 3.git更新blog和sitemap.xml文件
参考之前我写的blog
<https://276622709.github.io/2018/09/28/github%E5%88%9D%E6%AD%A5%E4%BD%BF%E7%94%A8/>
## 4.登陆百度站长平台将自己博客的sitemap.xml网址添加
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-23/3.png)
![](https://raw.githubusercontent.com/276622709/276622709.github.io/master/img/2020-03-23/4.png)
以后每次更新博客后通过该脚本即可主动更新sitemap.xml内容并推送给百度站长平台  
