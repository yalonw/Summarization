from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 文字雲試做
def wc_1(dataframe):
	font = 'summarization/static/fonts/kaiu.ttf'
	text = dataframe['jieba']
	cloud = WordCloud(background_color='white', font_path=font).generate(text)
	# return cloud
	# wc_output = cloud.to_file('static/images/wordcloud.png')
	plt.imshow(cloud)
	plt.axis("off")
	plt.show()


''' 測試區 '''
if __name__ == '__main__':
	import crawl_news
	import lda_topic_model
	from drawable_summary import Drawable_summary
	import matplotlib.pyplot as plt
	

	keyword = '森林'
	num_of_news = 2
	df = crawl_news.Crawl_BBC(keyword, num_of_news).make_dataframe()  # 爬文章

	lda = lda_topic_model.LDAclass(df, chinese_only=True)                             # 只做 jieba 分詞
	lda.lda_class(n_topics=3, max_iter=100, evaluate_every=10, verbose=1)  # 做 LDA
	print('='*30, '\n', lda.n_topics_dict())
	df = lda.dataframe

	summary = Drawable_summary(df,'text_rank', 50, '3', keyword).make_summary()
	print('='*30)
	wc_1(summary)