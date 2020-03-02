from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
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
######################################################
driver.find_element_by_class_name('_2GjXc').click()
print("点击我的课程之后的url")
print(driver.current_url)
time.sleep(15)


driver.find_element_by_class_name('_1kz8o').click()
time.sleep(5)
windows=driver.window_handles
driver.switch_to.window(windows[1])

print("点击进入学习后")
print(driver.current_url)
url_list=[]
video_name_list=[]
k=driver.find_elements_by_class_name('_1zb')
count=1
for i in k:
    if count == 1:
        video_name = i.text
        video_name_list.append(video_name)
        i.click()
        time.sleep(5)
        windows=driver.window_handles
        driver.switch_to.window(windows[2])
        print("%s的url" % video_name )
        time.sleep(2)
        print(driver.find_element_by_id('myVideo_html5_api').get_attribute('src'))
        url_list.append(driver.find_element_by_id('myVideo_html5_api').get_attribute('src'))
        count += 1
        driver.close()
    else:
        windows=driver.window_handles
        driver.switch_to.window(windows[1])
        time.sleep(3) 
        if (count == 24) or (count == 25) or (count == 26):
            count += 1
            continue
        elif count == 27:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="2019年逻辑英语痴学社·CATTI专题"]').click()
        elif count == 29:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="第一阶：中英文对切基本公式"]').click()
        elif count == 36:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="第二阶：单词的前世今生"]').click()
        elif count == 42:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="第三阶：语法核心重建"]').click()
        elif count == 50:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="第四阶：伦敦腔及听力重建"]').click()
        elif count == 58:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="第五阶：极致美学作文修辞"]').click()
        elif count == 68:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="零基础关怀礼包"]').click()
        elif count == 76:
            js="window.scrollTo(0,400);"
            driver.execute_script(js)
            time.sleep(1)
            driver.find_element_by_xpath('//*[text()="专属考试大招课"]').click()
        elif count >= 79:
            break
        else:
            pass
        video_name = i.text
        time.sleep(1)
        i.click()
        time.sleep(5)
        windows=driver.window_handles
        driver.switch_to.window(windows[-1])
        print("%s的url" % video_name )
#        print(driver.current_url)
        time.sleep(2)
        video_url=driver.find_element_by_id('myVideo_html5_api').get_attribute('src')
        print(video_url)
        video_name_list.append(video_name)
        url_list.append(video_url)
        count += 1
        driver.close()
        print(count)
print(url_list)
for i in url_list:
    with open('video_url_list.txt','a+') as fp:
        fp.write(i+"\n")
for o in video_name_list:
    with open('video_name_list.txt','a+') as fp:
        fp.write(o+"\n")
