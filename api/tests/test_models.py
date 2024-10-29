from django.test import TestCase
from django.contrib.auth.models import User
from ..models import UserProfile, Post, Comment, Vote, Follow


class TestUserProfileModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.profile = UserProfile.objects.create(user=self.user, bio='Test bio')

    def test_str(self):
        self.assertEqual(str(self.profile), 'testuser')


class TestPostModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.post = Post.objects.create(
            author=self.user, title='Test Title', content='Test Content'
        )

    def test_str(self):
        self.assertEqual(str(self.post), 'Test Title')

    def test_total_votes(self):
        self.assertEqual(self.post.total_votes, 0)  # Initially, no votes should be 0


class TestCommentModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.post = Post.objects.create(
            author=self.user, title='Test Title', content='Test Content'
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, content='Test Comment'
        )

    def test_str(self):
        self.assertEqual(str(self.comment), 'Comment by testuser on Test Title')


class TestVoteModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.other_user = User.objects.create(username='otheruser')
        self.post = Post.objects.create(
            author=self.user, title='Test Title', content='Test Content'
        )
        self.vote = Vote.objects.create(
            user=self.user, post=self.post, vote_type=1
        )  # Upvote

    def test_str(self):
        self.assertEqual(str(self.vote), 'Vote by testuser on Test Title - Upvote')

    def test_unique_together(self):
        with self.assertRaises(Exception):
            Vote.objects.create(
                user=self.user, post=self.post, vote_type=-1
            )  # Should raise IntegrityError


class TestFollowModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.other_user = User.objects.create(username='otheruser')
        self.follow = Follow.objects.create(
            follower=self.user, following=self.other_user
        )

    def test_str(self):
        self.assertEqual(str(self.follow), 'testuser follows otheruser')

    def test_unique_together(self):
        with self.assertRaises(Exception):
            Follow.objects.create(
                follower=self.user, following=self.other_user
            )  # Should raise IntegrityError
