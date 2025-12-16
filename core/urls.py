from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.service_list, name='service_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<slug:slug>/', views.project_detail, name='project_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # Management URLs
    path('manage/projects/', views.manage_projects, name='manage_projects'),
    path('manage/projects/create/', views.create_project, name='create_project'),
    path('manage/projects/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('manage/projects/<int:pk>/delete/', views.delete_project, name='delete_project'),
    
    path('manage/messages/', views.manage_messages, name='manage_messages'),
    path('manage/messages/<int:pk>/delete/', views.delete_message, name='delete_message'),

    # Testimonial Management URLs
    path('manage/testimonials/', views.manage_testimonials, name='manage_testimonials'),
    path('manage/testimonials/create/', views.create_testimonial, name='create_testimonial'),
    path('manage/testimonials/<int:pk>/edit/', views.edit_testimonial, name='edit_testimonial'),
    path('manage/testimonials/<int:pk>/delete/', views.delete_testimonial, name='delete_testimonial'),
]
