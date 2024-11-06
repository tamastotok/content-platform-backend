from django.urls import path

from .views import (
    UserActivityView,
    GetPosts,
    RefreshPost,
    CreatePost,
    PostVoteView,
    DeleteAllPosts,
    GetComments,
    CreateComment,
    CommentVoteView,
    EditComment,
    DeleteComment,
)

urlpatterns = [
    ### User Paths
    path(
        'user-activity/<str:username>/',
        UserActivityView.as_view(),
        name='user-activity',
    ),
    path('posts/<int:post_id>/vote/', PostVoteView.as_view(), name='vote-on-post'),
    path('posts/delete/all/', DeleteAllPosts.as_view(), name='delete-posts'),
    #    path('settings/update/<str:username>/', UpdateUser_as.view, name='user-update'),
    #    path('settings/delete/<str:username>/', DeleteUser_as.view, name='delete-update'),
    #    ### Posts
    path('post/create/', CreatePost.as_view(), name='create-post'),
    path('posts/', GetPosts.as_view(), name='get-posts'),
    path('posts/<int:pk>/', RefreshPost.as_view(), name='post-refresh'),
    path('comments/<int:pk>/', GetComments.as_view(), name='get-comments'),
    path(
        'comments/<int:post_id>/create/', CreateComment.as_view(), name='create-comment'
    ),
    path(
        'comments/<int:post_id>/<int:comment_id>/vote/',
        CommentVoteView.as_view(),
        name='vote-on-comment',
    ),
    path(
        'comments/<int:post_id>/update/<int:comment_id>/',
        EditComment.as_view(),
        name='edit-comment',
    ),
    path(
        'comments/<int:post_id>/delete/<int:comment_id>/',
        DeleteComment.as_view(),
        name='delete-comment',
    ),
    #    path('post/edit/<id:pk>/', EditPost.view, name='edit-post'),
    #    path('post/delete/<id:pk>/', DeletePost.view, name='delete-post'),
    #    ### Comments
    #    path('comment/edit/<id:pk>/', EditComment.view, name='edit-comment'),
    #    path('comment/delete/<id:pk>/', DeleteComment.view, name='delete-comment'),
    #    ### Votes
    #    path('vote/post/<id:pk>/', VotePost.view, name='vote-post'),
    #    path('vote/comment/<id:pk>/', VoteComment.view, name='vote-comment'),
]
