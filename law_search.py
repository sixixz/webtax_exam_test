import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import os

host = 'https://www.webtax.com.cn/'
chromedriver = "D:\python/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
browser = webdriver.Chrome(chromedriver)
# browser.maximize_window()  # 窗口最大化
browser.get(host)
first_window_handle = browser.current_window_handle  # 获取当前（百度首页）的窗口句柄
# print('now handle is : ', first_window_handle)  # 打印百度首页窗口句柄
time.sleep(1)


def law_search():
    # 点击进入法规库
    browser.find_element(by=By.XPATH, value="// *[ @ id = \"__layout\"] / div / div[1] / div / div / ul / li[3]").click()
    # 等待界面加载完毕
    WebDriverWait(browser, 8, 0.5, ignored_exceptions=TimeoutException).until(
        lambda x: x.find_element(by=By.XPATH, value="//*[@id=\"__layout\"]/div/div[2]/div[1]").is_displayed(), message='请求超时')
    law = browser.current_window_handle
    # 点击输入框
    input_box = browser.find_element(by=By.XPATH, value="//*[@id=\"__layout\"]/div/div[2]/div[1]/div/div[1]/div[1]/div/input")
    input_box.click()
    time.sleep(1)
    input_box.send_keys("财税201636")
    input_box.send_keys(Keys.RETURN)  # 输入回车键
    time.sleep(2)
    articles = browser.find_element(by=By.XPATH, value="//*[@id=\"__layout\"]/div/div[2]/div[2]/div[2]/ul//a")
    path = os.getcwd()
    if not os.path.exists('article'):
        os.mkdir(path + '\\article')
    os.chdir(path + '\\article')
    for eacharticle in articles:
        # url = eacharticle.get_attribute("href")
        eacharticle.click()
        # second_window_handle = browser.current_window_handle  # 再获取一次窗口句柄并打印
        # print('and now handle is : ', second_window_handle)
    all_handles = browser.window_handles  # 获取所有窗口句柄
    for window in all_handles:
        if window != first_window_handle:
            # print('and and now handle is : ', window)
            browser.switch_to.window(window)  # 切换到非首页的窗口
            WebDriverWait(browser, 8, 0.5, ignored_exceptions=TimeoutException).until(lambda x: x.find_element_by_class_name("article-detail").is_displayed())
            time.sleep(1)
            current_page_url = browser.current_url
            print("当前页面的url是：", current_page_url)
            title = browser.find_element(by=By.XPATH, value="//div[@class='head-content']/div[contains(@class,'article-detail_tit')]").text  # 点击登录按钮
            print("当前文章的标题是：", title)
            content = browser.find_element(by=By.ID, value="detailContent").text
            print("获取content中...")
            '''
            将正文保存到本地文件
            '''
            if os.path.exists(title + '.txt'):
                print("文章已存在...")
                browser.close()
            else:
                file_handle = open(title + '.txt', mode='w')
                file_handle.write(content)
                file_handle.close()
                print("文章保存完毕...")
                browser.close()  # 关闭该窗口
    # article = browser.find_element(by=By.XPATH, value="//*[@id=\"__layout\"]/div/div[2]/div[2]/div[2]/ul/li[1]/div/h2/a")
    '''
    accept()方法是单击弹出的对话框的确认按钮:driver.switchTo().alert().accept();
    dismiss()方法实现单击弹出对话框的取消按钮:driver.switchTo().alert().dismiss();
    '''
    print("5s后关闭浏览器")
    time.sleep(5)
    browser.quit()


if __name__ == '__main__':
    law_search()