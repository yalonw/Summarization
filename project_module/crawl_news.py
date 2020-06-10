import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from opencc import OpenCC

class Crawl():
    '''
    input  : keyword, num_of_news   
    output : title, time, content, url 
    '''
    def __init__(self, keyword, num_of_news):
        self.keyword = keyword
        self.num_of_news = num_of_news
        self.title = [] 
        self.time = []
        self.content = []
        self.url = []

    def make_dataframe(self):
        '''return dataframe'''
        return pd.DataFrame({
            'title': self.title, 
            'time': self.time, 
            'content': self.content, 
            'url': self.url            
        })


class Crawl_BBC(Crawl):
    '''分析 BBC 中文網（https://www.bbc.com/zhongwen/trad）'''    
    def __init__(self, keyword, num_of_news):
        super(Crawl_BBC, self).__init__(keyword, num_of_news)
        self.crawler()

    @staticmethod
    def get_content(url):
        '''針對 BBC 的內文進行擷取、清理、組合'''
        response = requests.get(url, headers = {'User-Agent':'Mozilla/5.0'})
        html = BeautifulSoup(response.text, 'html.parser') 
        body = html.find('div', class_='story-body__inner').find_all('p')
        cont = ''.join([p.text.replace('\r', '').replace('\n', '').replace(' ','') for p in body])
        return cont

    def crawler(self):        
        num = 0
        page = 1  # 起始頁1，下一頁+10  
          
        while num != self.num_of_news :
            url = 'https://www.bbc.com/zhongwen/trad/search?q=' + self.keyword + '&start=' + str(page)
            response = requests.get(url, headers = {'User-Agent':'Mozilla/5.0'})
            html = BeautifulSoup(response.text, 'html.parser') 

            # 判斷頁面是否有內容           
            if len(html.find_all('div', class_='hard-news-unit')) == 0 :
                print('=====搜尋頁無內容=====')
                break            
            else: 
                # 擷取新聞標題、發布時間、新聞網址
                for i in html.find_all('div', class_='hard-news-unit'):
                    try:
                        # 過濾視頻和音頻
                        print(i.find('span', class_='icon-new').text)
                    except:
                        self.title.append(i.find('a', class_='hard-news-unit__headline-link').text)
                        self.time.append(i.find('div', class_='date date--v2').text.replace(" ", ""))
                        self.url.append(i.find('a', class_='hard-news-unit__headline-link')['href'])
                        self.content.append(self.get_content(i.find('a', class_='hard-news-unit__headline-link')['href']))
                        num += 1                            
                        print(f'下載篇數：{num}')
                        print("crawl_news.py: num_of_news:", self.num_of_news)

                        if num == self.num_of_news :
                            break
                        else:
                            page += 10  # 下一頁

    def make_dataframe(self):
        '''return dataframe'''
        return super(Crawl_BBC, self).make_dataframe()


class Crawl_NYtimes(Crawl):
    '''分析 The New York Times 中文網（https://cn.nytimes.com/zh-hant/）'''
    def __init__(self, keyword, num_of_news):
        super(Crawl_NYtimes, self).__init__(keyword, num_of_news)
        self.crawler()

    @staticmethod
    def get_content(url):
        '''針對 NYtimes 的內文進行擷取、清理、組合'''
        response = requests.get(url, headers = {'User-Agent':'Mozilla/5.0'})
        html = BeautifulSoup(response.text, 'html.parser') 
        body = html.find_all('div', class_='article-paragraph')

        body_p = []
        for p in body:
            if p.contents[0].name == 'figure' or p.contents[0].name == 'i': p.clear()
            body_p.append(p.text.replace('\r', '').replace('\n', '').replace(' ',''))

        cont = ''.join(body_p).replace('（歡迎點擊此處訂閱NYT簡報，我們將在每個工作日發送最新內容至您的郵箱。）', '')
        return cont    

    def crawler(self):        
        cc = OpenCC('s2tw') # 簡中轉繁中
        num = 0
        page = 0   # 起始頁0，下一頁+100

        while num != self.num_of_news :
            url = 'https://cn.nytimes.com/search/data/'
            params = {'query': self.keyword, 'lang':'', 'dt': 'json', 'from': str(page), 'size': '100'}
            response = requests.get(url, params=params)  
            news = json.loads(response.text)

            # 判斷頁面是否有內容           
            if num > news['total'] :
                print('=====搜尋頁無內容=====')
                break            
            else: 
                # 擷取新聞標題、發布時間、新聞網址
                for i in news['items']:
                    self.title.append(cc.convert(i['headline']))
                    self.time.append(i['publication_date'].replace(" ", ""))
                    self.url.append(i['web_url_with_host'] + 'zh-hant/') # 以繁體中文顯示
                    self.content.append(self.get_content(i['web_url_with_host'] + 'zh-hant/'))  
                    num += 1                            
                    print(f'下載篇數：{num}')
                    if num == self.num_of_news : break
                else:
                    page += 100  # 下一頁

    def make_dataframe(self):
        '''return dataframe'''
        return super(Crawl_NYtimes, self).make_dataframe()

        
''' 測試區 '''
if __name__ == '__main__':
    # news1 = Crawl_BBC('口罩', 3)
    # print('--------- 搜尋完成，印出 DataFrame -----------')
    # print(news1.make_dataframe())

    # df_news = Crawl_BBC('肺炎', 1).make_dataframe()
    # print('--------- 搜尋完成，印出 DataFrame -----------')
    # print(df_news)
    # print(df_news.loc[2, 'content'])

    # s = Crawl_BBC.get_content("https://www.bbc.com/zhongwen/trad/world-52499708")
    # print(s)

    # Debug for num_of_news
    keyword = input("keyword:")
    num_of_news = input("num_of_news: ")
    df_news = Crawl_NYtimes(keyword, int(num_of_news)).make_dataframe()
    print('--------- 搜尋完成，印出 DataFrame -----------')
    print(df_news)