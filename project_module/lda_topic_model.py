import jieba
import jieba.analyse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import re

class KeywordExtraction():
    '''提取關鍵字'''
    @staticmethod
    def word_cut_list(content):
        '''jieba 分詞，包含標點符號'''
        return  ' '.join(jieba.cut(content))

    @staticmethod
    def keyword_tf(content, num_of_keyword=50, withweight=False):
        '''提取關鍵字：TF-IDF (考慮詞頻)'''
        return jieba.analyse.extract_tags(content,
                                          topK=num_of_keyword,
                                          withWeight=withweight,
                                          allowPOS=())
    @staticmethod
    def keyword_tr(content, num_of_keyword=50, withweight=False):
        '''提取關鍵字：TextRank (考慮文意)'''
        return jieba.analyse.textrank(content,
                                      topK=num_of_keyword,
                                      withWeight=withweight,
                                      allowPOS=('ns', 'n', 'vn', 'v'))
    @staticmethod
    def keyword_mix(content, num_of_keyword=50, withweight=False):
        '''提取關鍵字：mix = TF-IDF + TextRank'''
        keyword_tf = jieba.analyse.extract_tags(content,
                                                topK=num_of_keyword,
                                                withWeight=True,
                                                allowPOS=())
        keyword_tr = jieba.analyse.textrank(content,
                                            topK=num_of_keyword,
                                            withWeight=True,
                                            allowPOS=('ns', 'n', 'vn', 'v'))
        mix = {x[0]:x[1] for x in keyword_tf} 
        for word in keyword_tr:
            if word[0] in mix.keys():
                mix[word[0]] += word[1]
            else:
                mix[word[0]] = word[1]

        if withweight == False:
            return sorted(mix.keys(), key=mix.get, reverse=True)
        else:
            return sorted(mix.items(), key=lambda x:x[1], reverse=True)

    @staticmethod
    def stop_words_dict(stop_words_file):
        ''' 
        讀取 "停用詞" 字典（*.txt），回傳 list()
            注意：停用詞.txt 中，一個單詞一行
        '''
        with open(stop_words_file, encoding = 'utf-8') as f:
            stopwords = f.readlines()            
        return [w.replace('\n', '').replace(' ', '') for w in stopwords] 


