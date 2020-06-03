import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from keras_bert import load_trained_model_from_checkpoint
from keras_bert import Tokenizer
from keras.models import Model
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn import preprocessing
import matplotlib.pyplot as plt

class Bert_extractive():
    '''抽取式摘要  

       作法說明：藉由 BERT 模型產生的句向量，再透過 clustering 找出離質心最近的點，以該點抽取出來的句子，做為抽取式文本摘要。  
       參考論文：Leveraging BERT for Extractive Text Summarization on Lectures ( https://arxiv.org/pdf/1906.04165.pdf )     

       參數說明：   
        1. text：輸入單篇文章
        2. summary_num：設定抽取句數
        3. reduce_dim：預設為2，只有壓縮成二維時才能輸出成圖片
        4. see：是否輸出分群結果的二維圖片，預設為False
        5. seqence_len：原始文章句數之輸入最大長度，預設150
    '''
    def __init__(self, text, summary_num, reduct_dim=2, see=False, seqence_len=150):    
        self.text = text
        self.summary_num = summary_num
        self.seqence_len = seqence_len
        self.see = see
        self.reduct_dim = reduct_dim

    def get_model(self):
        pretrained_path = 'chinese_L-12_H-768_A-12'
        config_path     = os.path.join(pretrained_path, 'bert_config.json')
        checkpoint_path = os.path.join(pretrained_path, 'bert_model.ckpt')
        vocab_path      = os.path.join(pretrained_path, 'vocab.txt')
        
        self.token_dict = {}
        with open(vocab_path, 'r', encoding='utf8') as f:
            for line in f.readlines():
                token = line.strip()
                self.token_dict[token] = len(self.token_dict)

        model = load_trained_model_from_checkpoint(config_path,
                                                   checkpoint_path,
                                                   training=False,
                                                   trainable=False,
                                                   seq_len=self.seqence_len)                
        self.mine = Model(model.input[:2], 
                          outputs=model.get_layer('Encoder-11-FeedForward-Norm').output)
                          # 根據論文，倒數第二層出來的句子向量，效果最好，因此拿bert 1-11 層
    

    def article_preprocess(self):
        tokenizer = Tokenizer(self.token_dict)
        self.text_split = [ele for ele in self.text.split('。') if len(ele) > 0]
        self.sent_num = len(self.text_split)
        tok = [tokenizer.encode(sent)[0] for sent in self.text_split]
        tok_pad = pad_sequences(tok, maxlen=self.seqence_len)
        self.data_in = [tok_pad, np.zeros(shape=(self.sent_num, self.seqence_len))]


    def turn_vector_pca(self):
        ans = self.mine.predict(self.data_in)
        avg_tok = np.array([sum(ans[x][:]/ans.shape[2]) for x in range(self.sent_num)])
        pca = PCA(n_components=self.reduct_dim)
        pca.fit(avg_tok)
        self.X_embedded = PCA(n_components=self.reduct_dim).fit_transform(avg_tok)

        if (self.see == True) & (self.reduct_dim==2):
            print(pca.explained_variance_ratio_)
            print(self.X_embedded.shape)
            plt.scatter(self.X_embedded[:,0],self.X_embedded[:,1])
            count = 0
            for a, b in self.X_embedded:
                plt.annotate('(%s)' %(count),
                             xy=(a, b),
                             xytext=(0, 10),
                             textcoords='offset points',
                             ha='center',
                             va='top')
                count += 1
            plt.show()


    def clustering(self):
        self.X_embedded = preprocessing.scale(self.X_embedded)
        self.k_means = KMeans(init='k-means++', 
                              n_clusters=self.summary_num, 
                              n_init=10, 
                              max_iter = 600)
        self.k_means.fit(self.X_embedded)
        self.y_predict = self.k_means.predict(self.X_embedded)

        if (self.see == True) & (self.reduct_dim==2):
            plt.scatter(self.X_embedded[:,0],
                        self.X_embedded[:,1], 
                        c=self.y_predict)
            plt.scatter(self.k_means.cluster_centers_[:,0], 
                        self.k_means.cluster_centers_[:,1], 
                        marker = '*', 
                        s = 150, 
                        c='r')
            count = 0
            for a, b in self.X_embedded:
                plt.annotate('(%s)' %(count),
                             xy=(a, b),
                             xytext=(0, 15),
                             textcoords='offset points',
                             ha='center',
                             va='top')
                count += 1
            plt.show()


    def find_point(self):
        X = self.X_embedded
        y = self.y_predict
        center = self.k_means.cluster_centers_

        def distance(a,b):
            res = [(a[n]-b[n])**2  for n in range(len(a))]
            return np.sqrt(sum(res))

        output = []
        for gp in np.unique(y):
            idx_list = np.where(self.y_predict==gp)[0]
            dist_list = [distance(center[gp],X[idx]) for idx in idx_list]
            pos = np.argmin(dist_list)
            output.append(idx_list[pos])

        self.output = output


    def make_summary(self):
        self.get_model()
        self.article_preprocess()
        self.turn_vector_pca()
        self.clustering()
        self.find_point()
        summary = '。'.join([self.text_split[x] for x in self.output]) + '。'
        return summary
      

