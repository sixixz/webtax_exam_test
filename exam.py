# coding=utf-8
import json
import base64
import random
import cv2
from selenium import webdriver
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mysql import webtaxMysql


def get_distance(bg, tp):
    """
    比对图片，获取移动距离

    :param bg: 背景图片
    :param tp: 缺口图片
    :return: 缺口的X坐标
    """
    bg_img = cv2.imread(bg)
    bg_img = cv2.Canny(bg_img, 310, 155)
    tp_pic = cv2.imread(tp)
    tp_pic = cv2.Canny(tp_pic, 47, 155)
    bg_img_gray = cv2.cvtColor(bg_img, cv2.COLOR_GRAY2RGB)  # 对图片灰度化处理
    cv2.imwrite('full_gray.png', bg_img_gray)
    tp_pic_gray = cv2.cvtColor(tp_pic, cv2.COLOR_GRAY2RGB)  # 对图片灰度化处理
    cv2.imwrite('gap_gray.png', tp_pic_gray)
    res = cv2.matchTemplate(bg_img_gray, tp_pic_gray, cv2.TM_CCOEFF_NORMED)
    # # 绘制方框
    # th, tw = tp_pic.shape[:2]
    # tl = max_loc  # 左上角点的坐标
    # br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
    # cv2.rectangle(bg_img, tl, br, (255, 255, 255), 2)  # 绘制矩形
    cv2.imwrite("out.png", bg_img)  # 保存在本地
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
    tl = max_loc  # 左上角点的坐标
    distance = tl[0] * 400 / 310  # 浏览器图片与本地图片等比例缩放
    # 返回缺口的X坐标
    return distance


