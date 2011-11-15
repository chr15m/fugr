from django.contrib.auth.models import User
from django.db import models

class FeedTags(models.Model):
	tag = models.CharField(max_length=256)

class Feed(models.Model):
	title = models.CharField(max_length=1024)
	feed_url = models.CharField(max_length=1024)
	blog_url = models.CharField(max_length=1024)
	# text = 
	# flavour = 

class UserFeeds(models.Model):
	user = models.ForeignKey(User)
	feed = models.ForeignKey(Feed)
	tags = models.ManyToManyField(FeedTags)

