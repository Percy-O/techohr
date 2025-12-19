from .models import SiteSettings, CompanyStats

def site_settings(request):
    settings_obj = SiteSettings.objects.first()
    stats_obj = CompanyStats.objects.first()
    return {
        'site_settings': settings_obj,
        'company_stats': stats_obj,
    }
