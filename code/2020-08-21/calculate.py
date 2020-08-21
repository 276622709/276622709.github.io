# -*- coding:utf-8 -*-
from tkinter import *
root=Tk()
#setup the attribute of screen
screenwidth=root.winfo_screenwidth()
screenheight=root.winfo_screenheight()
x=screenwidth-400
y=screenheight-600
root.geometry("220x270+%d+%d" %(x/2,y/2))
root.resizable(0,0)
root.title("calculate")
content=""
#show function
def show(arg):
    global content
    content+=arg
    label["text"]=content
#eq function
def eq(arg):
    global content
    label["text"] = (content + "=\n" + str(eval(content)))
#clear function
def clear():
    global content
    label["text"]="0"
    content=""
#bdel function
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
#button layout
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