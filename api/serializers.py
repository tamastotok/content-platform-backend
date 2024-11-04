from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile, Post, Comment, Vote, Follow
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.middleware.csrf import get_token
from django.db import models


class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id  # Add user ID to the token
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id  # Add user ID to the response
        data['csrfToken'] = get_token(
            self.context['request']
        )  # Include CSRF token in the response
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


### Custom code
class VoteSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Vote
        fields = ['user_id', 'value']  # Only include user_id and vote value


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    votes = VoteSerializer(
        many=True, source='votes_set', read_only=True
    )  # Nested votes

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'author_username',
            'content',
            'created_at',
            'updated_at',
            'upvotes',
            'downvotes',
            'total_votes',
            'votes',
        ]
        read_only_fields = [
            'post',
            'created_at',
            'updated_at',
            'upvotes',
            'downvotes',
            'total_votes',
        ]


class PostSerializer(serializers.ModelSerializer):
    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    votes = VoteSerializer(many=True, source='votes_set', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'author_username',
            'title',
            'content',
            'created_at',
            'updated_at',
            'category',
            'keywords',
            'upvotes',
            'downvotes',
            'total_votes',
            'comments_count',
            'votes',
            'comments',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
            'upvotes',
            'downvotes',
            'total_votes',
            'comments_count',
        ]


'''
class PostVoteSerializer(serializers.ModelSerializer):
    vote_type = serializers.ChoiceField(choices=Vote.VOTE_CHOICES)

    class Meta:
        model = Vote
        fields = [
            'vote_type',
            'content_type',
            'object_id',
        ]  # Adjusted for GenericForeignKey

    def validate(self, data):
        # Ensure that vote_type is either 1 (upvote) or -1 (downvote)
        if data['vote_type'] not in [1, -1]:
            raise serializers.ValidationError("Invalid vote type. Must be 1 or -1.")
        return data


class CommentVoteSerializer(serializers.ModelSerializer):
    vote_type = serializers.ChoiceField(choices=Vote.VOTE_CHOICES)

    class Meta:
        model = Vote
        fields = ['vote_type', 'comment']

    def validate(self, data):
        if not data.get('comment'):
            raise serializers.ValidationError(
                "Comment ID is required for comment voting."
            )
        if data.get('post'):
            raise serializers.ValidationError(
                "Cannot vote on both post and comment at the same time."
            )
        return data

'''


###
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following']
        read_only_fields = ['id']  # Make 'id' read-only
