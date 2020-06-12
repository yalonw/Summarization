from django.shortcuts import render
from datetime import datetime, timedelta, date
from project_module import crawl_news as cn
from project_module import lda_topic_model as ltm
from . import models
import pandas as pd
from project_module import extractive_summarization_jieba as esjieba
import os
from project_module import word_cloud
import csv


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

	# 先針對contains搜尋, 並依時間降序排列
	db_news = models.CrawlNews.objects.filter(
		content__contains=keyword
	).order_by('id')

	# 再依選擇的時間區間再次縮小搜尋範圍
	if search_time == "30":
		print("="*20+"過去一個月"+"="*20)
		date_end = timedelta(days=30)
		D1 = date_now-date_end
		db_news_day = db_news.filter(
			date__gte=D1
		).order_by('id')

	elif search_time == "90":
		print("="*20+"過去三個月"+"="*20)
		date_end = timedelta(days=90)
		D1 = date_now-date_end
		db_news_day = db_news.filter(
			date__gte=D1
		).order_by('id')

	elif search_time == "180":
		print("="*20+"過去半年"+"="*20)
		date_end = timedelta(days=180)
		D1 = date_now-date_end
		db_news_day = db_news.filter(
			date__gte=D1
		).order_by('id')

	elif search_time == "360":
		print("="*20+"過去一年"+"="*20)
		date_end = timedelta(days=360)
		D1 = date_now-date_end
		db_news_day = db_news.filter(
			date__gte=D1
		).order_by('id')
	else:
		print("="*20+"全部紀錄"+"="*20)
		db_news_day = db_news

	# 將搜尋完結果存成dataframe
	datesize = len(db_news_day)
	df_news = pd.DataFrame(list(db_news_day.values(
		"title", "sub_title", "content", "sub_content", "date", "url"
	)))

	try:
		# 取得資料庫資料後，做LDA模型分類
		lda = ltm.LDAclass(df_news, chinese_only=True,
						   stop_words="app_news_summary/static/stop_words.txt")  # 只做 jieba 分詞
		lda.lda_class(n_topics=3, max_iter=100,
					  evaluate_every=10, verbose=1)  # 做 LDA
		df_lda = lda.dataframe

		if keyword == "肺炎" and search_time == "180":
			# 展示範利用，取得已分析好的結果摘要，直接呈現在網頁上
			# 範例: keyword=肺炎, search_time=過去半年
			date_now = date.today()
			date_end = timedelta(days=180)
			D1 = date_now-date_end
			summary_for_database = models.SummaryCrawl.objects.filter(
				content__contains=keyword).filter(
				date__gte=D1).order_by(
				'id')
			summary = pd.DataFrame(list(summary_for_database.values(
				"title", "content", "date", "url", "topic", "jeiba", "summary1"
			)))
		elif keyword == "中國" and search_time == "all":
			# 展示範利用，取得已分析好的結果摘要，直接呈現在網頁上
			# 範例: keyword=中國, search_time=全部紀錄
			summary_for_database = models.SummaryCrawl.objects.filter(
				content__contains=keyword).order_by('id')
			summary = pd.DataFrame(list(summary_for_database.values(
				"title", "content", "date", "url", "topic", "jeiba", "summary1"
			)))
		else:
			# 取得LDA結果，做抽取式摘要
			summary = esjieba.Drawable_summary(
				df_lda, 'text_rank', 25, '2', keyword).make_summary()

		# 輸出csv檔
		# summary.to_csv("app_news_summary/static/summary_output_"+str(keyword)+"_"+str(search_time)+".csv")

		# 無論如何先刪掉之前已產生的文字雲圖片
		for i in range(0, 3):
			try:
				os.remove(
					'app_news_summary/static/images/wordcloud'+str(i)+'.png')
			except OSError as e:
				print(e)

		# 文字雲製作
		wc_list = []
		for i in range(0, 3):
			try:
				df = df_lda.groupby('topic').get_group(i)
				df_1 = df['jieba'].sum()
				wc = word_cloud.wc_1(df_1)
				wc = wc.to_file(
					'app_news_summary/static/images/wordcloud'+str(i)+'.png')
				wc_list.append(i)
			except KeyError:
				pass
		print(wc_list)
	except KeyError:
		pass

	# 無論如何先刪掉之前已產生的文字雲圖片
	# if datesize == 0:
	#     for i in range(0, 3):
	#         try:
	#             os.remove(
	#                 'app_news_summary/static/images/wordcloud'+str(i)+'.png')
	#         except OSError as e:
	#             print(e)

	return render(request, 'search_result.html', locals())
