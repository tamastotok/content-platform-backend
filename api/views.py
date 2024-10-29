from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    PostSerializer,
    CommentSerializer,
    PostVoteSerializer,
    CommentVoteSerializer,
    FollowSerializer,
    CustomTokenSerializer,
)
from .models import UserProfile, Post, Comment, Vote, Follow


def csrf_token_view(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


### Custom code
class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostEditDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()


class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class FollowListView(generics.ListCreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class FollowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class UserPostsAndCommentsView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        posts = Post.objects.filter(author=user)
        comments = Comment.objects.filter(author=user)
        post_serializer = PostSerializer(posts, many=True)
        comment_serializer = CommentSerializer(comments, many=True)
        return Response(
            {'posts': post_serializer.data, 'comments': comment_serializer.data}
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
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePost(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RefreshPost(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostVoteView(generics.GenericAPIView):
    serializer_class = PostVoteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data.get('vote_type')

        # Call the toggle_vote method to handle the vote logic
        post.toggle_vote(request.user, vote_type)

        # Now, we need to return the updated total votes
        total_votes = post.total_votes  # Use the property directly

        message = "Vote updated."
        return Response(
            {"message": message, "total_votes": total_votes},
            status=status.HTTP_200_OK,
        )


class CommentVoteView(generics.GenericAPIView):
    serializer_class = CommentVoteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote_type = serializer.validated_data.get('vote_type')

        vote, created = Vote.objects.update_or_create(
            comment=comment, user=request.user, defaults={'vote_type': vote_type}
        )

        message = "Vote updated." if not created else "Vote added."
        return Response(
            {
                "message": message,
                "total_votes": comment.total_votes,
            },
            status=status.HTTP_200_OK,
        )
