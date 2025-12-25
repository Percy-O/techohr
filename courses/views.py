from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from users.decorators import staff_required
from .models import Course, Lesson, Enrollment, Module, LessonCompletion, Certificate, Category, Review, CertificateSettings, Assessment, Question, Choice, Submission, StudentAnswer
from .forms import CourseForm, ModuleForm, LessonForm, CertificateSettingsForm, ReviewForm, AssessmentForm, QuestionForm, ChoiceForm, SubmissionForm, SubmissionGradingForm
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from django.http import JsonResponse, HttpResponse, FileResponse
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import hmac
import hashlib
from django.http import HttpResponse
from urllib.error import HTTPError, URLError
from django.urls import reverse
from core.models import SiteSettings
from .models import Payment
import uuid
from fpdf import FPDF
import io
import os
from PIL import Image, ImageDraw, ImageEnhance # Import PIL
import json
from urllib import request as urlrequest, parse as urlparse
import time
import tempfile
from .utils import generate_certificate_pdf_bytes, send_certificate_email
from core.utils import send_html_email

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None

@staff_required
def create_module_assessment(request, module_pk):
    module = get_object_or_404(Module, pk=module_pk)
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course = module.course
            assessment.module = module
            assessment.save()
            messages.success(request, 'Assessment created successfully!')
            return redirect('manage_modules', course_pk=module.course.pk)
    else:
        form = AssessmentForm()
    return render(request, 'courses/assessment_form.html', {'form': form, 'module': module, 'title': 'Add Assessment to Module'})

