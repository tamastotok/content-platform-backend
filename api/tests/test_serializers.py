from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from ..models import Post
from ..serializers import (
    UserProfileSerializer,
    PostSerializer,
    CommentSerializer,
    VoteSerializer,
    FollowSerializer,
)

User = get_user_model()


class UserProfileSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile_data = {'user': self.user.id, 'bio': 'Test Bio'}

    def test_user_profile_serialization(self):
        serializer = UserProfileSerializer(data=self.profile_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['bio'], 'Test Bio')

    def test_user_profile_creation(self):
        serializer = UserProfileSerializer(data=self.profile_data)
        self.assertTrue(serializer.is_valid())
        user_profile = serializer.save()
        self.assertEqual(user_profile.user, self.user)
        self.assertEqual(user_profile.bio, 'Test Bio')


class PostSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post_data = {
            'author': self.user.id,
            'title': 'Test Post',
            'content': 'This is a test post.',
            'category': 'Test Category',
            'keywords': 'test, post',
        }

    def test_post_serialization(self):
        serializer = PostSerializer(data=self.post_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['title'], 'Test Post')

    def test_post_creation(self):
        serializer = PostSerializer(data=self.post_data)
        self.assertTrue(serializer.is_valid())
        post = serializer.save()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.title, 'Test Post')


class CommentSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user, title='Test Post', content='Content'
        )
        self.comment_data = {
            'post': self.post.id,
            'author': self.user.id,
            'content': 'This is a test comment.',
        }

    def test_comment_serialization(self):
        serializer = CommentSerializer(data=self.comment_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data['content'], 'This is a test comment.'
        )

    def test_comment_creation(self):
        serializer = CommentSerializer(data=self.comment_data)
        self.assertTrue(serializer.is_valid())
        comment = serializer.save()
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.content, 'This is a test comment.')


class VoteSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user, title='Test Post', content='Content'
        )
        self.vote_data = {
            'user': self.user.id,
            'post': self.post.id,
            'vote_type': 1,  # Upvote
        }

    def test_vote_serialization(self):
        serializer = VoteSerializer(data=self.vote_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['vote_type'], 1)

    def test_vote_creation(self):
        serializer = VoteSerializer(data=self.vote_data)
        self.assertTrue(serializer.is_valid())
        vote = serializer.save()
        self.assertEqual(vote.user, self.user)
        self.assertEqual(vote.post, self.post)


class FollowSerializerTest(APITestCase):
    def setUp(self):
        self.follower = User.objects.create_user(
            username='follower', password='testpass'
        )
        self.following = User.objects.create_user(
            username='following', password='testpass'
        )
        self.follow_data = {
            'follower': self.follower.id,
            'following': self.following.id,
        }

    def test_follow_serialization(self):
        serializer = FollowSerializer(data=self.follow_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['follower'], self.follower)

    def test_follow_creation(self):
        serializer = FollowSerializer(data=self.follow_data)
        self.assertTrue(serializer.is_valid())
        follow = serializer.save()
        self.assertEqual(follow.follower, self.follower)
        self.assertEqual(follow.following, self.following)
