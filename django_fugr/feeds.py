from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from models import Entry, FeedTag, UserFeed

import settings

def generate_internal_feed(request, username, filter_name, *tagnames):
	# TODO: check if this user wants their stuff private?
	entries = Entry.objects.filter(feeds__userfeed__in=UserFeed.objects.filter(tags__tag__in=tagnames, user=get_object_or_404(User, username=username)))
	return {
		"feed": {
			"link": None,
			"title": username + ": " + ", ".join(tagnames)
		},
		"entries": entries
	}

def filter_all():
	pass

def filter_interesting():
	pass

def filter_popular():
	pass