@staff_required
def create_course_assessment(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course = course
            assessment.module = None # Course level
            assessment.save()
            messages.success(request, 'Course Assessment created successfully!')
            return redirect('manage_courses') # Or edit_course
    else:
        form = AssessmentForm()
    return render(request, 'courses/assessment_form.html', {'form': form, 'course': course, 'title': 'Add Course Assessment'})

@staff_required
def edit_assessment(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assessment updated successfully!')
            if assessment.module:
                return redirect('manage_modules', course_pk=assessment.course.pk)
            else:
                return redirect('manage_courses')
    else:
        form = AssessmentForm(instance=assessment)
    return render(request, 'courses/assessment_form.html', {'form': form, 'assessment': assessment, 'title': 'Edit Assessment'})

@staff_required
def delete_assessment(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    course_pk = assessment.course.pk
    module_pk = assessment.module.pk if assessment.module else None
    assessment.delete()
    messages.success(request, 'Assessment deleted successfully!')
    if module_pk:
        return redirect('manage_modules', course_pk=course_pk)
    return redirect('manage_courses')

@staff_required
def manage_assessment_questions(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    if request.method == 'POST':
        if 'create_question' in request.POST:
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.assessment = assessment
                question.save()
                messages.success(request, 'Question added successfully!')
                return redirect('manage_assessment_questions', pk=pk)
        elif 'delete_question' in request.POST:
            question_id = request.POST.get('question_id')
            Question.objects.filter(id=question_id, assessment=assessment).delete()
            messages.success(request, 'Question deleted successfully!')
            return redirect('manage_assessment_questions', pk=pk)
            
    question_form = QuestionForm()
    questions = assessment.questions.all()
    return render(request, 'courses/manage_questions.html', {'assessment': assessment, 'questions': questions, 'question_form': question_form})

@staff_required
def manage_question_choices(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        if 'create_choice' in request.POST:
            form = ChoiceForm(request.POST)
            if form.is_valid():
                choice = form.save(commit=False)
                choice.question = question
                choice.save()
                messages.success(request, 'Choice added successfully!')
                return redirect('manage_question_choices', pk=pk)
        elif 'delete_choice' in request.POST:
            choice_id = request.POST.get('choice_id')
            Choice.objects.filter(id=choice_id, question=question).delete()
            messages.success(request, 'Choice deleted successfully!')
            return redirect('manage_question_choices', pk=pk)
            
    choice_form = ChoiceForm()
    choices = question.choices.all()
    return render(request, 'courses/manage_choices.html', {'question': question, 'choices': choices, 'choice_form': choice_form})

@login_required
def submit_assessment(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    # Check enrollment
    if not Enrollment.objects.filter(student=request.user, course=assessment.course).exists():
        messages.error(request, 'You must be enrolled to take this assessment.')
        return redirect('course_detail', slug=assessment.course.slug)

    # Check if already submitted
    submission = Submission.objects.filter(assessment=assessment, student=request.user).first()
    if submission:
        return render(request, 'courses/submission_detail.html', {'submission': submission, 'assessment': assessment})

    if request.method == 'POST':
        if assessment.assessment_type == 'assignment':
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.assessment = assessment
                submission.student = request.user
                submission.save()
                messages.success(request, 'Assignment submitted successfully!')
                return redirect('course_detail', slug=assessment.course.slug)
        elif assessment.assessment_type == 'quiz':
            # Handle quiz submission
            submission = Submission.objects.create(assessment=assessment, student=request.user)
            score = 0
            total_points = 0
            
            for question in assessment.questions.all():
                total_points += question.points
                
                if question.question_type == 'text':
                    text_answer = request.POST.get(f'question_{question.id}')
                    if text_answer:
                        StudentAnswer.objects.create(
                            submission=submission,
                            question=question,
                            text_answer=text_answer,
                            is_correct=False, # Needs manual grading
                            points_awarded=0
                        )
                else:
                    selected_choice_id = request.POST.get(f'question_{question.id}')
                    if selected_choice_id:
                        try:
                            choice = Choice.objects.get(id=selected_choice_id, question=question)
                            is_correct = choice.is_correct
                            points_awarded = question.points if is_correct else 0
                            score += points_awarded
                            
                            StudentAnswer.objects.create(
                                submission=submission,
                                question=question,
                                selected_choice=choice,
                                is_correct=is_correct,
                                points_awarded=points_awarded
                            )
                        except Choice.DoesNotExist:
                            pass
            
            submission.score = score
            # Auto-grade if purely multiple choice? Yes.
            submission.save()
            messages.success(request, f'Quiz submitted! You scored {score}/{total_points}.')
            return redirect('course_detail', slug=assessment.course.slug)
    else:
        if assessment.assessment_type == 'assignment':
            form = SubmissionForm()
            return render(request, 'courses/take_assignment.html', {'form': form, 'assessment': assessment})
        else:
            # Quiz view
            questions = assessment.questions.all()
            return render(request, 'courses/take_quiz.html', {'assessment': assessment, 'questions': questions})

@staff_required
def manage_submissions(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    submissions = assessment.submissions.all().order_by('-submitted_at')
    return render(request, 'courses/manage_submissions.html', {'assessment': assessment, 'submissions': submissions})

@staff_required
def manage_payments(request):
    payments = Payment.objects.all().order_by('-paid_at')
    status = request.GET.get('status')
    if status:
        payments = payments.filter(status=status)
    query = request.GET.get('q')
    if query:
        payments = payments.filter(reference__icontains=query)
    return render(request, 'courses/manage_payments.html', {'payments': payments})

@staff_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    if request.method == 'POST':
        form = SubmissionGradingForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.save()
            messages.success(request, 'Submission graded successfully!')
            return redirect('manage_submissions', pk=submission.assessment.pk)
    else:
        form = SubmissionGradingForm(instance=submission)
    return render(request, 'courses/grade_submission.html', {'form': form, 'submission': submission})

@staff_required
def manage_certificate_settings(request):
    settings = CertificateSettings.objects.first()
    if not settings:
        settings = CertificateSettings() # Create ephemeral instance if none exists
    
    if request.method == 'POST':
        # If it doesn't exist in DB, create it
        if not settings.pk:
            form = CertificateSettingsForm(request.POST, request.FILES)
        else:
            form = CertificateSettingsForm(request.POST, request.FILES, instance=settings)
            
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificate settings updated successfully!')
            return redirect('manage_certificate_settings')
    else:
        if not settings.pk:
            form = CertificateSettingsForm()
        else:
            form = CertificateSettingsForm(instance=settings)
            
    return render(request, 'courses/manage_certificate_settings.html', {'form': form})

def course_list(request):
    courses = Course.objects.filter(is_published=True)
    categories = Category.objects.all().order_by('name')
    return render(request, 'courses/course_list.html', {'courses': courses, 'categories': categories})

def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            'assessments',
            'modules__lessons',
            'modules__assessments'
        ),
        slug=slug
    )
    is_enrolled = False
    progress = 0
    
    completed_lesson_ids = []
    certificate = None
    resume_lesson = None
    submissions_map = {}
    
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        if enrollment:
            is_enrolled = True
            progress = enrollment.get_progress()
            completed_lesson_ids = LessonCompletion.objects.filter(
                enrollment=enrollment, 
                is_completed=True
            ).values_list('lesson_id', flat=True)
            
            # Fetch submissions for this user and course
            user_submissions = Submission.objects.filter(student=request.user, assessment__course=course)
            submissions_map = {sub.assessment_id: sub for sub in user_submissions}
            
            # Find the first uncompleted lesson to resume
            for module in course.modules.all():
                for lesson in module.lessons.all():
                    if lesson.id not in completed_lesson_ids:
                        resume_lesson = lesson
                        break
                if resume_lesson:
                    break
            
            # If all completed or none started, default to first lesson
            if not resume_lesson:
                first_module = course.modules.first()
                if first_module:
                    resume_lesson = first_module.lessons.first()
            
            if progress == 100 and course.has_certificate:
                certificate = Certificate.objects.filter(student=request.user, course=course).first()

    # Prepare Assessment Objects with Submissions Attached
    # Course Level
    course_assessments = []
    for assessment in course.assessments.all():
        if not assessment.module: # Only course level
            assessment.user_submission = submissions_map.get(assessment.id)
            course_assessments.append(assessment)

    # Module Level
    modules_list = []
    for module in course.modules.all():
        # Attach submission to each assessment in the module
        module_assessments = []
        for assessment in module.assessments.all():
            assessment.user_submission = submissions_map.get(assessment.id)
            module_assessments.append(assessment)
        
        module.prefetched_assessments = module_assessments
        modules_list.append(module)

    # Reviews
    reviews = course.reviews.all().order_by('-created_at')
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        
    review_form = ReviewForm()

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'progress': progress,
        'completed_lesson_ids': completed_lesson_ids,
        'certificate': certificate,
        'resume_lesson': resume_lesson,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
        'course_assessments': course_assessments,
        'modules': modules_list,
    })

@login_required
def init_course_payment(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if course.price <= 0:
        return redirect('enroll_course', slug=slug)

    if not django_settings.PAYSTACK_SECRET_KEY or django_settings.PAYSTACK_SECRET_KEY == 'PAYSTACK_SECRET_KEY':
        messages.error(request, 'Payment not configured. Please set PAYSTACK keys.')
        return redirect('course_payment', slug=slug)

    # Ensure positive integer amount in kobo
    amount_kobo = int(max(float(course.current_price), 0) * 100)
    if amount_kobo <= 0:
        messages.error(request, 'Invalid course amount. Please contact support.')
        return redirect('course_payment', slug=slug)
    callback_url = request.build_absolute_uri(
        reverse('verify_course_payment', kwargs={'slug': slug})
    )
    payload = {
        'email': request.user.email or 'noemail@techohr.com.ng',
        'amount': amount_kobo,
        'currency': 'NGN',
        'callback_url': callback_url,
        'metadata': {
            'course_slug': slug,
            'user_id': request.user.id,
            'username': request.user.username,
        }
    }
    data = json.dumps(payload).encode('utf-8')
    req = urlrequest.Request(
        'https://api.paystack.co/transaction/initialize',
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {django_settings.PAYSTACK_SECRET_KEY}"
        },
        method='POST'
    )
    try:
        with urlrequest.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            res = json.loads(body)
            if res.get('status') and res.get('data', {}).get('authorization_url'):
                return render(request, 'courses/payment_init.html', {
                    'course': course,
                    'authorization_url': res['data']['authorization_url'],
                    'amount_naira': float(course.current_price),
                })
            # Show Paystack error message if available
            err_msg = res.get('message') or 'Unable to initialize payment. Please try again.'
            messages.error(request, err_msg)
    except HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            err_json = json.loads(err_body)
            err_msg = err_json.get('message') or 'Payment initialization failed.'
            messages.error(request, err_msg)
        except Exception:
            messages.error(request, 'Payment initialization failed. Please try again later.')
        return redirect('course_payment', slug=slug)
    except URLError:
        messages.error(request, 'Network error contacting Paystack. Check your internet and try again.')
        return redirect('course_payment', slug=slug)
    except Exception:
        messages.error(request, 'Payment initialization failed. Please try again later.')
        return redirect('course_payment', slug=slug)
    return redirect('course_payment', slug=slug)

@login_required
def verify_course_payment(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, 'Payment verification failed: missing reference.')
        return redirect('course_detail', slug=slug)
    # Retry verification a few times to allow Paystack to finalize the transaction
    attempts = 6
    last_error_message = None
    for i in range(attempts):
        verify_req = urlrequest.Request(
            f'https://api.paystack.co/transaction/verify/{urlparse.quote(reference)}',
            headers={'Authorization': f"Bearer {django_settings.PAYSTACK_SECRET_KEY}"},
            method='GET'
        )
        try:
            with urlrequest.urlopen(verify_req) as resp:
                body = resp.read().decode('utf-8')
                res = json.loads(body)
                data = res.get('data') or {}
                status_val = str(data.get('status') or '').lower()
                if res.get('status') and (status_val == 'success' or status_val == 'successful'):
                    try:
                        Payment.objects.get_or_create(
                            reference=data.get('reference') or reference or '',
                            defaults={
                                'user': request.user,
                                'course': course,
                                'amount': data.get('amount') or 0,
                                'status': data.get('status') or 'success',
                                'raw': data,
                            }
                        )
                    except Exception:
                        pass
                    if not Enrollment.objects.filter(student=request.user, course=course).exists():
                        Enrollment.objects.create(student=request.user, course=course)
                        
                        # Only send email on new enrollment to prevent duplicates
                        try:
                            site_settings = SiteSettings.objects.first()
                            
                            amount_naira = (data.get('amount') or 0) / 100.0
                            
                            context = {
                                'user': request.user,
                                'course': course,
                                'reference': data.get('reference') or reference,
                                'amount_naira': amount_naira,
                                'status': data.get('status'),
                                'paid_at': data.get('paid_at') or timezone.now(),
                                'start_url': request.build_absolute_uri(reverse('course_detail', kwargs={'slug': slug})),
                            }
                            
                            send_html_email(
                                subject=f'Payment Receipt - {course.title}',
                                template_name='emails/payment_receipt.html',
                                context=context,
                                recipient_list=[request.user.email],
                                request=request
                            )
                        except Exception:
                            pass
                    messages.success(request, f'Payment successful. You are now enrolled in {course.title}.')
                    first_module = course.modules.first()
                    if first_module:
                        first_lesson = first_module.lessons.first()
                        if first_lesson:
                            return redirect('lesson_detail', course_slug=course.slug, lesson_slug=first_lesson.slug)
                    return redirect('course_detail', slug=slug)
                # Record message and retry if status not success
                last_error_message = res.get('message') or (data.get('gateway_response') if isinstance(data, dict) else None) or 'Payment not successful or pending.'
        except HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                err_json = json.loads(err_body)
                last_error_message = err_json.get('message') or 'Payment verification error.'
            except Exception:
                last_error_message = 'Payment verification error.'
        except URLError:
            last_error_message = 'Network error contacting Paystack during verification.'
        except Exception:
            last_error_message = 'Payment verification failed due to an unexpected error.'
        # Wait before next attempt (incremental backoff)
        time.sleep(i + 1)
    try:
        payment = Payment.objects.filter(reference=reference).first()
        if payment and str(payment.status).lower() in ('success', 'successful'):
            if not Enrollment.objects.filter(student=request.user, course=course).exists():
                Enrollment.objects.create(student=request.user, course=course)
            messages.success(request, f'Payment confirmed. You are now enrolled in {course.title}.')
            first_module = course.modules.first()
            if first_module:
                first_lesson = first_module.lessons.first()
                if first_lesson:
                    return redirect('lesson_detail', course_slug=course.slug, lesson_slug=first_lesson.slug)
            return redirect('course_detail', slug=slug)
    except Exception:
        pass
    messages.error(request, last_error_message or 'Payment verification failed. Please contact support.')
    return redirect('course_detail', slug=slug)

@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    # For paid courses, force payment before enrollment
    if course.current_price and float(course.current_price) > 0:
        messages.info(request, 'Please complete payment to access this course.')
        return redirect('course_payment', slug=slug)

@login_required
def course_payment(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    if course.price <= 0:
        return redirect('enroll_course', slug=slug)
    keys_ready = bool(django_settings.PAYSTACK_PUBLIC_KEY and django_settings.PAYSTACK_PUBLIC_KEY != 'PAYSTACK_PUBLIC_KEY' and django_settings.PAYSTACK_SECRET_KEY and django_settings.PAYSTACK_SECRET_KEY != 'PAYSTACK_SECRET_KEY')
    try:
        amount_kobo = int(Decimal(str(course.price)) * 100)
    except Exception:
        amount_kobo = int(float(course.price) * 100)
    return render(request, 'courses/course_payment.html', {
        'course': course,
        'amount_naira': float(course.price),
        'amount_kobo': amount_kobo,
        'keys_ready': keys_ready,
        'public_key': django_settings.PAYSTACK_PUBLIC_KEY if keys_ready else '',
    })

    # Check if already enrolled
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f"You have successfully enrolled in {course.title}!")
    
    # Redirect to the first lesson
    first_module = course.modules.first()
    if first_module:
        first_lesson = first_module.lessons.first()
        if first_lesson:
            return redirect('lesson_detail', course_slug=course.slug, lesson_slug=first_lesson.slug)
            
    # Fallback if no lessons found
    messages.info(request, "Course content is coming soon.")
    return redirect('course_detail', slug=slug)

@csrf_exempt
def paystack_webhook(request):
    try:
        body = request.body
        signature = request.headers.get('X-Paystack-Signature') or request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
        if not signature:
            return HttpResponse(status=400)
        computed = hmac.new(
            key=django_settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            msg=body,
            digestmod=hashlib.sha512
        ).hexdigest()
        if not hmac.compare_digest(computed, signature):
            return HttpResponse(status=401)
        payload = json.loads(body.decode('utf-8'))
        data = payload.get('data') or {}
        status_val = str(data.get('status') or '').lower()
        reference = data.get('reference')
        amount = data.get('amount') or 0
        course_slug = (data.get('metadata') or {}).get('course_slug')
        user_id = (data.get('metadata') or {}).get('user_id')
        if status_val in ('success', 'successful') and reference:
            try:
                course = Course.objects.filter(slug=course_slug).first()
                user = None
                if user_id:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.filter(id=user_id).first()
                Payment.objects.get_or_create(
                    reference=reference,
                    defaults={
                        'user': user,
                        'course': course,
                        'amount': amount,
                        'status': status_val,
                        'raw': data,
                    }
                )
                if user and course and not Enrollment.objects.filter(student=user, course=course).exists():
                    Enrollment.objects.create(student=user, course=course)
                    
                    # Send Payment Receipt Email via Webhook
                    try:
                        amount_naira = (data.get('amount') or 0) / 100.0
                        
                        # Construct Start URL (Harder in webhook without request context, but we can try)
                        # We can use the domain from SiteSettings if available or fallback
                        start_url = reverse('course_detail', kwargs={'slug': course.slug})
                        # Ideally prepend domain, but send_html_email handles relative URLs? No, it needs absolute for buttons usually.
                        # Let's try to get domain from request or settings.
                        domain = request.get_host() 
                        protocol = 'https' if request.is_secure() else 'http'
                        full_start_url = f"{protocol}://{domain}{start_url}"

                        context = {
                            'user': user,
                            'course': course,
                            'reference': reference,
                            'amount_naira': amount_naira,
                            'status': status_val,
                            'paid_at': data.get('paid_at') or timezone.now(),
                            'start_url': full_start_url,
                        }
                        
                        send_html_email(
                            subject=f'Payment Receipt - {course.title}',
                            template_name='emails/payment_receipt.html',
                            context=context,
                            recipient_list=[user.email],
                            request=request 
                        )
                    except Exception as e:
                        print(f"Webhook email error: {e}")
                        pass
            except Exception:
                pass
        return HttpResponse(status=200)
    except Exception:
        return HttpResponse(status=400)

@staff_required
def manage_courses(request):
    courses = Course.objects.all().order_by('-created_at')
    total_courses = courses.count()
    published_courses = courses.filter(is_published=True).count()
    draft_courses = courses.filter(is_published=False).count()
    
    context = {
        'courses': courses,
        'total_courses': total_courses,
        'published_courses': published_courses,
        'draft_courses': draft_courses,
    }
    return render(request, 'courses/manage_courses.html', context)

@staff_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('manage_courses')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Create Course'})

@staff_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('manage_courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Edit Course'})

@staff_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, 'Course deleted successfully!')
    return redirect('manage_courses')

@staff_required
def manage_course_categories(request):
    categories = Category.objects.all().order_by('name')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            slug = slugify(name)
            # Ensure unique slug
            if not slug:
                slug = f"cat-{uuid.uuid4().hex[:8]}"
            original_slug = slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            Category.objects.create(name=name, slug=slug)
            messages.success(request, 'Category created successfully!')
            return redirect('manage_course_categories')
    return render(request, 'courses/manage_categories.html', {'categories': categories})

@staff_required
def delete_course_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('manage_course_categories')

@staff_required
def manage_enrollments(request):
    enrollments = Enrollment.objects.all().order_by('-enrolled_at')
    return render(request, 'courses/manage_enrollments.html', {'enrollments': enrollments})

@staff_required
def manage_certificates(request):
    certificates = Certificate.objects.all().order_by('-issued_at')
    return render(request, 'courses/manage_certificates.html', {'certificates': certificates})

@staff_required
def manage_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'courses/manage_reviews.html', {'reviews': reviews})

