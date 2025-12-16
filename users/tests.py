from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment, Category

User = get_user_model()

class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='teststudent', password='password', is_student=True)
        self.instructor = User.objects.create_user(username='instructor', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.course = Course.objects.create(
            title='Test Course', 
            slug='test-course', 
            instructor=self.instructor, 
            description='Test Description',
            category=self.category,
            is_published=True
        )
        self.enrollment = Enrollment.objects.create(student=self.user, course=self.course)

    def test_dashboard_access(self):
        self.client.login(username='teststudent', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/dashboard.html')
        self.assertIn('active_courses', response.context)
        self.assertIn('completed_courses', response.context)
        self.assertIn('certificates', response.context)
        self.assertEqual(len(response.context['active_courses']), 1)
