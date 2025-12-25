import os
import uuid
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import SiteSettings
from email.mime.image import MIMEImage

def send_html_email(subject, template_name, context, recipient_list, from_email=None, request=None, attachments=None, fail_silently=False):
    """
    Sends an HTML email with the brand logo embedded as a CID attachment.
    This ensures the logo is visible even on localhost or offline.
    
    attachments: List of tuples (filename, content, mimetype)
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    # Get Site Settings
    site_settings = SiteSettings.objects.first()
    context['site_settings'] = site_settings
    
    # Determine Logo Logic
    logo_path = None
    logo_cid = None
    # Use a unique ID to prevent caching issues
    logo_content_id = f'brand_logo_{uuid.uuid4().hex[:8]}'
    
    if site_settings:
        # Prefer main logo, then light, then dark
        logo_field = site_settings.logo or site_settings.logo_light or site_settings.logo_dark
        if logo_field:
            try:
                logo_path = logo_field.path
                if os.path.exists(logo_path):
                    logo_cid = logo_content_id
            except Exception:
                pass
    
    # Always try to generate absolute URL as fallback (though template prefers CID)
    if request:
        try:
            base_url = request.build_absolute_uri('/')[:-1]
            if site_settings:
                # Use the same field logic as CID
                logo_field_url = site_settings.logo or site_settings.logo_light or site_settings.logo_dark
                if logo_field_url:
                    context['logo_url'] = f"{base_url}{logo_field_url.url}"
        except Exception:
            pass

    # Pass CID to template
    if logo_cid:
        context['logo_cid'] = logo_cid

    # Render Template
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    # Create Email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    email.mixed_subtype = 'related' # Critical for inline images

    # Attach Logo File
    if logo_path and logo_cid:
        try:
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
            
            logo = MIMEImage(logo_data)
            logo.add_header('Content-ID', f'<{logo_cid}>')
            logo.add_header('Content-Disposition', 'inline', filename='logo.png')
            email.attach(logo)
        except Exception as e:
            print(f"Error attaching logo to email: {e}")

    # Attach other files
    if attachments:
        for attachment in attachments:
            # Expecting (filename, content, mimetype)
            email.attach(*attachment)

    # Send
    return email.send(fail_silently=fail_silently)
