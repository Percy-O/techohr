from django.contrib import admin
from .models import Category, Course, Module, Lesson, Enrollment, Review, Certificate, LessonCompletion, CertificateSettings, Assessment, Question, Choice, Submission, StudentAnswer
from .models import Payment, PaymentSettings

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'paystack_public_key', 'stripe_public_key')
    
    def has_add_permission(self, request):
        # Allow adding only if no instance exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'module', 'assessment_type', 'max_score', 'due_date')
    list_filter = ('assessment_type', 'course')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'assessment', 'question_type', 'points')
    list_filter = ('assessment', 'question_type')
    inlines = [ChoiceInline]

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'score', 'submitted_at')
    list_filter = ('assessment', 'submitted_at')
    search_fields = ('student__username', 'assessment__title')

@admin.register(CertificateSettings)
class CertificateSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'updated_at')
    
    def has_add_permission(self, request):
        # Allow adding only if no instance exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    inlines = [LessonInline]

class ModuleInlineForCourse(admin.StackedInline):
    model = Module
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'level', 'is_published', 'created_at')
    list_filter = ('is_published', 'level', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInlineForCourse]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'get_progress')
    list_filter = ('course', 'enrolled_at', 'is_completed')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'course')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'issued_at', 'certificate_id')
    list_filter = ('course', 'issued_at')
    search_fields = ('student__username', 'certificate_id')

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed_at', 'is_completed')
    list_filter = ('is_completed', 'completed_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'reference', 'amount', 'status', 'paid_at')
    list_filter = ('status', 'course')
    search_fields = ('reference', 'user__username', 'course__title')
