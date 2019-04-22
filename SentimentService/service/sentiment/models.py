from django.db import models


class Comment(models.Model):
    comment_id = models.TextField(unique=True, max_length=20)
    submission_id = models.TextField(max_length=20)
    subreddit_id = models.TextField(max_length=20)
    subreddit_name = models.TextField(max_length=100)
    parent_id = models.TextField(max_length=20)
    created_utc = models.DateTimeField(null=True, default=None)
    is_distinguished = models.BooleanField(default=False)
    score = models.IntegerField()
    body = models.TextField()


class CommentSentiment(models.Model):
    comment = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='sentiment')
    positive = models.FloatField()
    neutral = models.FloatField()
    negative = models.FloatField()
    compound = models.FloatField()


class SubredditSentiment(models.Model):
    subreddit_id = models.TextField(unique=True, max_length=20)
    subreddit_name = models.TextField(unique=True, max_length=100)
    positive = models.FloatField(default=0.0, blank=True)
    neutral = models.FloatField(default=0.0, blank=True)
    negative = models.FloatField(default=0.0, blank=True)
    compound = models.FloatField(default=0.0, blank=True)
    count = models.IntegerField(default=0, blank=True)
