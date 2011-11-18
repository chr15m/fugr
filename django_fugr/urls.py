from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# root static page
	url(r'^$', 'django_fugr.views.index', name='index'),
	# upload handler for OPML files
	url(r'^opml-upload$', 'django_fugr.views.opml_upload', name='opml_upload'),
	# feed loader - returns XML to the browser
	url(r'^xml/feed/(?P<feed_url>.*)$', 'django_fugr.views.feed', name='xml_feed'),
	
	# JSON API
	url(r'^json/feeds$', 'django_fugr.views.feeds', name='json_feeds'),
)
