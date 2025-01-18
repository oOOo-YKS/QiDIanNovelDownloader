import sqlite3
import random
import time
import logging
from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

# 设置日志记录
logging.basicConfig(filename="novel_spider.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 初始化 Chromium 配置和页面对象
co = ChromiumOptions(ini_path=r'config1.ini')
page = ChromiumPage(addr_or_opts=co)

# 创建并连接 SQLite 数据库（如果数据库不存在会自动创建）
conn = sqlite3.connect('novel.db')  # 数据库名为 novel.db
cursor = conn.cursor()

# 创建章节表（如果表不存在）
cursor.execute('''
CREATE TABLE IF NOT EXISTS chapters (
    chapter_id TEXT PRIMARY KEY,
    title TEXT,
    content TEXT
)
''')

# 解析 URL 获取章节 ID
def get_page_id(webpage):
    parsed_url = urlparse(webpage.url)
    path_parts = parsed_url.path.split('/')
    chapter_id = path_parts[-2]  # 获取倒数第二部分作为章节 ID
    return chapter_id

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

# 将章节数据存入数据库
def save_chapter_to_db(chapter_id, title, content):
    cursor.execute('''
    INSERT OR REPLACE INTO chapters (chapter_id, title, content)
    VALUES (?, ?, ?)
    ''', (chapter_id, title, content))  # 直接将内容存储为字符串
    conn.commit()

# 随机等待时间：2-3分钟之间的随机值（以秒为单位）
def wait_random_time():
    wait_time = random.randint(20, 40)  # 2到3分钟之间的随机秒数
    print(f"等待 {wait_time} 秒...")
    time.sleep(wait_time)

# 爬取并保存章节
def crawl_chapter():
    chapter_number = 1
    while True:
        try:
            print(f"正在爬取第 {chapter_number} 章...")
            chapter_id = get_page_id(page)
            title, content = get_title_and_content(page)
            print(f"章节标题: {title}")
            print(f"章节内容: {content}")  # 输出合并后的章节内容

            # 将章节数据存入数据库
            save_chapter_to_db(chapter_id, title, content)

            # 点击下一章按钮（如果存在）
            next_button = get_next_button(page)
            if next_button:
                next_button.click()
                wait_random_time()
                chapter_number += 1
            else:
                print("没有找到“下一章”按钮，爬取结束。")
                break

        except Exception as e:
            logging.error(f"在爬取第 {chapter_number} 章时发生错误: {e}")
            print(f"发生错误，在第 {chapter_number} 章处，跳过此章节。")
            chapter_number += 1
            continue

# 启动爬虫
crawl_chapter()

# 关闭数据库连接
conn.close()
