import jieba
import jieba.analyse
import numpy as np


class Drawable_summary():
    '''
    抽取式摘要
        1. dataframe　　　： df_news -> df_lda -> summary 
        2. rank_algorithm : 提取關鍵字的演算法，如 'tf_idf', 'text_rank', 'mix' 
        3. num_of_keyword : 提取關鍵字的數量
        4. sum_length　　 ： 抽取文本長度的門檻值，如 'avg', 'Q1', 'Q2', 'Q3'，或填入 '數字'        
        5. remove_word　　： 移除詞，因無法為讀者提供更多訊息，故直接移除；如 '搜尋的關鍵字'
    '''
    def __init__(self, dataframe, rank_algorithm, num_of_keyword, sum_length, remove_word):
        self.dataframe = dataframe
        self.rank_algorithm = rank_algorithm
        self.num_of_keyword = num_of_keyword
        self.sum_length = sum_length
        self.remove_word = [remove_word]
        
    def choose_algorithm(self, content):
        '''
        選擇提取關鍵字的演算法：
            1. tf_idf
            2. text_rank
            3. mix : 基於前兩種演算法分數相加
        '''
        if self.rank_algorithm == 'tf_idf':
            keyword_tf = jieba.analyse.extract_tags(content,
                                                    topK=self.num_of_keyword,
                                                    withWeight=True,
                                                    allowPOS=())
            self.keyword = keyword_tf

        elif self.rank_algorithm == 'text_rank':
            keyword_tr = jieba.analyse.textrank(content,
                                                topK=self.num_of_keyword,
                                                withWeight=True,
                                                allowPOS=('ns', 'n', 'vn', 'v'))
            self.keyword = keyword_tr
            
        elif self.rank_algorithm == 'mix':
            keyword_tf = jieba.analyse.extract_tags(content,
                                                    topK=self.num_of_keyword,
                                                    withWeight=True,
                                                    allowPOS=())
            keyword_tr = jieba.analyse.textrank(content,
                                                topK=self.num_of_keyword,
                                                withWeight=True,
                                                allowPOS=('ns', 'n', 'vn', 'v'))

            mix_keyword = {x[0]:x[1] for x in keyword_tf} 
            for word in keyword_tr:
                if word[0] in mix_keyword.keys():
                    mix_keyword[word[0]] += word[1]
                else:
                    mix_keyword[word[0]] = word[1]
        
            mix_keyword = [(x,mix_keyword[x]) for x in mix_keyword]
            self.keyword = mix_keyword
        
        return self.keyword
           
    def give_score(self, content_after_jieba):
        '''
        給每個句子分數
            content_after_jieba : jieba 後的 data 需要包含標點符號
        ''' 

        def none_empty(x): 
            '''避免出現空值的狀況'''
            return x.strip()

        process_data = [sent.split(' ') for sent in content_after_jieba.split('。')]
        process_data = [list(filter(none_empty, x)) for x in process_data if len(list(filter(none_empty, x))) > 0]
        
        self.sent_score = []
        for sent in process_data:
            score = 0
            for word in self.keyword:
                if (word[0] in sent) & (word[0] not in self.remove_word):   # 考慮停用詞
                    score += word[1]
            self.sent_score.append(tuple([''.join(sent),score]))

        return self.sent_score
        
    def draw_length(self):
        '''
        選擇抽取文本長度的門檻值，並抽取文本：
            1.  數字　　　　　：以 "指定句數的分數" 為門檻值；若 "指定句數" 超過則文本句數，則萃取全文
            2. 'avg'　　　　　: 以 "平均分數" 為門檻值，萃取分數達標的句子
            3. 'Q1','Q2','Q3': 以 "四分位距" 為門檻值，萃取分數達標的句子
        '''
        score_list = sorted([x[1] for x in self.sent_score], reverse = True)   # 分數由高到低排列 
        average_score = sum(score_list)/len(score_list)                        # 平均分數
        percentile = np.percentile(score_list, [25, 50, 75])                   # 四分位距
        
        # 根據不同狀況決定門檻值
        if self.sum_length.isdigit() and int(self.sum_length)-1 <= len(score_list):
            threshold = score_list[int(self.sum_length)-1]
        elif self.sum_length.isdigit() and int(self.sum_length)-1 > len(score_list):
            threshold = score_list[len(score_list)-1]
        elif self.sum_length == 'avg':
            threshold = average_score
        elif self.sum_length == 'Q1':
            threshold = percentile[0]
        elif self.sum_length == 'Q2':
            threshold = percentile[1]
        elif self.sum_length == 'Q3':
            threshold = percentile[2]

        # 萃取分數達標的句子   
        summary = [x[0] for x in self.sent_score if x[1] >= threshold]
        summary = '。'.join(summary) + '。'
        return summary
    
    def make_summary(self):
        self.dataframe['summary1'] = None
        for i in range(len(self.dataframe)):
            self.choose_algorithm(self.dataframe.loc[i, 'content'])
            self.give_score(self.dataframe.loc[i, 'jieba'])
            self.dataframe.loc[i,'summary1'] = self.draw_length()
        return self.dataframe


''' 測試區 '''
if __name__ == '__main__':
    import crawl_news
    import lda_topic_model

    keyword = '肺炎'
    num_of_news = 3
    df = crawl_news.Crawl_BBC(keyword, num_of_news).make_dataframe()  # 爬文章

    lda = lda_topic_model.LDAclass(df, chinese_only=True)                             # 只做 jieba 分詞
    lda.lda_class(n_topics=3, max_iter=100, evaluate_every=10, verbose=1)  # 做 LDA
    print('='*30, '\n', lda.n_topics_dict())
    df = lda.dataframe

    summary = Drawable_summary(df,'text_rank', 50, '3', keyword).make_summary()
    print(summary.loc[1, 'summary1'])
    print(summary.loc[1, 'content'])
