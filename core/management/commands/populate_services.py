from django.core.management.base import BaseCommand
from core.models import Service
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populates the database with initial services'

    def handle(self, *args, **kwargs):
        services = [
            {
                "title": "Web Development",
                "icon": "fas fa-laptop-code",
                "short_description": "Custom responsive websites tailored to capture your brand identity and audience.",
                "content": "We build high-performance, SEO-optimized websites using the latest technologies. Whether you need a simple landing page or a complex web application, our team delivers solutions that are fast, secure, and scalable.",
                "features": "Responsive Design\nSEO Optimization\nFast Loading Speed\nCustom Functionality"
            },
            {
                "title": "Software Development (SaaS)",
                "icon": "fas fa-layer-group",
                "short_description": "Scalable SaaS models built with security and reliability in mind.",
                "content": "We develop robust Software as a Service (SaaS) platforms that are scalable, secure, and user-friendly. From multi-tenant architectures to subscription management, we handle it all.",
                "features": "Multi-tenancy\nSubscription Billing\nCloud Infrastructure\nAPI-first Design"
            },
            {
                "title": "Data Analysis & Data Science",
                "icon": "fas fa-chart-line",
                "short_description": "Turn your data into actionable insights for smarter decision making.",
                "content": "Unlock the power of your data with our advanced analytics and data science services. We help you visualize trends, predict outcomes, and make data-driven decisions.",
                "features": "Data Visualization\nPredictive Analytics\nBusiness Intelligence\nBig Data Processing"
            },
            {
                "title": "AI Integration & AI Agents",
                "icon": "fas fa-robot",
                "short_description": "Cutting-edge AI solutions to automate workflows and enhance customer experiences.",
                "content": "Leverage the power of Artificial Intelligence to automate tasks, improve customer support with chatbots, and optimize business processes using custom AI agents.",
                "features": "Custom Chatbots\nProcess Automation\nNLP Integration\nMachine Learning Models"
            },
            {
                "title": "UI/UX Design",
                "icon": "fas fa-pencil-ruler",
                "short_description": "Intuitive and beautiful user interfaces that delight users and improve retention.",
                "content": "Our design team creates user-centric designs that are both beautiful and functional. We focus on user experience (UX) to ensure your product is intuitive and easy to use.",
                "features": "User Research\nWireframing & Prototyping\nVisual Design\nUsability Testing"
            },
            {
                "title": "Mobile App Development",
                "icon": "fas fa-mobile-alt",
                "short_description": "Native and cross-platform mobile applications for iOS and Android.",
                "content": "Reach your customers on the go with our mobile app development services. We build high-quality iOS and Android apps using React Native and Flutter.",
                "features": "Cross-platform Development\nNative Performance\nOffline Capabilities\nPush Notifications"
            },
            {
                "title": "API Integration",
                "icon": "fas fa-network-wired",
                "short_description": "Seamlessly connect your software with third-party services and data sources.",
                "content": "We connect your disparate systems to ensure seamless data flow. Whether it's payment gateways, CRMs, or custom internal APIs, we ensure robust integrations.",
                "features": "RESTful & GraphQL APIs\nSecure Authentication\nReal-time Data Sync\nThird-party Connectors"
            }
        ]

        for service_data in services:
            slug = slugify(service_data["title"])
            service, created = Service.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": service_data["title"],
                    "icon": service_data["icon"],
                    "short_description": service_data["short_description"],
                    "content": service_data["content"],
                    "features": service_data["features"]
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created service: {service.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Service already exists: {service.title}'))
