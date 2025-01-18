from DrissionPage import ChromiumOptions, ChromiumPage

co = ChromiumOptions()
page = ChromiumPage()
page.get("https://www.qidian.com/")
a = input()
co.save("config.ini")