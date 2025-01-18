import random
import time
from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from database_helper import DatabaseHelper


# 解析 URL 获取章节 ID
def get_page_id(webpage):
    parsed_url = urlparse(webpage.url)
    path_parts = parsed_url.path.split('/')
    chapter_id = path_parts[-2]  # 获取倒数第二部分作为章节 ID
    novel_id = path_parts[-3]
    return chapter_id, novel_id

# 获取“下一章”按钮
def get_next_button(webpage):
    buttons = webpage.ele(".nav-btn-group")
    next_button = buttons.ele("下一章")
    return next_button

# 获取章节标题和内容
def get_title_and_content(webpage):
    html = webpage.html
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.body

    # 删除不需要的元素
    for img in soup.find_all('img'):
        img.decompose()
    for review in soup.find_all(class_="review-count"):
        review.decompose()
    for button in soup.find_all('button'):
        button.decompose()

    # 获取标题
    title = None
    h1_elements = soup.find_all('h1', class_=re.compile(r'^title'))
    if h1_elements:
        title = h1_elements[0].text.strip()  # 获取第一个匹配的 h1 标签标题

    # 获取章节内容
    contents = []
    main_element = soup.find('main')
    if main_element:
        content_text_elements = main_element.find_all(class_='content-text')
        for content in content_text_elements:
            contents.append(content.get_text(strip=True))

    # 用换行符分隔内容
    content_text = "\n".join(contents)
    return title, content_text

# 随机等待时间：2-3分钟之间的随机值（以秒为单位）
def wait_random_time():
    wait_time = random.randint(20, 40)  # 2到3分钟之间的随机秒数
    print(f"等待 {wait_time} 秒...")
    time.sleep(wait_time)

# 爬取并保存章节
def read_page(webpage):
    chapter_id, novel_id = get_page_id(webpage=webpage)
    title, content_text = get_title_and_content(webpage=webpage)
    next_button = get_next_button(webpage=webpage)
    return (novel_id, chapter_id, title, content_text, next_button)

def get_to_certain_page():
    # 初始化 Chromium 配置和页面对象
    co = ChromiumOptions(ini_path=r'config.ini')
    page = ChromiumPage(addr_or_opts=co)
    page.get("https://www.qidian.com/")
    return page