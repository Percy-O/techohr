from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Comment, Tag
from users.decorators import staff_required
from django.contrib import messages
from .forms import PostForm, CommentForm
from django.utils.text import slugify
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
import uuid

User = get_user_model()

def post_list(request):
    search_query = request.GET.get('q')
    if search_query:
        posts = Post.objects.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).filter(published_at__lte=timezone.now()).distinct().order_by('-published_at')
    else:
        posts = Post.objects.filter(published_at__lte=timezone.now()).order_by('-published_at')
    
    categories = Category.objects.all()
    recent_posts = Post.objects.filter(published_at__lte=timezone.now()).order_by('-published_at')[:5]
    tags = Tag.objects.all()
    return render(request, 'blog/post_list.html', {
        'posts': posts, 
        'categories': categories, 
        'search_query': search_query,
        'recent_posts': recent_posts,
        'tags': tags
    })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published_at__lte=timezone.now())
    comments = post.comments.filter(active=True)
    new_comment = None
    
    # Related posts logic: same category or tags, exclude current
    related_posts = Post.objects.filter(
        Q(category=post.category) | Q(tags__in=post.tags.all())
    ).exclude(id=post.id).filter(published_at__lte=timezone.now()).distinct()[:3]

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            messages.success(request, 'Your comment has been submitted and is awaiting moderation.')
            return redirect('post_detail', slug=post.slug)
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'related_posts': related_posts
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, published_at__lte=timezone.now()).order_by('-published_at')
    categories = Category.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'categories': categories, 'current_category': category})

def author_posts(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author, published_at__lte=timezone.now()).order_by('-published_at')
    categories = Category.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts, 'categories': categories, 'current_author': author})

@staff_required
def manage_posts(request):
    posts = Post.objects.all().order_by('-published_at')
    return render(request, 'blog/manage_posts.html', {'posts': posts})

@staff_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Handle status from buttons
            if request.POST.get('save_draft') == 'true':
                post.status = 'draft'
            elif request.POST.get('publish') == 'true':
                post.status = 'published'
            # else keep form value or default
            
            post.save()
            
            # Handle Tags
            tags_input = form.cleaned_data.get('tags_input', '')
            if tags_input:
                tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
                for tag_name in tag_names:
                    # Logic to ensure unique slug for tags
                    tag = Tag.objects.filter(name=tag_name).first()
                    if not tag:
                        slug = slugify(tag_name)
                        if not slug: # Handle cases where slugify returns empty string (e.g. symbols)
                            slug = f"tag-{uuid.uuid4().hex[:8]}"
                        
                        original_slug = slug
                        counter = 1
                        while Tag.objects.filter(slug=slug).exists():
                            slug = f"{original_slug}-{counter}"
                            counter += 1
                        tag = Tag.objects.create(name=tag_name, slug=slug)
                    post.tags.add(tag)
            
            messages.success(request, f'Post {"saved as draft" if post.status == "draft" else "published"} successfully!')
            return redirect('manage_posts')
    else:
        # If POST request but invalid form, show error message
        if request.method == 'POST':
             messages.error(request, 'Please correct the errors below.')
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create Post'})

@staff_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # Handle status from buttons
            if request.POST.get('save_draft') == 'true':
                post.status = 'draft'
            elif request.POST.get('publish') == 'true':
                post.status = 'published'
            
            post.save()
            
            # Handle Tags (Clear existing and re-add)
            post.tags.clear()
            tags_input = form.cleaned_data.get('tags_input', '')
            if tags_input:
                tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
                for tag_name in tag_names:
                    # Logic to ensure unique slug for tags
                    tag = Tag.objects.filter(name=tag_name).first()
                    if not tag:
                        slug = slugify(tag_name)
                        if not slug:
                            slug = f"tag-{uuid.uuid4().hex[:8]}"
                        
                        original_slug = slug
                        counter = 1
                        while Tag.objects.filter(slug=slug).exists():
                            slug = f"{original_slug}-{counter}"
                            counter += 1
                        tag = Tag.objects.create(name=tag_name, slug=slug)
                    post.tags.add(tag)
            
            messages.success(request, 'Post updated successfully!')
            return redirect('manage_posts')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post'})

@staff_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, 'Post deleted successfully!')
    return redirect('manage_posts')

@staff_required
def manage_categories(request):
    categories = Category.objects.all().order_by('name')
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        
        if name:
            if not slug:
                slug = slugify(name)
            
            # Ensure slug is unique
            original_slug = slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
                
            Category.objects.create(name=name, slug=slug)
            messages.success(request, 'Category created successfully!')
            return redirect('manage_categories')
    return render(request, 'blog/manage_categories.html', {'categories': categories})

@staff_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('manage_categories')

@staff_required
def manage_comments(request):
    comments = Comment.objects.all().order_by('-created_at')
    return render(request, 'blog/manage_comments.html', {'comments': comments})

@staff_required
def approve_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.active = True
    comment.save()
    messages.success(request, 'Comment approved successfully!')
    return redirect('manage_comments')

@staff_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    messages.success(request, 'Comment deleted successfully!')
    return redirect('manage_comments')

@staff_required
@require_POST
def reply_comment(request, pk):
    parent_comment = get_object_or_404(Comment, pk=pk)
    body = request.POST.get('body')
    
    if body:
        Comment.objects.create(
            post=parent_comment.post,
            parent=parent_comment,
            name=request.user.username if request.user.username else "Admin", # Fallback if empty
            email=request.user.email,
            body=body,
            active=True # Admin replies are auto-approved
        )
        messages.success(request, 'Reply posted successfully!')
    else:
        messages.error(request, 'Reply content cannot be empty.')
        
    return redirect('manage_comments')

@staff_required
def post_preview(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # We don't save to DB, just render template with this instance
            # Need to handle tags manually for display if needed, but since it's not saved, M2M won't work easily.
            # For preview, we can just show what we have.
            
            # Mock tags for template
            tags_input = form.cleaned_data.get('tags_input', '')
            mock_tags = []
            if tags_input:
                tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
                for name in tag_names:
                    mock_tags.append({'name': name})
            
            return render(request, 'blog/post_detail.html', {
                'post': post,
                'comments': [],
                'new_comment': None,
                'comment_form': CommentForm(),
                'related_posts': [],
                'preview_mode': True,
                'mock_tags': mock_tags
            })
    return redirect('create_post')

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

@staff_required
@require_POST
def create_category_ajax(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'success': False, 'error': 'Category name is required'})
        
        category = Category.objects.filter(name=name).first()
        created = False
        if not category:
            slug = slugify(name)
            if not slug:
                slug = f"cat-{uuid.uuid4().hex[:8]}"
            
            original_slug = slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            category = Category.objects.create(name=name, slug=slug)
            created = True
        
        return JsonResponse({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name
            },
            'created': created
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_required
@require_POST
def create_tag_ajax(request):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        if not name:
            return JsonResponse({'success': False, 'error': 'Tag name is required'})
            
        tag = Tag.objects.filter(name=name).first()
        created = False
        if not tag:
            slug = slugify(name)
            if not slug:
                slug = f"tag-{uuid.uuid4().hex[:8]}"
            
            original_slug = slug
            counter = 1
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            tag = Tag.objects.create(name=name, slug=slug)
            created = True
        
        return JsonResponse({
            'success': True,
            'tag': {
                'id': tag.id,
                'name': tag.name
            },
            'created': created
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
