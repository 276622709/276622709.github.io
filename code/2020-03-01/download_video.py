from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import subprocess
import requests
import wget
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(executable_path="./chromedriver",chrome_options=chrome_options)
driver.get("https://ke.youdao.com/")
time.sleep(1)
driver.find_element_by_class_name('_1u03u').click()
time.sleep(2)
driver.find_element_by_class_name('_2TY2B').click()
time.sleep(15)
print("扫描二维码之后的url")
print(driver.current_url)
driver.find_element_by_class_name('_2GjXc').click()
print("点击我的课程之后的url")
print(driver.current_url)
result1,url_content=subprocess.getstatusoutput('cat video_url_list.txt')
result2,video_name_content=subprocess.getstatusoutput('cat video_name_list.txt')
url_list=url_content.split("\n")
video_name_list=video_name_content.split("\n")
url_to_name=zip(url_list,video_name_list)
url_to_name_list=[]
for i in url_to_name:
    url_to_name_list.append(list(i))

cookies=driver.get_cookies()
driver.close()
sess=requests.Session()
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063','Host':'stream.ydstatic.com','Referer':'http://live.youdao.com/live/index.html'}
for cookie in cookies:
    sess.cookies.set(cookie['name'],cookie['value'])
#data=sess.get(url='https://stream.ydstatic.com/private/xuetang/-646118947_180319185954.mp4',headers=headers).content
for i in url_to_name_list:
    url,name=i
    data=sess.get(url=url,headers=headers).content
    name=name.strip()
    newname=name+'.mp4'
    path='/Volumes/Untitled/有道精品课/'
    allname=path+newname
    with open(allname,'wb') as fp:
        fp.write(data)
        print("%s#####下载成功!" %newname)
