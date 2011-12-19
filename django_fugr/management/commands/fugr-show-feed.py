from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.contrib.auth.models import User

from django_fugr.models import Feed

import settings

class Command(BaseCommand):
    args = '<searchterm username>'
    help = 'Searches the feeds for a certain string'

    def handle(self, *args, **options):
	if len(args) >= 1 and len(args) <= 2:
		searchterm = args[0]
		if len(args) == 2:
			user = User.objects.get(username=args[1])
		else:
			user = None
	        for feed in Feed.objects.filter(Q(url__contains=searchterm) | Q(blog_url__contains=searchterm) | Q(title__contains=searchterm)):
			print feed.title, "<" + feed.blog_url + ">"
			for e in feed.entry_set.all().order_by("-date"):
				print e
				if user:
					marked = e.entry_for_user(user)
					print "\t", marked.read and "read" or "", marked.star and "star" or "", marked.like and "like" or ""
	else:
		print "Supply one username and one search term."

