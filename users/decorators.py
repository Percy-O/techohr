from django.contrib.auth.decorators import user_passes_test

def staff_required(view_func):
    decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='admin_login'
    )
    return decorator(view_func)
