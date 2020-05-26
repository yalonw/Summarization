from django.shortcuts import render

def homepage(request):
    return render(request, 'text_summary.html', locals())
