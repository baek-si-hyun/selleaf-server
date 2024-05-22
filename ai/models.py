from django.db import models

from member.models import Member
from post.models import Post
from selleaf.models import Tag


class AiPost(models.Model):
    post_title = models.CharField(max_length=80, null=False)
    post_content = models.CharField(max_length=8000, null=False)
    post_tags = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'tbl_ai_post'


class AiKnowhow(models.Model):
    knowhow_title = models.CharField(max_length=80, null=False)
    knowhow_content = models.CharField(max_length=8000, null=False)
    knowhow_category = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = 'tbl_ai_knowhow'


class AiPostReply(models.Model):
    comment = models.CharField(null=False, max_length=10000)
    target = models.SmallIntegerField(default=0, null=False)

    class Meta:
        db_table = 'tbl_ai_post_reply'
        ordering = ['-id']