@staff_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, 'Review deleted successfully!')
    return redirect('manage_reviews')

@login_required
def add_review(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'You must be enrolled to review this course.')
        return redirect('course_detail', slug=slug)
        
    # Check if already reviewed
    if Review.objects.filter(user=request.user, course=course).exists():
        messages.error(request, 'You have already reviewed this course.')
        return redirect('course_detail', slug=slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.course = course
            review.user = request.user
            review.save()
            messages.success(request, 'Review added successfully!')
        else:
            messages.error(request, 'Error adding review. Please check the form.')
            
    return redirect('course_detail', slug=slug)


@staff_required
def manage_modules(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        if 'create_module' in request.POST:
            title = request.POST.get('title')
            if title:
                Module.objects.create(course=course, title=title, order=course.modules.count() + 1)
                messages.success(request, 'Module added successfully!')
                return redirect('manage_modules', course_pk=course.pk)
    
    return render(request, 'courses/manage_modules.html', {'course': course})

@staff_required
def edit_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated successfully!')
            return redirect('manage_modules', course_pk=module.course.pk)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'courses/module_form.html', {'form': form, 'module': module})

@staff_required
def delete_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    course_pk = module.course.pk
    module.delete()
    messages.success(request, 'Module deleted successfully!')
    return redirect('manage_modules', course_pk=course_pk)

@staff_required
def create_lesson(request, module_pk):
    module = get_object_or_404(Module, pk=module_pk)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Lesson created successfully!')
            return redirect('manage_modules', course_pk=module.course.pk)
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form, 'module': module, 'title': 'Add Lesson'})

