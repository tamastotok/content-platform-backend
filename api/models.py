from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.CharField(max_length=100, blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    votes = GenericRelation('Vote', related_query_name='post_votes_set')

    @property
    def upvotes(self):
        return Vote.objects.filter(
            content_type=ContentType.objects.get_for_model(Post),
            object_id=self.id,
            value=1,
        ).count()

    @property
    def downvotes(self):
        return Vote.objects.filter(
            content_type=ContentType.objects.get_for_model(Post),
            object_id=self.id,
            value=-1,
        ).count()

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    votes = GenericRelation('Vote', related_query_name='comment_votes_set')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )

    @property
    def upvotes(self):
        return Vote.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
            value=1,
        ).count()

    @property
    def downvotes(self):
        return Vote.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
            value=-1,
        ).count()

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class Vote(models.Model):
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    value = models.IntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f'Vote by {self.user.username} on {self.content_object} - {self.get_vote_type_display()}'


class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User, related_name='followers', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
