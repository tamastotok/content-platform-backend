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
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'profile_picture']
        read_only_fields = ['id']


###
class PostSerializer(serializers.ModelSerializer):
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'created_at',
            'updated_at',
            'category',
            'keywords',
            'upvotes',
            'downvotes',
            'total_votes',
        ]

    def get_upvotes(self, obj):
        return obj.upvotes  # Now correctly gets the count

    def get_downvotes(self, obj):
        return obj.downvotes  # Now correctly gets the count

    def get_total_votes(self, obj):
        return obj.total_votes  # Now calculates total votes


class CommentSerializer(serializers.ModelSerializer):
    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'post_title',
            'content',
            'created_at',
            'updated_at',
            'upvotes',
            'downvotes',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['upvotes'] = instance.vote_set.filter(vote_type=1).count()
        representation['downvotes'] = instance.vote_set.filter(vote_type=-1).count()
        return representation


class PostVoteSerializer(serializers.ModelSerializer):
    vote_type = serializers.ChoiceField(choices=Vote.VOTE_CHOICES)

    class Meta:
        model = Vote
        fields = ['vote_type', 'post']

    def validate(self, data):
        if not data.get('post'):
            raise serializers.ValidationError("Post ID is required for post voting.")
        if data.get('comment'):
            raise serializers.ValidationError(
                "Cannot vote on both post and comment at the same time."
            )

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


###
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following']
        read_only_fields = ['id']  # Make 'id' read-only