''' 測試區 '''
if __name__ == '__main__':
    text = '通用汽車（General Motors）於16日宣布逐步退出「無法獲益的市場」，包括泰國、紐西蘭和澳洲。\
也計畫將在2021年全面停止旗下品牌Holden在澳洲、紐西蘭的所有汽車銷售業務；旗下汽車品牌雪佛蘭\
（Chevrolet）也將在2020年底停止在泰國市場的銷售。並且將位於泰國汽車工業重心羅勇府（Rayong）\
的製造廠賣給中國長城汽車（Great Wall Motor）。通用汽車於17日表示，這是他們全球業務重組的一環。\
在通用汽車退出東南亞之際，長城汽車則選擇進場，並著手全球布局。《經濟日報》報導，長城汽車全球戰略副總裁劉向上表示，\
此次收購將推動長城以泰國為中心，出口產品到東協及澳洲等國。泰國工廠將成為俄羅斯圖拉廠和印度塔里岡廠後，\
長城海外第3個整車製造基地。泰國每年製造200萬輛輕型汽車，\
其中有一半出口銷售，當中多數是日本品牌Toyota、Honda和Suzuki。去年8月通用汽車就已在羅勇府的工廠裁撤了327個職位，\
為了降低成本和減產，而這次的交易則有1500個工作機會受影響。\
《Thaiger》報導，長城汽車與BMW集團合作在中國設置工廠，去年銷售了106萬台輕型汽車，其中包括6萬5175部的出口量。\
據《新華網》報導，長城汽車作為中國汽車企業龍頭，持續在皮卡及SUV市場保持領軍地位。旗下品牌哈弗蟬聯SUV銷量冠軍，\
其生產的皮卡市占率超過45%。《路透社》報導，長城汽車董事長魏建軍去年在俄羅斯建廠時曾說，\
「我們沒有選擇，如果不全球化的話無法生存。」他們的競爭對手吉利汽車（Geely）透過馬來西亞國產品牌寶騰（Proton）合作，\
擴張東南亞地區的輕型汽車銷售。長城汽車在趨緩的中國內需市場中，尋求擴張全球市場的目標，\
並表示未來將透過這間製造廠在泰國、其他東南亞國家、澳洲銷售汽車。長城汽車才在1月與通用汽車簽訂收購印度工廠，\
海通國際證券集團（Haitong Internation）的分析師Shi Ji告訴路透社，這兩家工廠的收購將加速東南亞汽車市場的開放，\
「像這樣的收購案讓長城汽車迅速接軌東南亞市場，而泰國是當中作為製造基地建立汽車工業供應鏈，一個很好的選擇。」\
泰國近來相當積極推動汽車工業轉型，包括給予本地製造的電動車享有5~25%車輛貨物稅減免等。《曼谷郵報》19日報導，\
通用汽車（General Motors）表示，汽車裝配和引擎生產的生產線都會轉移給買主。此外，也確認一旦長城汽車接管工廠，\
將辭退約1500名員工。而泰國政府希望新的經營者可以活絡電動車工業，並帶動擺脫內燃機的轉型。\
《Thaiger》報導，美國通用汽車執行長Mary Barra表示，他們可能也將在日本、俄羅斯和歐洲採取同樣的策略，\
「我們（在這些地方）沒有得到明顯收益增長」。通用汽車在聲明中表示，\
「通用汽車將著重於我們使用正確策略而得到穩健回報的市場，以及優先在全球投資可以推動經濟增長的汽車前景，比如電動或自動汽車。」\
通用汽車未來的製造鏈將更倚賴美國、中國、拉丁美洲與南韓等國。《路透社》報導，本次通用汽車估計總共將花費11億，乃是延續自2015年其停止旗下品牌汽車在印尼製造時，\
就開始陸續退出亞洲部分地區的措施。中國最大的休旅車製造商、民營企業長城汽車，17日表示已與通用汽車簽訂合約購買其在泰國羅勇的製造廠，\
並在聲明中表示預計在2020年底完成交易。電動車大戰：泰國政策優惠招9大廠進駐，\
印尼修法降稅要搶2030年1/4市佔通用汽車東南亞董事長Hector Villarreal說，約有1500名在曼谷和羅勇的員工在交易中不會被轉移，\
「通用汽車將提供資遣費和過渡期的支援給影響的員工。」\
此外，目前大約有30萬輛雪佛蘭的汽車登記在泰國，對此，他表示將提供顧客車輛服務與維修備品的擔保到2020年以後。\
不過，並沒有提到會提供多久售後服務。'

    # summary = Bert_extractive(text, 2, 2, True).make_summary()
    summary = Bert_extractive(text, 2).make_summary()
    print(summary)