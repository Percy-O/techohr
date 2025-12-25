from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, AdminCreationForm, CustomPasswordChangeForm
from django.contrib.auth.decorators import login_required
from .decorators import staff_required
from courses.models import Enrollment, Course, Certificate
from core.models import Service, Project, Contact, Newsletter
from blog.models import Post
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from core.models import SiteSettings
from core.models import PageVisit
from django.urls import reverse
from core.utils import send_html_email

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate until confirmed
            user.is_student = True
            user.save()
            
            # Send Confirmation Email to Student
            current_site = get_current_site(request)
            subject = 'Activate Your TechOhr Account'
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activate_url = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )
            
            context = {
                'user': user,
                'domain': current_site.domain,
                'activate_url': activate_url,
            }
            
            email_sent = False
            try:
                send_html_email(
                    subject=subject,
                    template_name='emails/student_confirmation.html',
                    context=context,
                    recipient_list=[user.email],
                    request=request
                )
                email_sent = True
            except Exception as e:
                print(f"Error sending confirmation email: {e}")
                messages.error(request, f"Error sending confirmation email. Please contact support. ({e})")
                
            # Send Notification Email to Admin (only if student email sent, or regardless?)
            # Let's try to send admin email regardless, but don't show error to user for this one.
            try:
                dashboard_url = request.build_absolute_uri(reverse('manage_users'))
                
                admin_context = {
                    'user': user,
                    'dashboard_url': dashboard_url,
                }
                
                send_html_email(
                    subject=f'New Student Registration: {user.username}',
                    template_name='emails/admin_new_student.html',
                    context=admin_context,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    request=request
                )
            except Exception as e:
                print(f"Error sending admin notification: {e}")

            if email_sent:
                messages.success(request, 'Registration successful. Please check your email to confirm and activate your account.')
                return render(request, 'users/register_success.html')
            else:
                # If email failed, redirect to login (error message already added)
                return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been confirmed! Welcome to TechOhr.')
        return redirect('home')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('home')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            messages.warning(request, "You are not authorized to access the admin panel.")
            return redirect('dashboard')
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, f'Welcome back, Admin {username}!')
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Access denied. Staff privileges required.')
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/admin_login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

@login_required
def dashboard(request):
    # Fetch all enrollments for the user
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    active_courses = []
    completed_courses = []
    
    for enrollment in enrollments:
        # Calculate progress dynamically
        progress = enrollment.get_progress()
        enrollment.current_progress = progress # Attach to object for template
        
        # Check if course is completed (either by flag or 100% progress)
        if enrollment.is_completed or progress == 100:
            completed_courses.append(enrollment)
        else:
            active_courses.append(enrollment)
            
    # Fetch certificates
    certificates = Certificate.objects.filter(student=request.user).select_related('course')
    
    context = {
        'active_courses': active_courses,
        'completed_courses': completed_courses,
        'certificates': certificates,
        'total_enrolled': enrollments.count(),
        'total_active': len(active_courses),
        'total_completed': len(completed_courses),
        'total_certificates': certificates.count(),
    }
    return render(request, 'users/dashboard.html', context)

