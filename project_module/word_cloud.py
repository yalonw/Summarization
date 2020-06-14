from wordcloud import WordCloud
import numpy as np

def wc_1(text):
    '文字雲'
    diction = text
    x, y = np.ogrid[:500, :500]
    mask = (x-250)**2 + (y-250)** 2 > 240 ** 2
    mask = 255 * mask.astype(int)
    font = 'app_news_summary/static/fonts/NotoSansTC-Regular.otf'

    stopwords = set()
    stopwords_filepath = 'app_news_summary/static/stop_words.txt'
    with open(stopwords_filepath, 'r', encoding='utf8') as f:
        for line in f.readlines():
            stopwords.add(line.strip('\n'))

    wc = WordCloud(background_color='white',
                   font_path=font,
                   mask=mask,
                   stopwords=stopwords
                   ).generate(diction)
    return wc