from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# root static page
	url(r'^$', 'django_fugr.views.index', name='index'),
	# upload handler for OPML files
	url(r'^opml-upload$', 'django_fugr.views.opml_upload', name='opml_upload'),
	# user actions
	url(r'^update-entry/(?P<update_type>read|like|star)/(?P<value>true|false)/(?P<uid>.*)$', 'django_fugr.views.update_entry', name='update_entry'),
	
	# JSON API
	url(r'^json/feeds$', 'django_fugr.views.feeds', name='json_feeds'),
	url(r'^json/feed/(?P<feed_url>.*)$', 'django_fugr.views.feed', name='json_feed'),
)
