''' version: v3 '''

from selenium.webdriver import Chrome
import pandas as pd
import time

class Crawler_BBC():

    keyword = input("輸入關鍵字:")
    total = int(input("輸入總共要幾筆新聞:"))
    title_list = []
    date_list = []
    content_list = []
    url_list = []
    df = pd.DataFrame(columns=["title", "content", "time", "url"])
    driver = Chrome("./chromedriver")
    page = 1    #換頁
    count = 0   #存入筆數

    while True:
        driver.get("https://www.bbc.com/zhongwen/trad/search?q=" + keyword + "&start=" + str(page))
        news = driver.find_elements_by_class_name("hard-news-unit__headline-link")

        #取得用來篩選是否LIVE新聞的網址
        urls = []
        for link in driver.find_elements_by_xpath("//h3[@class='hard-news-unit__headline']/a"):
            print(link.get_attribute('href'))
            url = link.get_attribute('href')
            urls.append(url)

        if len(news) == 0:
            print("沒有新聞了")
            break

        for i in range(0, len(news)):

            # 音頻跟影片沒有內容只有摘要，不取
            if news[i].text.find("視頻") != -1 or news[i].text.find("音頻") != -1:
                continue
            # live新聞也沒有內容不取
            elif urls[i].find("live") != -1:
                continue
            else:
                news[i].click()
            time.sleep(3)

            #直播報導沒有重點也不取
            print(driver.current_url.find("live"))
            if driver.current_url.find("live") == -1:
                url_list.append(driver.current_url)
            else:
                continue
            # 取得URL

            # 取得標題
            title = driver.find_element_by_class_name("story-body__h1")
            title_list.append(title.text)

            # 日期時間
            date = driver.find_element_by_css_selector("div[class=\"date date--v2\"]")
            date_list.append(date.text)

            # 新聞內容
            # 把取得的LIST轉成字串在append進去
            content = driver.find_elements_by_xpath("//div[@class='story-body__inner']/p")
            inner_list = []
            for c in content:
                inner_list.append(c.text)
            inner = "".join(inner_list)
            content_list.append(inner)

            # series存入DATAFRAME
            s = pd.Series([title_list[count], content_list[count], date_list[count], url_list[count]],
                          index=["title", "content", "time", "url"])
            df = df.append(s, ignore_index=True)
            print("存入第 " + str(count+1) + " 筆新聞")
            if count + 1 >= total:
                break
            else:
                driver.get("https://www.bbc.com/zhongwen/trad/search?q=" + keyword + "&start=" + str(page))
                news = driver.find_elements_by_class_name("hard-news-unit__headline-link")
                count = count + 1

        if count + 1 >= total:
            break
        else :
            #page換頁後，把LIST_news清空
            page = page + 10
            news = []
    driver.close()
    driver.quit()

    print(df)