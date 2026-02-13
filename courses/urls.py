from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    # Management URLs
    path('manage/', views.manage_courses, name='manage_courses'),
    path('manage/create/', views.create_course, name='create_course'),
    path('manage/<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('manage/<int:pk>/delete/', views.delete_course, name='delete_course'),
    
    path('manage/categories/', views.manage_course_categories, name='manage_course_categories'),
    path('manage/categories/<int:pk>/delete/', views.delete_course_category, name='delete_course_category'),
    
    path('manage/enrollments/', views.manage_enrollments, name='manage_enrollments'),
    path('manage/certificates/', views.manage_certificates, name='manage_certificates'),
    path('manage/certificates/settings/', views.manage_certificate_settings, name='manage_certificate_settings'),
    path('manage/reviews/', views.manage_reviews, name='manage_reviews'),
    path('manage/reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),
    
    path('manage/<int:course_pk>/modules/', views.manage_modules, name='manage_modules'),
    path('manage/modules/<int:pk>/edit/', views.edit_module, name='edit_module'),
    path('manage/modules/<int:pk>/delete/', views.delete_module, name='delete_module'),
    
    path('manage/modules/<int:module_pk>/lessons/create/', views.create_lesson, name='create_lesson'),
    path('manage/lessons/<int:pk>/edit/', views.edit_lesson, name='edit_lesson'),
    path('manage/lessons/<int:pk>/delete/', views.delete_lesson, name='delete_lesson'),

    # Assessment Management
    path('manage/modules/<int:module_pk>/assessments/create/', views.create_module_assessment, name='create_module_assessment'),
    path('manage/courses/<int:course_pk>/assessments/create/', views.create_course_assessment, name='create_course_assessment'),
    path('manage/assessments/<int:pk>/edit/', views.edit_assessment, name='edit_assessment'),
    path('manage/assessments/<int:pk>/delete/', views.delete_assessment, name='delete_assessment'),
    path('manage/assessments/<int:pk>/questions/', views.manage_assessment_questions, name='manage_assessment_questions'),
    path('manage/questions/<int:pk>/choices/', views.manage_question_choices, name='manage_question_choices'),
    path('manage/assessments/<int:pk>/submissions/', views.manage_submissions, name='manage_submissions'),
    path('manage/submissions/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    path('manage/payments/', views.manage_payments, name='manage_payments'),
    path('manage/payments/settings/', views.manage_payment_settings, name='manage_payment_settings'),
    
    # Taking Assessments
    path('assessment/<int:pk>/submit/', views.submit_assessment, name='submit_assessment'),

    # Progress & Certificates
    path('lesson/<int:pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('certificate/<str:certificate_id>/download/', views.download_certificate, name='download_certificate'),

    # Public Course URLs (Must be last to avoid conflict with 'manage/')
    path('<slug:slug>/pay/', views.course_payment, name='course_payment'),
    path('<slug:slug>/pay/init/', views.init_course_payment, name='init_course_payment'),
    path('<slug:slug>/pay/verify/', views.verify_course_payment, name='verify_course_payment'),
    path('pay/webhook/', views.paystack_webhook, name='paystack_webhook'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/learn/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('<slug:course_slug>/complete-all/', views.mark_all_complete, name='mark_all_complete'),
]
