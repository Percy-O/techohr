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
    path('reviews/new/', views.submit_review, name='submit_review'),
    
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

    # Settings & Team Management URLs
    path('manage/settings/', views.manage_settings, name='manage_settings'),
    path('manage/employees/', views.manage_employees, name='manage_employees'),
    path('manage/employees/create/', views.create_employee, name='create_employee'),
    path('manage/employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
    path('manage/employees/<int:pk>/delete/', views.delete_employee, name='delete_employee'),
]
