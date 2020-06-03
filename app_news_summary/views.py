from django.shortcuts import render
from datetime import datetime
from project_module import crawl_news as cn
from project_module import lda_topic_model as ltm
from project_module import extractive_summarization_jieba as esjieba
# from project_module import word_cloud

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
    lda.lda_class(n_topics=3, max_iter=100, evaluate_every=10, verbose=1)  # 做 LDA
    df_lda = lda.dataframe

    # 取得LDA結果，做抽取式摘要
    summary = esjieba.Drawable_summary(df_lda, 'text_rank', 25, '2', keyword).make_summary()

    return render(request, 'search_result.html', locals())


def summary_esjieba_database(request):
    '''透過既存資料庫取得資料，再進行新聞摘要'''

    # 取得輸入之關鍵字、日期期間
    keyword = request.POST['keyword']
    # num_of_news = request.POST['num_of_news']
    num_of_news = 11
    # search-time = request.POST['search-time']

    # TODO: serch_news

    # 取得爬蟲資料後，做LDA模型分類
    lda = ltm.LDAclass(df_news, chinese_only=True)  # 只做 jieba 分詞
    lda.lda_class(n_topics=3, max_iter=100, evaluate_every=10, verbose=1)  # 做 LDA
    df_lda = lda.dataframe

    # 取得LDA結果，做抽取式摘要
    summary = esjieba.Drawable_summary(df_lda, 'text_rank', 25, '2', keyword).make_summary()

    return render(request, 'search_result.html', locals())