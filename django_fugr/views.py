from json import dumps
import urllib2

from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from parse_opml import parse_opml
from json_encode import json_encode

from models import Feed, FeedTag, UserFeed

@login_required
def index(request):
	return direct_to_template(request, "index.html", {"feeds": feeds(request)})

############### OPML UPLOAD ###############

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
	return HttpResponseRedirect(reverse("index"))

############### FEED FETCHER ###############

@login_required
def feed(request, feed_url):
	""" Returns the actual XML of a particular feed. """
	# security - make sure this feed is one the user owns
	feed = get_object_or_404(UserFeed, user=request.user, feed__feed_url=feed_url)
	response = urllib2.urlopen(feed_url)
	return HttpResponse(response)

############### JSON API ###############

def json_api(fn):
	def newfunc(request, *args, **kwargs):
		return HttpResponse(json_encode(fn(request, *args, **kwargs)), mimetype="text/plain")
	return newfunc

@login_required
@json_api
def feeds(request):
	""" Returns the data object representing this user's feeds. """
	return dict([(uf.feed.feed_url, {"pk": uf.feed.pk, "blog_url": uf.feed.blog_url, "title": uf.feed.title, "tags": [t.tag for t in uf.tags.all()]}) for uf in UserFeed.objects.filter(user=request.user)])

