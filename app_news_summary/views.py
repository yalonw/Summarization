from django.shortcuts import render
from datetime import datetime, timedelta, date
from . import models
from project_module import crawl_news as cn
from project_module import lda_topic_model as ltm
from project_module import extractive_summarization_jieba as esjieba
from project_module import word_cloud
import os
import csv
import pandas as pd


def homepage(request):
    '''首頁'''
    now = datetime.now()
    return render(request, 'index.html', locals())


def summary_esjieba_crawl(request):
    '''透過即時爬蟲取得資料，再進行新聞摘要'''

    # 取得輸入之關鍵字、頁數，開始爬蟲
    keyword = request.POST['keyword']
    # num_of_news = request.POST['num_of_news']
    num_of_news = 11

    print("keyword: ", keyword, "\n""views: num_of_news: ", num_of_news)
    df_news = cn.Crawl_NYtimes(keyword, int(num_of_news)).make_dataframe()

    # 取得爬蟲資料後，做LDA模型分類
    lda = ltm.LDAclass(df_news, chinese_only=True)  # 只做 jieba 分詞
    lda.lda_class(n_topics=3, max_iter=100,
                  evaluate_every=10, verbose=1)  # 做 LDA
    df_lda = lda.dataframe

    # 取得LDA結果，做抽取式摘要
    summary = esjieba.Drawable_summary(
        df_lda, 'text_rank', 25, '2', keyword).make_summary()

    return render(request, 'search_result.html', locals())


def summary_esjieba_database(request):
    '''透過既存資料庫取得資料，再進行新聞摘要'''

    # 取得輸入之關鍵字、日期期間
    keyword = request.POST['keyword']
    search_time = request.POST['search-time']
    date_now = date.today()
    
    def database_filter_date(date_range):
        '''限制搜尋區間'''
        date_end = timedelta(days=date_range)
        D1 = date_now - date_end
        db_filter_day = models.SummaryCrawl.objects.filter(
                            date__gte=D1
                        ).order_by('date')
        print(db_filter_day)
        return db_filter_day

    
    # 依選擇的時間區間縮小搜尋範圍
    if search_time == "30":
        print("="*20+"過去一個月"+"="*20)
        db_filter_day = database_filter_date(30)
    elif search_time == "90":
        print("="*20+"過去三個月"+"="*20)
        db_filter_day = database_filter_date(90)
    elif search_time == "180":
        print("="*20+"過去半年"+"="*20)
        db_filter_day = database_filter_date(90)
    elif search_time == "360":
        print("="*20+"過去一年"+"="*20)
        db_filter_day = database_filter_date(90)
    else:
        print("="*20+"全部紀錄"+"="*20)
        db_filter_day = models.SummaryCrawl.objects.all()


    # 針對 contents 搜尋 keyword
    db_filter_day_keyword = db_filter_day.filter(
                                content__contains=keyword
                            )

    # 將搜尋完結果存成dataframe
    datesize = len(db_filter_day_keyword)
    summary = pd.DataFrame(list(db_filter_day_keyword.values(
                            "title", "content", "date", "url", "summary1"
                           )))

    try:
        # 取得資料庫資料後，做LDA模型分類
		# 只做 jieba 分詞
        lda = ltm.LDAclass(summary, 
                           chinese_only=True,
                           stop_words="app_news_summary/static/stop_words.txt")
		# 做 LDA				   
        lda.lda_class(n_topics=3, 
					  max_iter=100,
                      evaluate_every=10, 
					  verbose=1)					  
        df_lda = lda.dataframe

		# 刪除歷史文字雲
        for i in range(0, 3):
            try:
                os.remove(
                    'app_news_summary/static/images/wordcloud' + str(i) + '.png')
            except OSError as e:
                print(e)
        # 文字雲製作
        wc_list = []
        for i in range(0, 3):
            try:
                df = df_lda.groupby('topic').get_group(i)
                df_1 = df['jieba'].sum()                
                wc = word_cloud.wc_1(df_1)
                wc = wc.to_file('app_news_summary/static/images/wordcloud' + str(i) + '.png')
                wc_list.append(i)
            except KeyError:
                pass
        print(wc_list)

    except KeyError:
        pass

    return render(request, 'search_result.html', locals())
