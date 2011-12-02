from datetime import datetime
from json_encode import json_encode
import base64

from django.contrib.auth.models import User
from django.db import models

import feedparser

class FeedTag(models.Model):
	""" A tag that a user can apply to a feed. """
	tag = models.CharField(max_length=256)
	
	def __unicode__(self):
		return unicode(self.tag)

class Feed(models.Model):
	""" Represents a single rss/atom feed located at a particular URL. """
	title = models.CharField(max_length=1024)
	feed_url = models.CharField(max_length=1024)
	blog_url = models.CharField(max_length=1024)
	feed_parsed_json = models.TextField(null=True)
	feed_etag = models.CharField(max_length=256, null=True, blank=True)
	feed_last_modified = models.DateTimeField(null=True, blank=True)
	last_update = models.DateTimeField(null=True)
	
	def update_feed(self):
		""" Refreshes the cached version of the parsed feed from the remote URL. """
		parsed = feedparser.parse(self.feed_url, etag=self.feed_etag, modified=self.feed_last_modified)
		if hasattr(parsed, "status"):
			if parsed.status == 304:
				# nothing has changed since our last update
				print self.feed_url, "Feed not modified"
			else:
				# store the etag and modified fields to not re-request unchanged feeds next time
				self.feed_etag = getattr(parsed, "etag", None)
				modified = getattr(parsed, "modified", None)
				self.feed_last_modified = modified and datetime(*modified[:6]) or None
				# if the bozo flag is set, turn the resulting exception into a string so we can encode it
				if parsed.bozo:
					parsed.bozo_exception = str(parsed.bozo_exception)
				# store the json encoded version of the parsed feed we fetched in a b64 blob
				self.feed_parsed_json = base64.encodestring(json_encode(parsed))
				print self.feed_url, "Stored", len(self.feed_parsed_json), "bytes"
		else:
			print self.feed_url, "Feed did not return a valid status"
		self.last_update = datetime.now()
		self.save()
	
	def __unicode__(self):
		return unicode(self.title)

class UserFeed(models.Model):
	""" Links a user to a feed with the tags that user has applied to that feed. """
	user = models.ForeignKey(User)
	feed = models.ForeignKey(Feed)
	tags = models.ManyToManyField(FeedTag)
	
	def __unicode__(self):
		return unicode(self.user) + " - " + unicode(self.feed) + " " + str(self.tags.all())

class EntryInterest(models.Model):
	""" Stores the interest value of a particular item within a feed for a particular user. """
	uid = models.CharField(max_length=1024)
	userfeed = models.ForeignKey(UserFeed)
	interest = models.IntegerField()

