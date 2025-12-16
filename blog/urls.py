from django.urls import path
from . import views

urlpatterns = [
    # Management URLs (Must be before slug patterns to avoid collision)
    path('manage/', views.manage_posts, name='manage_posts'),
    path('manage/create/', views.create_post, name='create_post'),
    path('manage/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('manage/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('manage/comments/', views.manage_comments, name='manage_comments'),
    path('manage/comments/<int:pk>/approve/', views.approve_comment, name='approve_comment'),
    path('manage/comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('manage/comments/<int:pk>/reply/', views.reply_comment, name='reply_comment'),
    
    # AJAX URLs
    path('manage/api/create-category/', views.create_category_ajax, name='create_category_ajax'),
    path('manage/api/create-tag/', views.create_tag_ajax, name='create_tag_ajax'),
    
    # Preview URL
    path('manage/preview/', views.post_preview, name='post_preview'),

    # Public URLs
    path('', views.post_list, name='post_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('author/<str:username>/', views.author_posts, name='author_posts'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
