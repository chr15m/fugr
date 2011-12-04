from json import dumps
import urllib2
import hashlib
import base64
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from parse_opml import parse_opml
from json_encode import json_encode

from models import Feed, FeedTag, UserFeed, UserEntry

@login_required
def index(request):
	return direct_to_template(request, "index.html", {"username": json_encode(request.user)})

############### USER ACTIONS ###############

@login_required
def update_entry(request, update_type, value, uid):
	# star, like, read
	#e = get_object_or_404(UserEntry, entry__uid=uid, user=request.user)
	e, created = UserEntry.objects.get_or_create(entry__uid=uid, user=request.user)
	if update_type in ("read", "like", "start"):
		if value == "true":
			setattr(e, update_type, datetime.now())
		elif value == "false":
			setattr(e, update_type, None)
	e.save()
	return HttpResponse(json_encode(e), mime_type="text/plain")

############### OPML UPLOAD ###############

@login_required
def opml_upload(request):
	# TODO: provide feedback to the user - progress bar
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
			feed, created = Feed.objects.get_or_create(url=feed_url, title=opmldata[feed_url]["title"], blog_url=opmldata[feed_url]["blog_url"])
			feed.save()
			print 'Feed:', feed
			# now assign this feed with these tags to the current user
			uf, created = UserFeed.objects.get_or_create(user=request.user, feed=feed)
			uf.tags = tags
			uf.save()
			print 'UserFeed:', feed
	return HttpResponseRedirect(reverse("index"))

############### Feeds we publish ###############



############### JSON API ###############

def json_api(fn):
	def newfunc(request, *args, **kwargs):
		return HttpResponse(json_encode(fn(request, *args, **kwargs)), mimetype="text/plain")
	return newfunc

@login_required
@json_api
def feeds(request):
	""" Returns the data object representing this user's feeds. """
	return dict([(uf.feed.url, {"pk": uf.feed.pk, "blog_url": uf.feed.blog_url, "title": uf.feed.title, "tags": [t.tag for t in uf.tags.all()]}) for uf in UserFeed.objects.filter(user=request.user)])

@login_required
@json_api
def feed(request, feed_url):
	""" Returns the contents of a feed. """
	# is this a special internal constructed feed (e.g. aggregation or 'interesting')
	if feed_url.startswith("/feed"):
		pass
	else:
		# TODO: hmm, shouldn't bother un-encoding and re-encoding this json object like this - probably expensive
		return get_object_or_404(UserFeed, user=request.user, feed__url=feed_url).feed.feeddata.get_cached_feed(request.user)

