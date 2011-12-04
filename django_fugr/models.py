from datetime import datetime, timedelta
import base64

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models

import cPickle as pickle

import feedparser

import settings

class FeedTag(models.Model):
	""" A tag that a user can apply to a feed. """
	tag = models.CharField(max_length=256)
	
	def __unicode__(self):
		return unicode(self.tag)

class Feed(models.Model):
	""" Represents a single rss/atom feed located at a particular URL. """
	title = models.CharField(max_length=1024)
	blog_url = models.CharField(max_length=1024)
	url = models.CharField(max_length=1024)
	
	def __unicode__(self):
		return unicode(self.title)

class FeedData(models.Model):
	""" The heavy duty data contained in this feed, including latest feedparser object fetched. """
	etag = models.CharField(max_length=256, null=True, blank=True)
	last_modified = models.DateTimeField(null=True, blank=True)
	last_update = models.DateTimeField(null=True)
	feed = models.OneToOneField(Feed, null=True)
	parsed = models.TextField(null=True)
	
	def update_feed(self):
		""" Refreshes the cached version of the parsed feed from the remote URL. """
		url = self.feed.url
		parsed = feedparser.parse(url, etag=self.etag, modified=self.last_modified)
		if hasattr(parsed, "status"):
			if parsed.status == 304:
				# nothing has changed since our last update
				print url, "Feed not modified"
			else:
				# TODO: handle other statuses like redirect?
				# store the etag and modified fields to not re-request unchanged feeds next time
				self.etag = getattr(parsed, "etag", None)
				modified = getattr(parsed, "modified", None)
				self.last_modified = modified and datetime(*modified[:6]) or None
				# if the bozo flag is set, turn the resulting exception into a string so we can encode it
				if parsed.bozo:
					# this object does not always serialize nicely
					parsed.bozo_exception = str(parsed.bozo_exception)
				# store the pickle of the parsed feed we fetched in a b64 blob
				# TODO: also store pickle.DEFAULT_PROTOCOL and other serializing format info
				self.parsed = base64.encodestring(pickle.dumps(parsed))
				print url, "Stored", len(self.parsed), "bytes"
				# get or create all entries in this feed from the database
				for entry_data in getattr(parsed, "entries", []):
					uid = entry_data.guidislink and entry_data.get("link", None) or entry_data.get("id", None)
					if uid:
						entry, created = Entry.objects.get_or_create(uid=entry_data.id)
						# update all the relevant info for this entry from the feed
						updated = entry_data.get("updated_parsed", None)
						entry.date = updated and datetime(*updated[:6]) or None
						entry.title = entry_data.get("title", "")
						entry.parsed = base64.encodestring(pickle.dumps(entry_data))
						if not self in entry.feeds.all():
							entry.feeds.add(self.feed)
						entry.save()
					else:
						pass
						# malformed entry, not really sure what to do
		else:
			print url, "Feed did not return a valid status"
		self.last_update = datetime.now()
		self.save()
	
	def get_cached_feed(self, user):
		""" Unpickles and returns the cached version of the feedparser object. """
		# check if we have a recent copy of this feed
		if self.parsed is None or self.last_update < datetime.now() - timedelta(days=1) and self.feed:
			# for whatever reason we don't have a recent copy of this feed
			self.update_feed()
		feed = pickle.loads(base64.decodestring(self.parsed))
		# add the entries with the user data for this user
		feed.entries = [e.entry_for_user(user) for e in self.feed.entry_set.all()[:settings.FEED_ITEMS_PER_REQUEST]]
		return feed
	
	def __unicode__(self):
		return self.feed.__unicode__()

# When a Feed is created, also create the FeedData object that belongs to it
@receiver(post_save, sender=Feed)
def create_feeddata(sender, instance, created, **kwargs):
	if created:
		FeedData.objects.create(feed=instance)

class UserFeed(models.Model):
	""" Links a user to a feed with the tags that user has applied to that feed. """
	user = models.ForeignKey(User)
	feed = models.ForeignKey(Feed)
	tags = models.ManyToManyField(FeedTag)
	
	def __unicode__(self):
		return unicode(self.user) + " - " + unicode(self.feed) + " " + str(self.tags.all())

class Entry(models.Model):
	""" Single entry from a feed including a cached version of the parsed object. """
	title = models.CharField(max_length=1024, null=True)
	uid = models.CharField(max_length=256)
	date = models.DateTimeField(null=True)
	feeds = models.ManyToManyField(Feed)
	parsed = models.TextField(null=True)
	
	def entry_for_user(self, user):
		""" Get the entry with the entry data applied by the user. """
		entry_data = pickle.loads(base64.decodestring(self.parsed))
		try:
			user_data = self.userentry_set.get()
		except UserEntry.DoesNotExist:
			user_data = UserEntry()
		if user_data:
			entry_data.like = user_data.like
			entry_data.read = user_data.read
			entry_data.star = user_data.star
		return entry_data
	
	def __unicode__(self):
		return self.date.strftime("%Y-%m-%d %H:%M") + " " + self.title

class UserEntry(models.Model):
	""" Relationship a user has to a particular entry in a feed. """
	entry = models.ForeignKey(Entry)
	user = models.ForeignKey(User)
	read = models.DateTimeField(null=True, blank=True)
	like = models.DateTimeField(null=True, blank=True)
	star = models.DateTimeField(null=True, blank=True)
	interest = models.FloatField(default=0)

