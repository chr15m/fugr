from django.conf.urls.defaults import *

urlpatterns = patterns('',
	url(r'^$', 'django_fugr.views.index', name='index'),
	url(r'^opml-upload$', 'django_fugr.views.opml_upload', name='opml_upload'),
)
