from sys import exit
from multiprocessing import Pool

from django.core.management.base import NoArgsCommand, CommandError

from django_fugr.models import FeedData

import settings

class Command(NoArgsCommand):
	help = 'Flush all currently cached data from fugr feeds (does not delete old entries).'
	def handle_noargs(self, *args, **kwargs):
		for f in FeedData.objects.all():
			print 'Resetting "%s" <%s>' % (f.feed.title, f.feed.blog_url)
			f.parsed = None
			f.etag = None
			f.last_modified = None
			f.save()

