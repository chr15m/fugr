from sys import exit
from multiprocessing import Pool

from django.core.management.base import NoArgsCommand, CommandError

from django_fugr.models import Feed

import settings

def do_update(f):
	print 'Fetching "%s" <%s>' % (f.title, f.blog_url)
	try:
		f.feeddata.update_feed()
	except KeyboardInterrupt, e:
		return

class Command(NoArgsCommand):
	help = 'Cron job for fugr - updates feed cache and interest rankings.'
	def handle_noargs(self, *args, **kwargs):
		# launches a pool of processes to do the actual fetching of each feed
		fetchers = Pool(settings.FEED_FETCHER_POOL_SIZE)
		try:
			fetchers.map_async(do_update, Feed.objects.all()).get(0xFFFF)
		except KeyboardInterrupt:
			# bail!
			fetchers.terminate()
			exit()

