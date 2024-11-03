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

        # Ensure vote_type is either 1 (upvote) or -1 (downvote)
        if vote_type not in [1, -1]:
            return Response(
                {"error": "Invalid vote type. Must be 1 (upvote) or -1 (downvote)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the post object
        post = get_object_or_404(Post, id=post_id)

        # Get the ContentType for the Post model
        content_type = ContentType.objects.get_for_model(Post)

        # Check if the user already voted on this post
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=post_id,
            defaults={'value': vote_type},
        )

        if created:
            # If this is a new vote, set the vote type
            vote.value = vote_type
            vote.save()
        else:
            # Toggle the vote if the user clicks the same button again
            if vote.value == vote_type:
                # If the user clicks the same button (e.g., upvote again), remove the vote
                vote.delete()
            else:
                # Otherwise, update the vote to the new value
                vote.value = vote_type
                vote.save()

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
