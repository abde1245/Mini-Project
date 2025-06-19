from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db import models

# Dummy model to show "Reports" in admin index
class ReportEntry(models.Model):
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        managed = False  # No DB table

class ReportEntryAdmin(admin.ModelAdmin):
    change_list_template = "admin/reporting/report_index.html"
    def changelist_view(self, request, extra_context=None):
        # Add links to all reports
        return TemplateResponse(request, "admin/reporting/report_index.html", {})

#admin.site.register(ReportEntry, ReportEntryAdmin)

# Custom admin views for reports
def overall_duty_summary(request):
    return TemplateResponse(request, "admin/reporting/overall_duty_summary.html", {})

def user_activity_logs(request):
    return TemplateResponse(request, "admin/reporting/user_activity_logs.html", {})

def ta_performance_overview(request):
    return TemplateResponse(request, "admin/reporting/ta_performance_overview.html", {})

def professor_ta_performance(request):
    return TemplateResponse(request, "admin/reporting/professor_ta_performance.html", {})

def professor_schedule_summary(request):
    return TemplateResponse(request, "admin/reporting/professor_schedule_summary.html", {})

def professor_duty_completion_rate(request):
    return TemplateResponse(request, "admin/reporting/duty_completion_rate.html", {}) # Corrected template name

# Add these to admin URLs
def get_report_urls():
    return [
        path('reports/overall-duty-summary/', admin.site.admin_view(overall_duty_summary), name='overall-duty-summary'),
        path('reports/user-activity-logs/', admin.site.admin_view(user_activity_logs), name='user-activity-logs'),
        path('reports/ta-performance-overview/', admin.site.admin_view(ta_performance_overview), name='ta-performance-overview'),
        path('reports/professor/ta-performance/', admin.site.admin_view(professor_ta_performance), name='professor-ta-performance'),
        path('reports/professor/schedule-summary/', admin.site.admin_view(professor_schedule_summary), name='professor-schedule-summary'),
        path('reports/professor/duty-completion-rate/', admin.site.admin_view(professor_duty_completion_rate), name='professor-duty-completion-rate'),
    ]

# Store the original get_urls method
original_get_urls = admin.site.get_urls

# Define a new get_urls function that includes report URLs
def custom_admin_get_urls():
    urls = get_report_urls()  # Get the report-specific URLs
    urls += original_get_urls() # Add the original admin URLs
    return urls

# Patch admin URLs with the new function
admin.site.get_urls = custom_admin_get_urls