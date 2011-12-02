from multiprocessing import Process
from sys import exit

from django.core.management.base import NoArgsCommand, CommandError

from django_fugr.models import Feed

def do_update(f):
	print 'Updating "%s" <%s>' % (f.title, f.blog_url)
	f.update_feed()

class Command(NoArgsCommand):
	help = 'Cron job for fugr - updates feed cache and interest rankings.'
	def handle_noargs(self, *args, **kwargs):
		for f in Feed.objects.all():
			# do this in parallel
			#try:
			#	t = Process(target=lambda: do_update(f))
			#	t.start()
			#except KeyboardInterrupt:
			#	exit()
			do_update(f)
			# raise CommandError('Poll "%s" does not exist' % poll_id)

