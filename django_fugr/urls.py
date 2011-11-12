from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^$', 'django_fugr.views.index', name='index'),
)
