from wordcloud import WordCloud
import numpy as np

# 文字雲

def wc_1(dataframe):
    text = dataframe
    x, y = np.ogrid[:300, :300]
    mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
    mask = 255 * mask.astype(int)
    font = 'app_news_summary/static/fonts/NotoSansTC-Regular.otf'
    wc = WordCloud(background_color='white',
                   font_path=font, mask=mask).generate(text)
    return wc