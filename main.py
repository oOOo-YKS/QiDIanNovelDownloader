from read_novel import read_page, wait_random_time, get_to_certain_page
from database_helper import DatabaseHelper
from DrissionPage import ChromiumPage, ChromiumOptions

# 在打开的网页中通过点击到要开始下载的章节。
# page = get_to_certain_page()
db = DatabaseHelper()
# # while True:
# #     if len(page.url.split('/')) == 5:
# #         break
# a = input()
co = ChromiumOptions(ini_path=r'config.ini')
page = ChromiumPage(addr_or_opts=co)
while True:
    try:
        result = read_page(page)
        if result[4]:
            db.add_chapter(result[0], result[1], result[2], result[3])
            wait_random_time()
            result[4].click()
        else:
            break
    except:
        break

        