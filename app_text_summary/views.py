from django.shortcuts import render
from project_module import extractive_summarization_bert as esbert
from project_module import extract_time as extime

def homepage(request):
    return render(request, 'index2.html', locals())

def summary_esbert(request):
    article = request.POST['article']
    summary_num = int(request.POST['summary_num'])
    summary = esbert.Bert_extractive(article, summary_num).make_summary()
    mark = ['，', '”', '」', ')']
    extract_time = extime.GetEvent.time_event(article, mark)
    return render(request, 'analyze_result.html', locals())