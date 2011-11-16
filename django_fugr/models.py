from django.contrib.auth.models import User
from django.db import models

class FeedTag(models.Model):
	tag = models.CharField(max_length=256)
	
	def __unicode__(self):
		return unicode(self.tag)

class Feed(models.Model):
	title = models.CharField(max_length=1024)
	feed_url = models.CharField(max_length=1024)
	blog_url = models.CharField(max_length=1024)
	# text = 
	# flavour = 
	
	def __unicode__(self):
		return unicode(self.title)

class UserFeed(models.Model):
	user = models.ForeignKey(User)
	feed = models.ForeignKey(Feed)
	tags = models.ManyToManyField(FeedTag)
	
	def __unicode__(self):
		return unicode(self.user) + " - " + unicode(self.feed) + " " + str(self.tags.all())

