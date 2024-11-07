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
from django.http import Http404, JsonResponse
from .serializers import (
    UserSerializer,
    PostSerializer,
    CommentSerializer,
    CustomTokenSerializer,
    UserProfileSerializer,
)
from .models import Post, Comment, Vote, UserProfile
from rest_framework.exceptions import NotFound


def csrf_token_view(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # First, create the user using the serializer
        user = serializer.save()

        # Now create the UserProfile for the new user
        UserProfile.objects.create(user=user)


class EditUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        # Ensure the user is only updating their own profile
        return self.request.user

    def perform_update(self, serializer):
        # Update the user details
        user = serializer.save()

        # Check if a UserProfile exists, if not, create it
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        # Optionally, update the UserProfile's bio and profile_picture
        user_profile.bio = self.request.data.get('bio', user_profile.bio)
        user_profile.profile_picture = self.request.data.get(
            'profile_picture', user_profile.profile_picture
        )
        user_profile.save()

        return user  # Return the updated user object


class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def perform_destroy(self, instance):
        # Optional: You can add extra actions before deleting the user (e.g., logging or sending a notification)
        instance.delete()


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
        comments = (
            Comment.objects.filter(author=user)
            .select_related('post')
            .order_by('-created_at')
        )  # Optimize with select_related

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
            Prefetch('votes', queryset=Vote.objects.all(), to_attr='post_votes_set')
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
        Prefetch('votes', queryset=Vote.objects.all(), to_attr='post_votes_set')
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
        'votes',
        'comments__votes',
    ).all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CreateComment(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)


class CommentVoteView(generics.GenericAPIView):
    def post(self, request, post_id, comment_id):
        vote_type = request.data.get('vote_type')

        # Validate vote_type (1 for upvote, -1 for downvote, None for removal)
        if vote_type not in [1, -1, None]:
            return Response(
                {
                    "error": "Invalid vote type. Must be 1 (upvote), -1 (downvote), or null for removal."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the post object
        post = get_object_or_404(Post, id=post_id)

        # Try to get the comment
        comment = get_object_or_404(post.comments.all(), id=comment_id)

        # The content type is always for the Comment model, no reply logic needed
        content_type = ContentType.objects.get_for_model(Comment)

        # Check if the user already voted on this comment
        try:
            vote = Vote.objects.get(
                user=request.user, content_type=content_type, object_id=comment_id
            )
            if vote_type is None:
                vote.delete()  # Delete vote if vote_type is None (toggle off)
            else:
                if vote.value != vote_type:
                    vote.value = vote_type
                    vote.save()
                else:
                    vote.delete()  # Toggle off if the same vote is submitted again
        except Vote.DoesNotExist:
            if vote_type is not None:
                Vote.objects.create(
                    user=request.user,
                    content_type=content_type,
                    object_id=comment_id,
                    value=vote_type,
                )

        return Response(
            {
                "message": "Vote toggled successfully.",
                "upvotes": comment.upvotes,
                "downvotes": comment.downvotes,
                "total_votes": comment.total_votes,
            },
            status=status.HTTP_200_OK,
        )


class RefreshComment(generics.RetrieveAPIView):
    queryset = Comment.objects.prefetch_related(
        Prefetch('votes', queryset=Vote.objects.all(), to_attr='post_votes_set')
    ).all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditComment(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')

        # Ensure the comment belongs to the specified post and get the comment
        comment = get_object_or_404(Comment, id=comment_id, post__id=post_id)

        # Optional: Check if the request user is the author of the comment
        if comment.author != self.request.user:
            self.permission_denied(
                self.request, message="You do not have permission to edit this comment."
            )

        return comment

    def update(self, request, *args, **kwargs):
        # Perform the update with partial update option
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteComment(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the specific comment by post_id and comment_id
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')

        # Ensure the comment belongs to the specified post
        return get_object_or_404(Comment, id=comment_id, post__id=post_id)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user is the comment's author (added for extra safety)
        if instance.author != request.user:
            return Response(
                {"detail": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.perform_destroy(instance)
        return Response(
            {"message": "Comment deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class DeletePost(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_object(self):
        """
        Override the get_object method to handle retrieving the post.
        Ensures the post exists or raises a 404 error.
        """
        obj = super().get_object()  # Get the object using the provided id
        if obj.author.id != self.request.user.id:
            raise PermissionDenied('You are not authorized to delete this post.')
        return obj

    def perform_destroy(self, instance):
        """
        Override the perform_destroy method to delete the post.
        """
        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )  # Return a 204 No Content status after deletion


class EditPost(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'post_id'  # Use 'post_id' in the URL instead of 'id'

    def update(self, request, *args, **kwargs):
        post = self.get_object()

        # Check if the user is the author of the post
        if request.user != post.author:
            return Response(
                {"error": "You do not have permission to edit this post."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Proceed with the regular update logic
        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetProfile(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'pk'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound("This user does not have a profile.")
