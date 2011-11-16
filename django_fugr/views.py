from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from parse_opml import parse_opml

from models import Feed, FeedTag, UserFeed

@login_required
def index(request):
	return direct_to_template(request, "index.html", {})

@login_required
def opml_upload(request):
	uploaded = request.FILES.get('opml-upload')
	if uploaded:
		opmldata = parse_opml(uploaded.read())
		# create or modify feed objects for this opml data
		uploaded.close()
		# what the inside of each tuple looks like
		# u'http://bitcoinmorpheus.tumblr.com/rss': {'blog_url': u'http://bitcoinmorpheus.tumblr.com/',
                #                            'labels': set([u'bitcoin',
                #                                           u'economics']),
                #                            'title': u'Bitcoin Morpheus'},
		# go through every feed creating the stuff
		for feed_url in opmldata:
			# get or create the tags listed against this feed for this user
			tags = []
			for tag in opmldata[feed_url]["labels"]:
				tagobject, created = FeedTag.objects.get_or_create(tag=tag)
				tags.append(tagobject)
				tagobject.save()
				print 'FeedTag:', tagobject
			# get or create the feed
			feed, created = Feed.objects.get_or_create(feed_url=feed_url, title=opmldata[feed_url]["title"], blog_url=opmldata[feed_url]["blog_url"])
			feed.save()
			print 'Feed:', feed
			# now assign this feed with these tags to the current user
			uf, created = UserFeed.objects.get_or_create(user=request.user, feed=feed)
			uf.tags = tags
			uf.save()
			print 'UserFeed:', feed
	#from pprint import pformat
	#return HttpResponse(pformat(opmldata), mimetype="text/plain")
	return HttpResponseRedirect(reverse("index"))

