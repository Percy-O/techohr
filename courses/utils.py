import os
import io
import tempfile
import uuid
from PIL import Image, ImageDraw
from fpdf import FPDF
from django.conf import settings as django_settings
from .models import CertificateSettings

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None

def generate_certificate_pdf_bytes(certificate):
    # Static Assets Paths
    static_images_path = os.path.join(django_settings.BASE_DIR, 'static', 'images')
    corners_path = os.path.join(static_images_path, 'certificate_corners.png')
    seal_path = os.path.join(static_images_path, 'gold_seal.png')
    
    # Colors
    DARK_BLUE = (25, 55, 90)   # Brightened Dark Blue
    LIGHT_BLUE = (100, 180, 255) # Light Blue for inner border
    
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
    # settings already retrieved above
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
        
    # Cleanup Temp File
    if temp_bg_path and os.path.exists(temp_bg_path):
        try:
            os.remove(temp_bg_path)
        except:
            pass
            
    return pdf_bytes

from django.core.mail import EmailMessage

def send_certificate_email(certificate):
    try:
        pdf_bytes = generate_certificate_pdf_bytes(certificate)
        user = certificate.student
        course = certificate.course
        
        email = EmailMessage(
            subject=f'Certificate of Completion - {course.title}',
            body=f'Congratulations {user.get_full_name() or user.username}!\n\nYou have successfully completed the course "{course.title}".\n\nPlease find your certificate attached.',
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach(f'certificate_{certificate.certificate_id}.pdf', pdf_bytes, 'application/pdf')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending certificate email: {e}")
        return False
