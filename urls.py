from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

import settings

urlpatterns = patterns('',
	# (r'^$', direct_to_template, { 'template': 'index.html' }, 'index'),
	url(r'^accounts/', include('registration.backends.default.urls')),
	url(r'^$', 'django_fugr.views.index', name='index'),
	url(r'^fugr/', include("django_fugr.urls")),

	# Examples:
	# url(r'^$', 'fugr.views.home', name='home'),
	# url(r'^fugr/', include('fugr.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
)

# serve media files statically in debug mode
if settings.DEBUG or hasattr(settings, 'SELF_SERVE'):
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
	)