class LDAclass(KeywordExtraction):
    '''
    LDA 主題模型
        1. 單獨呼叫 LDAclass()，僅做 jieba 分詞(含標點符號)
        2. 呼叫 LDAclass().lda_class，才會進行 LDA 主題模型的分類訓練
    '''
    def __init__(self, dataframe, word_cut_algorithm=None, chinese_only=False, stop_words=None):
        self.dataframe = dataframe
        self.word_cut_algorithm = word_cut_algorithm     # 選擇文本分詞方式
        self.stop_words = stop_words                     # 是否使用停用詞字典
        self.chinese_only = chinese_only                 # 是否只擷取中日韓文字(不含英文、數字、標點符號)

        self.dataframe['jieba'] = self.dataframe['content'].apply(self.word_cut_list)

    def content_preprocess(self, content, num_of_keyword=50):
        '''
        文本處理函式，回傳 str()
            1. 是否正則轉換 chinese_only
                只保留中日韓非符號字符(不含英文、數字、標點符號)
            2. 選擇文本分詞方式 word_cut_algorithm
                (1) 原文載入
                (2) TF-IDF
                (3) TextRank
                (4) mix = TF-IDF + TextRank
            3. 是否有停用字 stop_words
        '''
        # 1. 是否正則轉換：[^\u4e00-\u9fa5]
        if self.chinese_only == True:
            rule = re.compile(r"[^\u4e00-\u9fa5]")        
            content_1 = rule.sub('', content)
        else:
            content_1 = content

        # 2. 選擇文本分詞方式
        if self.word_cut_algorithm == None:
            content_2 = list(jieba.cut(content_1))
        elif self.word_cut_algorithm == 'tf_idf':
            content_2 = self.keyword_tf(content_1, num_of_keyword)
        elif self.word_cut_algorithm == 'text_rank':
            content_2 = self.keyword_tr(content_1, num_of_keyword)
        elif self.word_cut_algorithm == 'mix':
            content_2 = self.keyword_mix(content_1, num_of_keyword)

        # 3. 是否有停用字
        if self.stop_words != None:
            stopwords = self.stop_words_dict(self.stop_words)
            content_3 = ' '.join([word for word in content_2 if word.strip() not in stopwords])
        else:
            content_3 = ' '.join(content_2)

        return content_3

    def content_cutted(self):
        '''對文本 dataframe['content'] 進行處理與分詞'''
        return self.dataframe['content'].apply(self.content_preprocess)

    def lda_class(self, n_topics=5, max_iter=50, learning_method='batch', 
                  learning_offset=2, evaluate_every=-1, verbose=0):
        '''
        LDA 主題模型的分類訓練
            1. CountVectorizer：將"文本列表"轉換為"詞頻矩陣 sparse matrix"
            2. LatentDirichletAllocation："LDA 主题模型" 訓練
                self.n_topics     # 區分主題數量                                            -> 會影響 perplexity 大小
                max_iter          # lda fit 迭代次數 (max_iter=50 為模型最大迭代次數)
                learning_method   # lda 訓練方法：'batch'(慢) 或 'online'(快)
                learning_offset   # 調整模型準確度，需配合 learning_method='online' 使用
                evaluate_every    # 設定 lda 每幾次 iter 顯示一次 perplexity，請配合 verbose  -> 數量影響模型訓練速度

                perplexity        # (主題數量, 主題區分loss率)                               -> 太小容易過擬合
                problist          # 主題預測機率
         '''
        self.n_topics = n_topics

        # 1. 將"文本列表"轉換為"詞頻矩陣 sparse matrix"
        #    是否正則轉換：[\u4e00-\u9fff]{2,6} -> [配對中日韓認同表意文字區]{配對長度2~6個字節}
        if self.chinese_only == True:             
            self.tf_vectorizer = CountVectorizer(token_pattern='[\u4e00-\u9fff]{2,6}',
                                                 max_features=500)                                            
        else:
            self.tf_vectorizer = CountVectorizer(max_features=500)

        tf = self.tf_vectorizer.fit_transform(self.content_cutted())        

        # 2. LDA 主题模型訓練
        self.lda_model = LatentDirichletAllocation(n_components=n_topics,
                                                   max_iter=max_iter,
                                                   learning_method=learning_method,
                                                   learning_offset=learning_offset,
                                                   evaluate_every=evaluate_every,
                                                   verbose=verbose,
                                                   random_state=None)
        self.lda_model.fit(tf)

        self.perplexity = (self.n_topics, self.lda_model.perplexity(tf))   # 主題區分loss率 -> 太小容易過擬合
        self.problist = self.lda_model.transform(tf)                       # 主題預測機率
        self.dataframe['topic'] = np.argmax(self.problist, axis=1)

    def lda_class_test(self, dataframe):
        '''
        預測文本主題，回傳 array() -> 2 dim
            注意：文本之 dataframe 需有 'content' 列
        '''
        content_cutted = dataframe['content'].apply(self.content_preprocess)
        tf = self.tf_vectorizer.transform(content_cutted)
        problist = self.lda_model.transform(tf)
        return np.argmax(problist, axis=1)

    def n_topics_dict(self, n_top_words=10):
        '''
        各主題分類中權重最高的詞，回傳 dict()
            n_top_words：設定每個主題回傳詞的個數        
        '''
        feature_names = self.tf_vectorizer.get_feature_names()
        compoments = self.lda_model.components_

        topics_dict = {}
        for i in range(self.n_topics):
            topic = [feature_names[i] for i in compoments[i].argsort()[:-(n_top_words)-1:-1]]
            topics_dict["topic" + str(i+1)] = topic

        return topics_dict


''' 測試區 '''
if __name__ == '__main__':
    import crawl_news

    keyword = '肺炎'
    num_of_news = 20
    df_news = crawl_news.Crawl_BBC(keyword, num_of_news).make_dataframe()

    lda = LDAclass(df_news, chinese_only=True)                             # 只做 jieba 分詞
    lda.lda_class(n_topics=3, max_iter=100, evaluate_every=10, verbose=1)  # 做 LDA
    print('='*30)
    print('(主題數量, 主題區分loss率):', lda.perplexity)
    print('='*30)
    print(lda.problist)
    print('='*30)
    print(lda.dataframe)  # 呼叫這個會印出 dataframe
    print('='*30)
    print(lda.n_topics_dict())