class Exam(object):
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        # 实例化浏览器
        self.browser = webdriver.Chrome()
        # 最大化浏览器
        self.browser.maximize_window()
        # 请求官网首页
        self.browser.get('https://test.webtax.com.cn/competition')

    def __del__(self):
        self.browser.quit()
        print('浏览器已关闭...')

    def save_pic(self, data_url, name):
        # noinspection PyBroadException
        try:
            header, encoded = data_url.split(",", 1)
            data = base64.b64decode(encoded)
            pic_name = name + '.png'
            with open(pic_name, "wb") as f:
                f.write(data)
        except:
            self.loop_check()

    def move(self, distance):
        """
        移动滑块

        :param distance: 移动距离
        """
        # 定位滑块位置
        btn = self.browser.find_elements(by=By.CLASS_NAME, value='verify-move-block')[-1]
        ActionChains(self.browser).drag_and_drop_by_offset(btn, distance, 0).perform()

    def loop_check(self):
        """
        拼图验证

        :return: 1 拼图验证成功
        """
        # 检查拼图验证弹窗是否关闭
        bg = self.browser.find_elements(by=By.XPATH, value='//*[@class="verify-img-panel"]/img')[-1].get_attribute(
            'src')
        block_pic = self.browser.find_elements(by=By.XPATH, value='//*[@class="verify-sub-block"]/img')[
            -1].get_attribute('src')
        # 保存图片
        self.save_pic(bg, "full")
        self.save_pic(block_pic, "gap")
        # 获取移动距离
        distance = get_distance("full.png", "gap.png")
        print('滑块移动距离：', distance)
        # 移动滑块
        self.move(distance)
        time.sleep(2)
        # check = is_element_exist_contain("div", "请完成安全验证")
        # # 弹窗存在，则循环
        # if check:
        #     loop_check()
        print('验证成功')
        # get_cookie()
        cookie = {}
        for i in self.browser.get_cookies():
            cookie[i["name"]] = i["value"]
        with open("cookies.txt", "w") as f:
            f.write(json.dumps(cookie))
        return 1

    def find_element(self, content):
        """
        根据文本信息精准匹配定位元素

        :param content: 文本信息
        :return: 定位元素
        """
        value = "//*[text()='{}']".format(content)
        # print(value)
        element = self.browser.find_element(by=By.XPATH, value=value)
        return element

    def is_element_exist(self, content):
        """
        检查元素是否存在

        :param content: 文本信息
        :return: 文本信息是否存在
        """
        flag = 1
        # noinspection PyBroadException
        try:
            self.find_element(content)
            print("已定位到\"{}\"".format(content))
            return flag
        except:
            flag = 0
            print("未定位到\"{}\"".format(content))
            return flag

    def find_element_contain(self, tag, content):
        """
        根据文本信息模糊匹配定位元素

        :param tag: 元素标签
        :param content: 文本信息
        :return: 定位元素
        """
        value = "//{}[contains(text(),'{}')]".format(tag, content)
        # print(value)
        element = self.browser.find_element(by=By.XPATH, value=value.format(tag, content))
        return element

    def is_element_exist_contain(self, tag, content):
        """
        检查元素是否存在

        :param tag: 元素标签
        :param content: 文本信息
        :return: 文本信息是否存在
        """
        flag = 1
        # noinspection PyBroadException
        try:
            self.find_element_contain(tag, content)
            print("已定位到\"{}\"".format(content))
            return flag
        except:
            flag = 0
            print("未定位到\"{}\"".format(content))
            return flag

    def login_vcode(self, phone, vcode):
        """
        手机+验证码登录

        :param phone: 手机号
        :param vcode: 验证码
        """
        is_login = self.is_element_exist("登录/注册")
        if is_login:
            print('用户未登录')
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "login-btn"))).click()  # 点击登录按钮
            time.sleep(1)
            self.browser.find_element(by=By.CSS_SELECTOR, value="input[type='text'][placeholder='请输入您的手机号']").send_keys(
                phone)  # 输入手机号
            time.sleep(1)
            self.browser.find_element(by=By.CLASS_NAME, value="getcode-btn").click()  # 点击获取验证码
            time.sleep(2)
            self.loop_check()  # 图形验证
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='text'][placeholder='请输入验证码']"))).send_keys(vcode)  # 输入验证码
            # if check:  # 验证成功
            #     self.browser.find_element(by=By.CSS_SELECTOR, value="input[type='text'][placeholder='请输入验证码']").send_keys(vcode)  # 输入验证码
            time.sleep(1)
            self.browser.find_elements(by=By.XPATH, value="//*[@class=\"login\"]//button")[-1].click()  # 点击登录按钮
            time.sleep(2)
            print('登录成功')
        else:
            print('用户已登录')

    def login_pw(self, phone, pw):
        """
        :param phone: 手机号
        :param pw: 密码
        """
        is_login = self.is_element_exist("登录/注册")
        if is_login:
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "login-btn"))).click()  # 点击登录按钮
            time.sleep(1)
            self.browser.find_element(by=By.CLASS_NAME, value="change-login").click()  # 切换至密码登录
            time.sleep(1)
            self.browser.find_element(by=By.CSS_SELECTOR, value="input[type='text'][placeholder='请输入您的手机号']").send_keys(
                phone)  # 输入手机号
            time.sleep(1)
            self.browser.find_element(by=By.CSS_SELECTOR,
                                      value="input[type='password'][placeholder='请输入密码']").send_keys(pw)  # 输入密码
            time.sleep(1)
            self.browser.find_element(by=By.XPATH, value="//*[@class=\"login\"]//button").click()  # 点击登录按钮
            time.sleep(2)
            self.loop_check()  # 图形验证
            print('登录成功')
            time.sleep(2)
        else:
            print('用户已登录')

    def exam_apply(self):
        # 选择职业
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@class=\"el-form apply-contain mt-20\"]/div[2]//input"))).click()
        time.sleep(2)
        positions = ["政府机构人员", "事务所人员", "企业人员", "高校老师", "学生", "自由职业者", "其他"]
        position = random.choice(positions)  # 随机点选一个
        self.find_element(position).click()
        # 选择城市
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@class=\"el-form apply-contain mt-20\"]/div[3]//input"))).click()
        time.sleep(1)
        self.find_element("河北省").click()
        time.sleep(1)
        self.find_element("唐山市").click()
        time.sleep(1)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@class=\"el-form apply-contain mt-20\"]/div[3]//input"))).send_keys('359389227@qq.com')
        time.sleep(1)
        self.find_element("提交").click()
        time.sleep(2)
        self.find_element("我知道了").click()
        print("报名成功...")

    def get_right_option(self):
        question = self.browser.find_element(by=By.CLASS_NAME, value='qa-title-content').text[4:]
        print(question)
        sql = 'SELECT option_content FROM wt_exam_question_option WHERE question_id = (SELECT id FROM wt_exam_question WHERE question LIKE \'{}\' AND is_delete = 0 AND is_enable = 1 AND review = 1) AND is_right = 1'.format(
            question)
        sq.execute_select(sql)
        options = sq.fetchall()
        print(options)
        return options

    def exam_answer(self):
        """
        答题
        """
        is_next = 1
        while is_next:
            # options = self.browser.find_elements(by=By.CLASS_NAME, value="show-right-select-text")  # 获取正确选项
            options = self.get_right_option()
            if options is None:
                print('查询失败，默认选A')
                self.find_element_contain("span", 'A.').click()
            else:
                for eachOption in options:
                    # find_element_contain("span", eachOption)
                    self.find_element_contain("span", eachOption[0]).click()
                    time.sleep(1)
            time.sleep(1)
            self.find_element('提 交').click()
            time.sleep(2)
            is_next = self.is_element_exist('下一题')
            if is_next:
                self.find_element('下一题').click()
            else:
                print('答题结束')
                break
            time.sleep(2)
        is_wait = self.is_element_exist_contain('span', '成功邀请好友立刻解锁答题')
        if is_wait:
            self.find_element('我知道了').click()
        is_pass = self.is_element_exist('领取奖励')
        if is_pass:
            print('闯关成功')
            time.sleep(2)
            self.find_element('领取奖励').click()
            self.exam_award()
        else:
            print('闯关失败')
            time.sleep(2)
            self.find_element('返回首页').click()

    def exam_award(self):
        award_type = ['现金红包', '答题道具']
        select_type = random.choice(award_type)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "award-item-box")))
        self.find_element(select_type).click()
        self.find_element('领取').click()
        time.sleep(2)
        is_again = self.is_element_exist_contain('span', '再次挑战')
        if is_again == 1:
            self.find_element_contain('span', '再次挑战').click()
            time.sleep(2)
            # 图形验证
            self.loop_check()
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "content-box")))
            self.exam_answer()
        else:
            time.sleep(2)
            self.find_element('回到首页').click()

    def exam(self):
        try:
            # 获取剩余闯关次数

            element = self.browser.find_element(by=By.XPATH, value="//*[@class=\"position-item position-absolute\"]/button")
            button_value = element.text
            print(button_value)
            if button_value == "开始答题":
                count = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
                    (By.XPATH, "//*[@class=\"position-item position-absolute\"]//font"))).text
                count = int(count)
                if count:
                    print('剩余答题次数：{}'.format(count))
                    element.click()
                    time.sleep(2)
                    # 图形验证
                    self.loop_check()
                    WebDriverWait(self.browser, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "content-box")))
                    self.exam_answer()
                else:
                    print('次数已用尽')
            elif button_value == "继续挑战":
                element.click()
                time.sleep(2)
                # 图形验证a
                self.loop_check()
                WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "content-box")))
                self.exam_answer()
            elif button_value == "立即报名":
                element.click()
                time.sleep(1)
                self.exam_apply()
                time.sleep(2)
                self.exam()
            elif button_value == "领奖入口":
                element.click()
                time.sleep(2)
                self.browser.quit()
            else:
                print("未开始/已通关/已结束/冷却中...")
                time.sleep(2)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    exam_test = Exam()
    exam_test.login_vcode("19900000041", "888888")
    sq = webtaxMysql()
    exam_test.exam()
