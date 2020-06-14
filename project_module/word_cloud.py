from wordcloud import WordCloud
import numpy as np
# 文字雲

def wc_1(text):
	
	stopwords='app_news_summary/static/stop_words.txt'
	diction = text
	x, y = np.ogrid[:300, :300]
	mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
	mask = 255 * mask.astype(int)
	font = 'app_news_summary/static/fonts/NotoSansTC-Regular.otf'
	
	wc = WordCloud(background_color='black',
				   font_path=font,
				   mask=mask,
				   stopwords=stopwords
				   ).generate(diction)
	return wc