@staff_required
def edit_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully!')
            return redirect('manage_modules', course_pk=lesson.module.course.pk)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form, 'module': lesson.module, 'title': 'Edit Lesson'})

@staff_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course_pk = lesson.module.course.pk
    lesson.delete()
    messages.success(request, 'Lesson deleted successfully!')
    return redirect('manage_modules', course_pk=course_pk)

@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, module__course=course, slug=lesson_slug)
    
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    # Require payment/enrollment for paid courses, regardless of free flag
    if (course.price and float(course.price) > 0) and not enrollment:
        messages.error(request, 'Please pay for the course to access lessons.')
        return redirect('course_detail', slug=course_slug)
    # For free courses, still require enrollment unless lesson is marked free
    if not enrollment and not (course.price and float(course.price) <= 0 and lesson.is_free):
        messages.error(request, 'You must be enrolled to view this lesson.')
        return redirect('course_detail', slug=course_slug)

    # Check completion
    is_completed = False
    completed_lesson_ids = []
    if enrollment:
        is_completed = LessonCompletion.objects.filter(enrollment=enrollment, lesson=lesson, is_completed=True).exists()
        completed_lesson_ids = LessonCompletion.objects.filter(
            enrollment=enrollment, 
            is_completed=True
        ).values_list('lesson_id', flat=True)

    # Get next/prev lesson logic could go here
    
    return render(request, 'courses/lesson_detail.html', {
        'course': course, 
        'lesson': lesson,
        'is_completed': is_completed,
        'enrollment': enrollment,
        'completed_lesson_ids': completed_lesson_ids
    })

