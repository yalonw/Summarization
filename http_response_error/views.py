from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden, HttpResponseBadRequest

def bad_request(request, *args, **kwargs):
    return HttpResponseBadRequest(render_to_string('400.html', request=request))

def forbidden(request, *args, **kwargs):
    return HttpResponseForbidden(render_to_string('403.html', request=request))

def page_not_found(request, *args, **kwargs):
    return HttpResponseNotFound(render_to_string('404.html', request=request))

def server_error(request, *args, **kwargs):
    return HttpResponseServerError(render_to_string('500.html', request=request))


# from django.http import HttpResponse
# from django.http import HttpResponseRedirect
# 
# def request_test(request):
#     response=HttpResponse()
#     try:
#         method=request.method
#         http_host=request.META['HTTP_HOST']
#         http_user_agent=request.META['HTTP_USER_AGENT']
#         remote_addr=request.META['REMOTE_ADDR']
#         response.write('[method]:%s<br>' % (method))
#         response.write('[http_host]:%s<br>' % (http_host))
#         response.write('[http_user_agent]:%s<br>' % (http_user_agent))
#         response.write('[remote_addr]:%s' % (remote_addr))
#         response['Cache-Control']='no-cache'
#         return response
#     except e:
#         return response.write('Error:%s' % e)
#
# def redirect(request):
#     return HttpResponseRedirect("/")


def loadingpage(request):
    '''等待頁面'''
    return render(request, 'loading.html', locals())