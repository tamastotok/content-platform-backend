from django.urls import path

from .views import (
    #    NoteListCreate,
    #    NoteDelete,
    #    UserProfileDetailView,
    PostListCreate,
    #    PostEditDelete,
    #    CommentListView,
    #    CommentDetailView,
    #    VoteListView,
    #    VoteDetailView,
    #    FollowListView,
    #    FollowDetailView,
    #    UserPostsAndCommentsView,
    UserActivityView,
    GetPosts,
    RefreshPost,
    CreatePost,
    PostVoteView,
    CommentVoteView,
    DeleteAllPosts,
)

# urlpatterns = [
#    path("notes/", NoteListCreate.as_view(), name="note-list"),
#    path("notes/delete/<int:pk>/", NoteDelete.as_view(), name="delete-note"),
### Custom code
#    path(
#        'profiles/<int:pk>/', UserProfileDetailView.as_view(), name='userprofile-detail'
#    ),
# path('posts/', PostListCreate.as_view(), name='post-create'),
#    path('posts/', GetPosts.as_view(), name='get-posts'),
#    path('post/create/', CreatePost.as_view, name='create-post'),
#    path('user/<str:username>/', GetUserInfo.as_view, name='user-info'),
# path('posts/<int:pk>/', PostEditDelete.as_view(), name='post-delete'),
# path('comments/', CommentListView.as_view(), name='comment-list'),
# path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
# path('votes/', VoteListView.as_view(), name='vote-list'),
# path('votes/<int:pk>/', VoteDetailView.as_view(), name='vote-detail'),
# path('follows/', FollowListView.as_view(), name='follow-list'),
# path('follows/<int:pk>/', FollowDetailView.as_view(), name='follow-detail'),
# path(
#    'api/user/posts-comments/',
#    UserPostsAndCommentsView.as_view(),
#    name='user-posts-comments',
# ),
# ]

urlpatterns = [
    ### User Paths
    path(
        'user-activity/<str:username>/',
        UserActivityView.as_view(),
        name='user-activity',
    ),
    path('posts/<int:post_id>/vote/', PostVoteView.as_view(), name='vote-on-post'),
    path(
        'comments/<int:comment_id>/vote/',
        CommentVoteView.as_view(),
        name='vote-on-comment',
    ),
    path('posts/delete/all/', DeleteAllPosts.as_view(), name='delete-posts'),
    #    path('settings/update/<str:username>/', UpdateUser_as.view, name='user-update'),
    #    path('settings/delete/<str:username>/', DeleteUser_as.view, name='delete-update'),
    #    ### Posts
    path('post/create/', CreatePost.as_view(), name='create-post'),
    path('posts/', GetPosts.as_view(), name='get-posts'),
    # path('posts/', PostListCreate.as_view(), name='post-create'),  # ÁTÍRNI!!!
    path('posts/<int:pk>', RefreshPost.as_view(), name='post-refresh'),
    #    path('post/edit/<id:pk>/', EditPost.view, name='edit-post'),
    #    path('post/delete/<id:pk>/', DeletePost.view, name='delete-post'),
    #    ### Comments
    #    path('comments/create/', CreateComment.view, name='create-comment'),
    #    path('comment/edit/<id:pk>/', EditComment.view, name='edit-comment'),
    #    path('comment/delete/<id:pk>/', DeleteComment.view, name='delete-comment'),
    #    ### Votes
    #    path('vote/post/<id:pk>/', VotePost.view, name='vote-post'),
    #    path('vote/comment/<id:pk>/', VoteComment.view, name='vote-comment'),
]
