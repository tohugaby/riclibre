"""
This code is a copy from https://djangosnippets.org/snippets/10539/ for template and
https://gist.github.com/aaugustin/1388243 for Admin class
"""

from django.contrib import admin


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """Disables all editing capabilities."""
    change_form_template = "admin/view.html"
    actions = None

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.method in ['GET', 'HEAD'] and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False
