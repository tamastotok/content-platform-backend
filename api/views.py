from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from django.db.models import Prefetch
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .serializers import (
    UserSerializer,
    PostSerializer,
    CommentSerializer,
    CustomTokenSerializer,
)
from .models import Post, Comment, Vote


def csrf_token_view(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


### Custom code ###


### Clear database:
class DeleteAllPosts(APIView):
    def delete(self, request):
        # Delete all posts
        deleted_count, _ = Post.objects.all().delete()

        # Return a response indicating how many posts were deleted
        return Response(
            {"message": f"{deleted_count} posts deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )


### New Codes:
class UserActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        posts = Post.objects.filter(author=user).order_by('-created_at')
        comments = Comment.objects.filter(author=user).order_by('-created_at')

        post_serializer = PostSerializer(posts, many=True)
        comment_serializer = CommentSerializer(comments, many=True)

        return Response(
            {
                "posts": post_serializer.data,
                "comments": comment_serializer.data,
            }
        )


class GetPosts(APIView):
    def get(self, request):
        # Prefetch the votes for each post to ensure they load with the query
        posts = Post.objects.prefetch_related(
            Prefetch('votes', queryset=Vote.objects.all(), to_attr='votes_set')
        ).all()

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePost(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RefreshPost(generics.RetrieveAPIView):
    queryset = Post.objects.prefetch_related(
        Prefetch('votes', queryset=Vote.objects.all(), to_attr='votes_set')
    ).all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostVoteView(generics.GenericAPIView):
    def post(self, request, post_id):
        vote_type = request.data.get('vote_type')

        # Allow None for toggling the vote off
        if vote_type not in [1, -1, None]:
            return Response(
                {
                    "error": "Invalid vote type. Must be 1 (upvote), -1 (downvote), or null for removal."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the post object
        post = get_object_or_404(Post, id=post_id)

        # Get the ContentType for the Post model
        content_type = ContentType.objects.get_for_model(Post)

        # Check if the user already voted on this post
        try:
            vote = Vote.objects.get(
                user=request.user, content_type=content_type, object_id=post_id
            )
            if vote_type is None:
                # If vote_type is None, delete the vote
                vote.delete()
            else:
                # Update the vote if it differs from the current value
                if vote.value != vote_type:
                    vote.value = vote_type
                    vote.save()
                else:
                    # If the vote is the same, delete it (toggle off)
                    vote.delete()
        except Vote.DoesNotExist:
            # Create a new vote if one doesn't exist and vote_type is not None
            if vote_type is not None:
                Vote.objects.create(
                    user=request.user,
                    content_type=content_type,
                    object_id=post_id,
                    value=vote_type,
                )

        # Update and calculate total votes
        post_total_votes = post.total_votes

        return Response(
            {
                "message": "Vote toggled successfully.",
                "upvotes": post.upvotes,
                "downvotes": post.downvotes,
                "total_votes": post_total_votes,
            },
            status=status.HTTP_200_OK,
        )


class GetComments(generics.RetrieveAPIView):
    queryset = Post.objects.prefetch_related(
        Prefetch('votes', queryset=Vote.objects.all(), to_attr='votes_set')
    ).all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
