import os
import subprocess
path="/root/samples_test_after_filter" #过滤后待识别的图片验证码
sum=0
for filename in os.listdir(path):
    sumnumber=len(os.listdir(path)) #待识别的文件总数
    fileindexname=filename.split(".")[0] #取文件名.前面的部分
    absolutefilename=path+'/'+filename #取绝对路径文件名
    outputfilename=os.getcwd()+'/'+'file' #tesseract识别后生成的文件名
    readoutputfile=os.getcwd()+'/'+'file.txt'#读取tesseract生成的文件名
    command1="tesseract %s %s -l engnum" %(absolutefilename,outputfilename) #执>行tesseract识别图片验证码命令参数保存在command1中
    command2="cat %s" %readoutputfile  #将识别出的结果保存在command2变量中
    os.system(command1)  #将识别结果保存到file.txt中
    value=subprocess.getoutput(command2) #取出识别结果赋值给value变量
    value_strip_blank=value.lower().strip().replace(' ','') #字母变小写后再去掉>识别过程中存在的空格
    if fileindexname == value_strip_blank:
        sum=sum+1
    print("当前图片识别结果是:%s" % value_strip_blank)
    print("图片应当别识别为:%s" % fileindexname)
print("识别率为:{:.2%}".format(sum/int(sumnumber)))
