import logging
from datetime import datetime
from typing import List
import time

import requests
from bs4 import BeautifulSoup
from lxml import etree
from faker import Faker
from tqdm import tqdm

from models.News import NewNews
from utils.db import update_new_news, check_url_exist
from utils.utils import get_news_info
from utils.page_navigator import PageNavigator

faker = Faker()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SpiderEnorth:
    def __init__(self):
        self.page_list: List[str] = list()

    def get_page_navigator(self, page: int = 20):
        logger.info(f"开始获取前{page}页的导航地址")
        navigator = PageNavigator()
        self.page_list.append(navigator.first_url)
        for i in tqdm(range(page - 1), desc="获取页面导航"):
            next_page_url = navigator.get_next_page_url(2)
            self.page_list.append(next_page_url)
        logger.info(f"成功获取{len(self.page_list)}个页面地址")

    @staticmethod
    def get_news_content(url):
        headers = {'User-Agent': faker.user_agent()}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.content.decode('gbk', errors='ignore')

        html = etree.HTML(content)
        soup = BeautifulSoup(content, 'html.parser')

        for element in soup(["script", "style"]):
            element.decompose()

        editor_time_elements = html.xpath('//div[@id="title"]/div[2]/p/span[4]/text()')
        if not editor_time_elements:
            raise Exception("无法获取编辑时间")
        editor_time = editor_time_elements[0]

        content_div = soup.find('div', class_='content')
        if content_div:
            paragraphs = content_div.find_all('p')
            text = '\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
        else:
            text = "无法获取正文"

        return editor_time, text

    def get_page_content(self):
        logger.info("开始获取网页内容")
        for page in tqdm(self.page_list, desc="处理页面"):
            headers = {'User-Agent': faker.user_agent()}
            response = requests.get(page, headers=headers)
            response.raise_for_status()
            html = etree.HTML(response.content.decode('gbk'))
            news_list = html.xpath('//td[@class="zi14"]/table/tr')
            logger.debug(f"当前地址：{page}成功获取{len(news_list)}条新闻")
            pre_new_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")# 今天
            for news in news_list:
                href = news.xpath('./td[2]/a/@href')[0]
                title = news.xpath('./td[2]/a/text()')[0]

                if check_url_exist(href):
                    logger.debug(f"发现已存在的URL {href}, 跳过")
                    continue
                summary = None
                try:
                    editor_time, text = self.get_news_content(href)
                    try:
                        ai_result = get_news_info(text)
                    except:
                        ai_result = None
                    if ai_result:
                        logger.debug(f"AI分析结果：{ai_result}")
                        summary = ai_result.get('summary', None)
                        tags = ','.join(ai_result.get('tags', []))
                        isFinanceOrEstate = ai_result.get('isFinanceOrEstate', False)
                    else:
                        logger.debug(f"无法获取AI分析结果，使用默认分析结果")
                        tags = None
                        isFinanceOrEstate = False
                    pre_new_date = editor_time
                except:
                    editor_time = pre_new_date
                    summary = "疑似外部地址，无法获取正文"
                    tags = None
                    isFinanceOrEstate = False

                news = NewNews()
                news.url = href
                news.title = title.strip()
                news.summary = summary
                news.tags = tags
                news.isFinanceOrEstate = isFinanceOrEstate
                news.editor_time = datetime.strptime(editor_time, '%Y-%m-%d %H:%M:%S')

                update_response = update_new_news(news)
                logger.debug(f"更新数据库结果：{update_response}")

            # 添加小延迟，避免请求过于频繁
            time.sleep(0.5)


if __name__ == '__main__':
    spider = SpiderEnorth()
    spider.get_page_navigator(1)
    spider.get_page_content()