@login_required
def mark_lesson_complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.module.course)
    
    completion, created = LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    completion.is_completed = True
    completion.save()
    
    # Check if course is completed
    progress = enrollment.get_progress()
    if progress == 100 and not enrollment.is_completed:
        enrollment.is_completed = True
        enrollment.completed_at = timezone.now()
        enrollment.save()
        
        # Generate Certificate
        if lesson.module.course.has_certificate:
            cert, created = Certificate.objects.get_or_create(student=request.user, course=lesson.module.course)
            if created:
                send_certificate_email(cert, request)
            messages.success(request, 'Congratulations! You have completed the course and earned a certificate.')
    
    messages.success(request, 'Lesson marked as complete!')
    return redirect('lesson_detail', course_slug=lesson.module.course.slug, lesson_slug=lesson.slug)

@login_required
def mark_all_complete(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    lessons = Lesson.objects.filter(module__course=course)
    
    for lesson in lessons:
        LessonCompletion.objects.get_or_create(enrollment=enrollment, lesson=lesson, defaults={'is_completed': True})
        
    # Update enrollment status
    enrollment.is_completed = True
    enrollment.completed_at = timezone.now()
    enrollment.save()
    
    # Generate Certificate if applicable
    if course.has_certificate:
        cert, created = Certificate.objects.get_or_create(student=request.user, course=course)
        if created:
            send_certificate_email(cert, request)
        messages.success(request, 'Congratulations! You have completed the course and earned a certificate.')
    else:
        messages.success(request, 'All lessons marked as complete!')
        
    return redirect('course_detail', slug=course.slug)

@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id, student=request.user)
    
    # Static Assets Paths
    static_images_path = os.path.join(django_settings.BASE_DIR, 'static', 'images')
    corners_path = os.path.join(static_images_path, 'certificate_corners.png')
    seal_path = os.path.join(static_images_path, 'gold_seal.png')
    
    # Colors
    DARK_BLUE = (25, 55, 90)   # Brightened Dark Blue
    LIGHT_BLUE = (100, 180, 255) # Light Blue for inner border
    GRAY = (100, 100, 100)
    
    # Get Settings for Logo & Colors
    settings = CertificateSettings.objects.first()
    
    # Use settings colors if available
    primary_color = DARK_BLUE
    secondary_color = DARK_BLUE
    accent_color = DARK_BLUE
    
    if settings:
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
        if settings.primary_color: primary_color = hex_to_rgb(settings.primary_color)
        if settings.secondary_color: secondary_color = hex_to_rgb(settings.secondary_color)
        if settings.accent_color: accent_color = hex_to_rgb(settings.accent_color)
        
    # Create Dynamic Background with Watermark
    temp_bg_path = None
    try:
        # 1. Create White Canvas (High Res for Print Quality, scaled down for PDF if needed)
        # A4 @ 96 DPI is approx 1123x794. Let's use 2000x1414 for good quality.
        bg_width, bg_height = 2000, 1414
        background = Image.new('RGBA', (bg_width, bg_height), (255, 255, 255, 255))
        
        # 2. Tile Faint Logo
        if settings and settings.logo:
            try:
                logo = Image.open(settings.logo.path).convert('RGBA')
                # Resize logo to be small (e.g., 100px width)
                logo_w = 150
                aspect = logo.height / logo.width
                logo_h = int(logo_w * aspect)
                resampling_attr = getattr(Image, 'Resampling', None)
                resample_filter = resampling_attr.LANCZOS if resampling_attr else getattr(Image, 'LANCZOS', Image.ANTIALIAS)
                logo = logo.resize((logo_w, logo_h), resample_filter)
                
                # Make logo faint (Opacity)
                # Create a new image with alpha channel adjusted
                # Easy way: split alpha, multiply by factor, merge back
                r, g, b, alpha = logo.split()
                alpha = alpha.point(lambda p: p * 0.08) # 8% opacity (Reduced from 15%)
                logo.putalpha(alpha)
                
                # Tile it
                # Spacing - "No space at all" means spacing equals dimensions
                space_x = logo_w 
                space_y = logo_h
                
                # Diagonal tiling or grid? Grid is simpler.
                for y in range(0, bg_height, space_y):
                    for x in range(0, bg_width, space_x):
                        # Offset every other row
                        offset = (space_x // 2) if (y // space_y) % 2 == 1 else 0
                        background.alpha_composite(logo, (x + offset, y))
            except Exception as e:
                print(f"Error processing watermark logo: {e}")
        else:
             print("No logo found in settings for watermark.")

        # 3. Draw Borders and Corners (Programmatically)
        try:
            draw = ImageDraw.Draw(background)
            
            # Dimensions
            margin = 50
            outer_border_width = 20
            gap = 5
            inner_border_width = 8
            
            # Outer Border (Dark Blue)
            # Note: In PIL, width draws inside the bounding box
            draw.rectangle(
                [margin, margin, bg_width - margin, bg_height - margin],
                outline=DARK_BLUE,
                width=outer_border_width
            )
            
            # Inner Border (Light Blue)
            inner_offset = margin + outer_border_width + gap
            draw.rectangle(
                [inner_offset, inner_offset, bg_width - inner_offset, bg_height - inner_offset],
                outline=LIGHT_BLUE,
                width=inner_border_width
            )
            
            # Corner Graphics (Decorative L-shapes)
            corner_length = 200
            corner_width = 25
            corner_offset = margin - 15 
            
            # Helper to draw thick lines
            def draw_corner(start, end, width, color):
                draw.line([start, end], fill=color, width=width)
                
            # Top-Left
            draw_corner((corner_offset, corner_offset), (corner_offset + corner_length, corner_offset), corner_width, DARK_BLUE)
            draw_corner((corner_offset, corner_offset), (corner_offset, corner_offset + corner_length), corner_width, DARK_BLUE)
            
            # Top-Right
            draw_corner((bg_width - corner_offset - corner_length, corner_offset), (bg_width - corner_offset, corner_offset), corner_width, DARK_BLUE)
            draw_corner((bg_width - corner_offset, corner_offset), (bg_width - corner_offset, corner_offset + corner_length), corner_width, DARK_BLUE)
            
            # Bottom-Left
            draw_corner((corner_offset, bg_height - corner_offset), (corner_offset + corner_length, bg_height - corner_offset), corner_width, DARK_BLUE)
            draw_corner((corner_offset, bg_height - corner_offset - corner_length), (corner_offset, bg_height - corner_offset), corner_width, DARK_BLUE)

            # Bottom-Right
            draw_corner((bg_width - corner_offset - corner_length, bg_height - corner_offset), (bg_width - corner_offset, bg_height - corner_offset), corner_width, DARK_BLUE)
            draw_corner((bg_width - corner_offset, bg_height - corner_offset - corner_length), (bg_width - corner_offset, bg_height - corner_offset), corner_width, DARK_BLUE)
            
        except Exception as e:
            print(f"Error drawing borders: {e}")

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            temp_bg_path = tmp.name
        background.save(temp_bg_path)
        
    except Exception as e:
        print(f"Error creating dynamic background: {e}")

    # Create PDF
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    font_path = os.path.join(django_settings.BASE_DIR, 'static', 'fonts')
    try:
        if os.path.exists(os.path.join(font_path, 'GreatVibes-Regular.ttf')):
            pdf.add_font('GreatVibes', '', os.path.join(font_path, 'GreatVibes-Regular.ttf'))
        if os.path.exists(os.path.join(font_path, 'Lato-Regular.ttf')):
            pdf.add_font('Lato', '', os.path.join(font_path, 'Lato-Regular.ttf'))
        if os.path.exists(os.path.join(font_path, 'Lato-Bold.ttf')):
            pdf.add_font('Lato', 'B', os.path.join(font_path, 'Lato-Bold.ttf'))
    except Exception as e:
        print(f"Font loading error: {e}")
    family_script = 'GreatVibes' if os.path.exists(os.path.join(font_path, 'GreatVibes-Regular.ttf')) else 'Helvetica'
    family_sans = 'Lato' if os.path.exists(os.path.join(font_path, 'Lato-Regular.ttf')) else 'Helvetica'
    family_sans_bold = 'Lato' if os.path.exists(os.path.join(font_path, 'Lato-Bold.ttf')) else 'Helvetica'

    pdf.add_page()
    
    # 1. Background (Dynamic)
    if temp_bg_path and os.path.exists(temp_bg_path):
        try:
            pdf.image(temp_bg_path, x=0, y=0, w=297, h=210)
        except Exception as e:
            print(f"Error loading background: {e}")
            
    # Clean up temp background immediately? No, wait until end or use try/finally block logic.
    # We'll clean up at the end of the view.

    # 2. Main Logo (Top Center)
    if settings and settings.logo:
        try:
            logo_path = settings.logo.path
            # Center the logo at the top
            pdf.image(logo_path, x=123.5, y=10, w=50) # x = (297-50)/2 = 123.5
        except Exception as e:
            print(f"Error loading logo: {e}")

    # 3. Title: "Certificate of Completion"
    # Font: Sans-Bold (Lato-Bold)
    pdf.set_font(family_sans_bold, 'B' if family_sans_bold != 'Helvetica' else 'B', 42)
    pdf.set_text_color(*primary_color)
    pdf.set_y(50) # Shifted down (was 45)
    pdf.cell(0, 15, 'Certificate of Completion', align='C')
    
    # 4. Subtitle: "THIS IS TO CERTIFY THAT"
    pdf.set_font(family_sans, '', 10)
    pdf.set_text_color(*secondary_color) # Keep uniform color or slightly lighter
    pdf.set_y(67) # Shifted down (was 62)
    pdf.cell(0, 10, 'THIS IS TO CERTIFY THAT', align='C')
    
    # 5. Student Name
    # Font: Script (GreatVibes)
    pdf.set_font(family_script, '', 48)
    pdf.set_text_color(*primary_color)
    pdf.set_y(80) # Shifted down (was 75)
    student_name = certificate.student.get_full_name() or certificate.student.username
    pdf.cell(0, 20, student_name, align='C')
    
    # Line under name
    text_width = pdf.get_string_width(student_name)
    # Ensure line is at least somewhat wide
    line_width = max(text_width + 20, 100)
    start_x = (297 - line_width) / 2
    pdf.set_draw_color(*accent_color)
    pdf.set_line_width(0.5)
    pdf.line(start_x, 100, start_x + line_width, 100) # Shifted down (was 95)
    
    # 6. "HAS SUCCESSFULLY COMPLETED"
    pdf.set_font(family_sans_bold, 'B' if family_sans_bold != 'Helvetica' else 'B', 8)
    pdf.set_text_color(*secondary_color)
    pdf.set_y(105) # Shifted down (was 100)
    pdf.cell(0, 10, 'HAS SUCCESSFULLY COMPLETED', align='C')
    
    # 7. Course Name
    pdf.set_font(family_sans, '', 24)
    pdf.set_text_color(*primary_color)
    pdf.set_y(120) # Shifted down (was 115)
    pdf.cell(0, 15, certificate.course.title.upper(), align='C')
    
    # 8. Bottom Section (Date, Seal, Signature)
    bottom_y = 165 # Shifted down (was 160)
    
    # Seal (Center)
    if os.path.exists(seal_path):
        # Center x = 297/2 = 148.5
        # Width 30 => x = 133.5
        pdf.image(seal_path, x=133.5, y=bottom_y - 10, w=30)
        
    # Date (Left)
    pdf.set_xy(40, bottom_y)
    pdf.set_font(family_sans_bold, 'B' if family_sans_bold != 'Helvetica' else 'B', 12)
    pdf.set_text_color(*secondary_color)
    pdf.cell(60, 5, certificate.issued_at.strftime('%B %d, %Y').upper(), align='C')
    
    # Date Line
    pdf.set_draw_color(*accent_color)
    pdf.line(40, bottom_y + 6, 100, bottom_y + 6)
    
    # Date Label
    pdf.set_xy(40, bottom_y + 8)
    pdf.set_font(family_sans_bold, 'B' if family_sans_bold != 'Helvetica' else 'B', 8)
    pdf.cell(60, 5, 'DATE OF COMPLETION', align='C')
    
    # Signature (Right)
    settings = CertificateSettings.objects.first() # Still get settings for signature
    if settings and settings.signature:
        try:
            sig_path = settings.signature.path
            
            # Calculate dimensions to fit in box above line
            # Line is at bottom_y + 6.
            # Available space above line: Let's say 30 units max height.
            # Max width: 50 units (to stay centered within 200-260)
            
            max_w = 50
            max_h = 25
            line_y = bottom_y + 6
            
            # Use PIL to get dimensions
            with Image.open(sig_path) as sig_img:
                img_w, img_h = sig_img.size
                aspect = img_h / img_w
                
                # Try fitting by width first
                target_w = max_w
                target_h = target_w * aspect
                
                # If height is too big, fit by height
                if target_h > max_h:
                    target_h = max_h
                    target_w = target_h / aspect
                    
                # Calculate position to center horizontally and align bottom to line
                # Center x of line is 230
                pos_x = 230 - (target_w / 2)
                # Position y so bottom touches line_y - padding (e.g. 1 unit)
                pos_y = line_y - target_h - 1
                
                pdf.image(sig_path, x=pos_x, y=pos_y, w=target_w, h=target_h)
                
        except Exception as e:
            print(f"Error loading signature: {e}")
            
    # Signature Line
    pdf.set_draw_color(*accent_color)
    pdf.line(200, bottom_y + 6, 260, bottom_y + 6)
    
    # Signature Label
    pdf.set_xy(200, bottom_y + 8)
    pdf.set_font(family_sans_bold, 'B' if family_sans_bold != 'Helvetica' else 'B', 8)
    pdf.cell(60, 5, 'SIGNATURE', align='C')

    # Instructor Name (Below Signature)
    pdf.set_xy(200, bottom_y + 13)
    instructor_name = certificate.course.instructor.get_full_name() or certificate.course.instructor.username
    pdf.set_font(family_sans_bold, 'B' if family_sans_bold != 'Helvetica' else 'B', 10)
    pdf.set_text_color(*secondary_color)
    pdf.cell(60, 5, instructor_name, align='C')
    pdf.set_xy(200, bottom_y + 18)
    pdf.set_font(family_sans, '', 8)
    pdf.cell(60, 5, 'INSTRUCTOR', align='C')
    
    # 9. Barcode (Below Seal)
    if barcode:
        try:
            options = {
                'write_text': False,
                'module_height': 5.0, 
                'quiet_zone': 1.0,
                'font_size': 0,
                'text_distance': 0,
            }
            code = barcode.get('code128', certificate.certificate_id, writer=ImageWriter())
            tmp_base = os.path.join(tempfile.gettempdir(), f"barcode_{certificate.certificate_id}")
            barcode_path = code.save(tmp_base, options=options)
            
            # Position below seal
            pdf.image(barcode_path, x=123.5, y=bottom_y + 25, w=50, h=10)
            
            # Clean up
            try:
                if os.path.exists(barcode_path):
                    os.remove(barcode_path)
            except:
                pass
        except Exception as e:
            print(f"Barcode error: {e}")

    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1')
    buffer = io.BytesIO(pdf_bytes)
    
    # Cleanup Temp File
    if temp_bg_path and os.path.exists(temp_bg_path):
        try:
            os.remove(temp_bg_path)
        except:
            pass
            
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f"attachment; filename=certificate_{certificate.certificate_id}.pdf"
    response['Content-Length'] = str(len(pdf_bytes))
    return response
