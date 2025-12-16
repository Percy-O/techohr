from django.shortcuts import render, get_object_or_404, redirect
from .models import Service, Project, Testimonial, Contact, Newsletter
from blog.models import Post
from courses.models import Course, Enrollment
from django.contrib import messages
from django.views.decorators.http import require_POST
from users.decorators import staff_required
from .forms import ProjectForm, TestimonialForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

def home(request):
    services = Service.objects.all()[:6] # Increased to 6 for the grid
    projects = Project.objects.filter(featured=True)[:3]
    testimonials = Testimonial.objects.all().order_by('-id')[:3]
    latest_posts = Post.objects.filter(status='published').order_by('-published_at')[:4]
    
    # Featured/Latest Courses
    courses = Course.objects.filter(is_published=True).order_by('-created_at')[:3]
    
    # Check enrollment status for each course if user is authenticated
    if request.user.is_authenticated:
        for course in courses:
            course.is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    return render(request, 'core/home.html', {
        'services': services,
        'projects': projects,
        'testimonials': testimonials,
        'latest_posts': latest_posts,
        'courses': courses
    })

def service_list(request):
    services = Service.objects.all()
    return render(request, 'core/service_list.html', {'services': services})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    return render(request, 'core/service_detail.html', {'service': service})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        Contact.objects.create(name=name, email=email, subject=subject, message=message)
        
        # Send Email Notification
        try:
            dashboard_url = request.build_absolute_uri(reverse('manage_messages'))
            html_message = render_to_string('emails/contact_notification.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'dashboard_url': dashboard_url
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=f'New Contact Message: {subject}',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL], # Send to admin (using default from for now)
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            # Log error if needed, but don't stop user flow
            print(f"Error sending email: {e}")

        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
        
    return render(request, 'core/contact.html')

def about(request):
    return render(request, 'core/about.html')

@require_POST
def subscribe(request):
    email = request.POST.get('email')
    if email:
        if Newsletter.objects.filter(email=email).exists():
            messages.info(request, 'You are already subscribed to our newsletter.', extra_tags='newsletter')
        else:
            Newsletter.objects.create(email=email)
            messages.success(request, 'Thank you for subscribing to our newsletter!', extra_tags='newsletter')
    else:
        messages.error(request, 'Please provide a valid email address.', extra_tags='newsletter')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def portfolio(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'core/portfolio.html', {'projects': projects})

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'core/project_detail.html', {'project': project})

# --- Management Views ---

from django.core.paginator import Paginator

@staff_required
def manage_projects(request):
    project_list = Project.objects.all().order_by('-created_at')
    paginator = Paginator(project_list, 5) # Show 5 projects per page.
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    return render(request, 'core/manage_projects.html', {'projects': projects})

@staff_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project created successfully!')
            return redirect('manage_projects')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form, 'title': 'Create Project'})

@staff_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('manage_projects')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {'form': form, 'title': 'Edit Project'})

@staff_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Project deleted successfully!')
    return redirect('manage_projects')

@staff_required
def manage_messages(request):
    contact_list = Contact.objects.all().order_by('-created_at')
    paginator = Paginator(contact_list, 5) # Show 5 messages per page.
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)
    return render(request, 'core/manage_messages.html', {'contacts': contacts})

@staff_required
def delete_message(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    messages.success(request, 'Message deleted successfully!')
    return redirect('manage_messages')

@staff_required
def manage_testimonials(request):
    testimonial_list = Testimonial.objects.all().order_by('-id')
    paginator = Paginator(testimonial_list, 5) # Show 5 testimonials per page.
    page_number = request.GET.get('page')
    testimonials = paginator.get_page(page_number)
    return render(request, 'core/manage_testimonials.html', {'testimonials': testimonials})

@staff_required
def create_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial created successfully!')
            return redirect('manage_testimonials')
    else:
        form = TestimonialForm()
    return render(request, 'core/testimonial_form.html', {'form': form, 'title': 'Create Testimonial'})

@staff_required
def edit_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial updated successfully!')
            return redirect('manage_testimonials')
    else:
        form = TestimonialForm(instance=testimonial)
    return render(request, 'core/testimonial_form.html', {'form': form, 'title': 'Edit Testimonial'})

@staff_required
def delete_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.delete()
    messages.success(request, 'Testimonial deleted successfully!')
    return redirect('manage_testimonials')
