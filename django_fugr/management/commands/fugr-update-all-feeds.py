from sys import exit, exc_info
from multiprocessing import Pool

from django.core.management.base import BaseCommand, CommandError

from django_fugr.models import Feed

import settings

def do_update(f):
	print unicode(u'Fetching "%s" <%s>' % (f.title, f.blog_url)).encode("utf-8")
	try:
		print unicode(f.feeddata.update_feed()).encode("utf-8")
	except:
		return exc_info()

class Command(BaseCommand):
	args = '<non-threaded>'
	help = 'Updates all known feeds in parallel using multiple processes (configurable with FEED_FETCHER_POOL_SIZE). Eats a fair bit of CPU.'
	def handle(self, *args, **options):
		feeds = Feed.objects.all()
		if len(args):
			[do_update(f) for f in feeds]
		else:
			# launches a pool of processes to do the actual fetching of each feed
			fetchers = Pool(settings.FEED_FETCHER_POOL_SIZE)
			try:
				for exception in fetchers.map_async(do_update, feeds).get(0xFFFF):
					if exception:
						raise exception[1], None, exception[2]
			except KeyboardInterrupt:
				print "Bail!"
				fetchers.terminate()
				exit()
		print feeds.count(), "fetched"

