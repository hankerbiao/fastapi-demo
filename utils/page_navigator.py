import re

import requests
from faker import Faker

faker = Faker()

headers = {
    'User-Agent': faker.user_agent()
}


def get_page_num():
    url = 'http://news.enorth.com.cn/system/count/0017001/009000000000/count_page_list_0017001009000000000.js'
    response = requests.get(url, headers=headers).content.decode('gb2312')
    lines = response.split('\n')
    for line in lines:
        if line.find('var maxpage') != -1:
            all_page = re.search('\d+', line)
            return int(all_page.group())
    raise Exception('没有找到最大页数')


class PageNavigator:
    def __init__(self):
        self.base_url = "http://news.enorth.com.cn/system/more"
        self.base_url2 = "http://news.enorth.com.cn/system/more2"
        self.max_page = get_page_num() + 1  # 原始值4810 + 1
        self.channel_id = "17001009000000000"
        self.first_url = "http://news.enorth.com.cn/tj/wytd/index.shtml"
        self.url_change_flag = 10000
        self.current_page = self.max_page

    def get_next_page_url(self, direction):
        if direction == 1:  # 上一页
            self.current_page += 1
            if self.current_page == self.max_page:
                return self.first_url

            page_num = f"{self.current_page:09d}"
            if self.current_page >= self.url_change_flag:
                return f"{self.base_url2}/{self.channel_id}/{page_num[1:3]}/{page_num[3:5]}/{page_num[5:7]}/{self.channel_id}_{page_num[1:]}.shtml"
            else:
                return f"{self.base_url}/{self.channel_id}/{page_num[3:7]}/{self.channel_id}_{page_num[1:]}.shtml"

        elif direction == 2:  # 下一页
            self.current_page -= 1
            page_num = f"{self.current_page:09d}"
            if self.current_page >= self.url_change_flag:
                return f"{self.base_url2}/{self.channel_id}/{page_num[1:3]}/{page_num[3:5]}/{page_num[5:7]}/{self.channel_id}_{page_num[1:]}.shtml"
            else:
                return f"{self.base_url}/{self.channel_id}/{page_num[3:7]}/{self.channel_id}_{page_num[1:]}.shtml"

    def jump_to_page(self, jump_num):
        if not jump_num.isdigit() or int(jump_num) <= 0 or int(jump_num) >= self.max_page:
            print("输入的页数必须为正整数，且大于0小于等于最大页数")
            return None

        jump_num = int(jump_num)
        if jump_num == 1:
            return self.first_url

        self.current_page = self.max_page - jump_num + 1
        page_num = f"{self.current_page:09d}"

        if self.current_page >= self.url_change_flag:
            return f"{self.base_url2}/{self.channel_id}/{page_num[1:3]}/{page_num[3:5]}/{page_num[5:7]}/{self.channel_id}_{page_num[1:]}.shtml"
        else:
            return f"{self.base_url}/{self.channel_id}/{page_num[3:7]}/{self.channel_id}_{page_num[1:]}.shtml"


if __name__ == '__main__':
    pre_20_page_list = []
    # 使用示例
    navigator = PageNavigator()
    pre_20_page_list.append(navigator.first_url)
    for i in range(19):
        # 获取下一页URL
        next_page_url = navigator.get_next_page_url(2)
        print("下一页URL:", next_page_url)
        pre_20_page_list.append(next_page_url)
    print(pre_20_page_list)
