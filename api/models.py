from django.db import models
from django.contrib.auth.models import User


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

    @property
    def upvotes(self):
        return self.vote_set.filter(vote_type=1).count()  # Count of upvotes

    @property
    def downvotes(self):
        return self.vote_set.filter(vote_type=-1).count()  # Count of downvotes

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes  # Calculate total votes

    def toggle_vote(self, user, vote_type):
        try:
            vote = Vote.objects.get(post=self, user=user)
            if vote.vote_type == vote_type:
                vote.delete()  # Remove vote
            else:
                # If switching votes
                if vote.vote_type == 1 and vote_type == -1:
                    vote.delete()  # Remove upvote
                    Vote.objects.create(
                        post=self, user=user, vote_type=-1
                    )  # Add downvote
                elif vote.vote_type == -1 and vote_type == 1:
                    vote.delete()  # Remove downvote
                    Vote.objects.create(post=self, user=user, vote_type=1)  # Add upvote
        except Vote.DoesNotExist:
            Vote.objects.create(post=self, user=user, vote_type=vote_type)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_votes(self):
        return self.vote_set.aggregate(total=models.Sum('vote_type'))['total'] or 0

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


class Vote(models.Model):
    VOTE_CHOICES = (
        (1, 'Upvote'),
        (-1, 'Downvote'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    vote_type = models.IntegerField(choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'Vote by {self.user.username} on {self.post.title} - {self.get_vote_type_display()}'


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
