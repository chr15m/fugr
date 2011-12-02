from sys import exit
from multiprocessing import Pool

from django.core.management.base import NoArgsCommand, CommandError

from django_fugr.models import Feed

import settings

def do_update(f):
	print 'Fetching "%s" <%s>' % (f.title, f.blog_url)
	f.update_feed()

class Command(NoArgsCommand):
	help = 'Cron job for fugr - updates feed cache and interest rankings.'
	def handle_noargs(self, *args, **kwargs):
		# launches a pool of processes to do the actual fetching of each feed
		fetchers = Pool(settings.FEED_FETCHER_POOL_SIZE)
		fetchers.map(do_update, Feed.objects.all())

