from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from django_fugr.models import Feed

class Command(BaseCommand):
    args = '<searchterm>'
    help = 'Searches the feeds for a certain string'

    def handle(self, *args, **options):
	if len(args) == 1:
		searchterm = args[0]
	        for f in Feed.objects.filter(Q(url__contains=searchterm) | Q(blog_url__contains=searchterm) | Q(title__contains=searchterm)):
			print f.title, "<" + str(f.blog_url) + ">"
	else:
		print "Supply one search term."