@staff_required
def admin_dashboard(request):
    # Stats
    total_users = User.objects.count()
    total_projects = Project.objects.count()
    total_courses = Course.objects.count()
    total_posts = Post.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_certificates = Certificate.objects.count()

    # Trends (last 7 days vs previous 7 days)
    from datetime import timedelta, date
    from django.utils import timezone
    now = timezone.now()
    start = now - timedelta(days=7)
    prev_start = now - timedelta(days=14)
    prev_end = start

    def pct_change(prev, current):
        if prev == 0:
            return 100 if current > 0 else 0
        return int(round(((current - prev) / prev) * 100))

    users_week = User.objects.filter(date_joined__gte=start).count()
    users_prev = User.objects.filter(date_joined__gte=prev_start, date_joined__lt=prev_end).count()
    users_week_change = pct_change(users_prev, users_week)

    projects_week_new = Project.objects.filter(created_at__gte=start).count()
    courses_week_new = Course.objects.filter(created_at__gte=start).count()
    posts_week_new = Post.objects.filter(published_at__gte=start).count()

    # Page Visit Trend (daily/weekly/monthly/yearly toggle)
    trend_type = request.GET.get('trend_type', 'daily')
    visit_trend_labels = []
    visit_trend_values = []

    if trend_type == 'daily':
        for i in range(6, -1, -1):
            day = (now - timedelta(days=i)).date()
            visit_trend_labels.append(day.strftime('%a'))
            visit_trend_values.append(
                PageVisit.objects.filter(visited_at__date=day).count()
            )
    elif trend_type == 'weekly':
        for i in range(4, -1, -1):
            week_start = (now - timedelta(weeks=i)) - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
            visit_trend_labels.append(f"Week {week_start.strftime('%W')}")
            visit_trend_values.append(
                PageVisit.objects.filter(visited_at__range=[week_start, week_end]).count()
            )
    elif trend_type == 'monthly':
        current_year = now.year
        current_month = now.month
        months = []
        for i in range(11, -1, -1):
            m = current_month - i
            y = current_year
            while m <= 0:
                m += 12
                y -= 1
            months.append((y, m))
        for y, m in months:
            visit_trend_labels.append(date(y, m, 1).strftime('%b'))
            visit_trend_values.append(
                PageVisit.objects.filter(visited_at__year=y, visited_at__month=m).count()
            )
    elif trend_type == 'yearly':
        for i in range(4, -1, -1):
            y = now.year - i
            visit_trend_labels.append(str(y))
            visit_trend_values.append(
                PageVisit.objects.filter(visited_at__year=y).count()
            )
    else:
        for i in range(6, -1, -1):
            day = (now - timedelta(days=i)).date()
            visit_trend_labels.append(day.strftime('%a'))
            visit_trend_values.append(
                PageVisit.objects.filter(visited_at__date=day).count()
            )

    # Recent Data
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_contacts = Contact.objects.order_by('-created_at')[:5]
    recent_subscribers = Newsletter.objects.order_by('-subscribed_at')[:5]
    recent_enrollments = Enrollment.objects.order_by('-enrolled_at')[:5]

    context = {
        'total_users': total_users,
        'total_projects': total_projects,
        'total_courses': total_courses,
        'total_posts': total_posts,
        'total_enrollments': total_enrollments,
        'total_certificates': total_certificates,
        'recent_users': recent_users,
        'recent_contacts': recent_contacts,
        'recent_subscribers': recent_subscribers,
        'recent_enrollments': recent_enrollments,
        # KPIs
        'users_week_change': users_week_change,
        'projects_week_new': projects_week_new,
        'courses_week_new': courses_week_new,
        'posts_week_new': posts_week_new,
        # Chart data
        'visit_trend_labels': visit_trend_labels,
        'visit_trend_values': visit_trend_values,
        'current_trend_type': trend_type,
    }
    return render(request, 'users/admin_dashboard.html', context)

from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash

@staff_required
def manage_users(request):
    user_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(user_list, 5) # Show 5 users per page.
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    return render(request, 'users/manage_users.html', {'users': users})

@staff_required
def create_admin_user(request):
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True
            user.save()
            messages.success(request, 'Admin user created successfully!')
            return redirect('manage_users')
    else:
        form = AdminCreationForm()
    return render(request, 'users/admin_user_form.html', {'form': form, 'title': 'Create Admin User'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated.')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

@staff_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot delete a superuser.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('manage_users')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})

@staff_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        user.is_active = False
        messages.warning(request, f"User {user.username} has been deactivated.")
    else:
        user.is_active = True
        messages.success(request, f"User {user.username} has been activated.")
    user.save()
    return redirect('manage_users')
