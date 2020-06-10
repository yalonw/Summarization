from django.shortcuts import render
from project_module import extractive_summarization_bert as esbert

def homepage(request):
    return render(request, 'index2.html', locals())

def summary_esbert(request):
    article = request.POST['article']
    summary_num = int(request.POST['summary_num'])
    summary = esbert.Bert_extractive(article, summary_num).make_summary()
    return render(request, 'analyze_result.html', locals())