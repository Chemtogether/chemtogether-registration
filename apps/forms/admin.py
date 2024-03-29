import logging

from csv import writer
from mimetypes import guess_type
from os.path import join
from datetime import datetime
from io import BytesIO, StringIO

from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.urls import reverse, re_path
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext, gettext_lazy as _

from .forms import EntriesForm
from .models import Form, Field, FormEntry, FieldEntry
from .settings import CSV_DELIMITER, UPLOAD_ROOT
from .utils import now, slugify


logger = logging.getLogger("ct_registration.forms_builder.admin")

fs = FileSystemStorage(location=UPLOAD_ROOT)
form_admin_filter_horizontal = ()
form_admin_fieldsets = [
    (None, {"fields": ("title", "slug", "status", ("publish_date", "expiry_date",), "intro", "description")}),
    (_("Email"), {"fields": ("send_email_to_company", "send_email_to_staff", "email_copies", "email_subject", "email_message")}),]

class FieldAdmin(admin.TabularInline):
    model = Field
    exclude = ('slug', 'visible', 'order')


class FormAdmin(admin.ModelAdmin):
    formentry_model = FormEntry
    fieldentry_model = FieldEntry

    inlines = (FieldAdmin,)
    list_display = ("title", "status", "publish_date", "expiry_date", "total_entries", "admin_links")
    list_display_links = ("title",)
    list_editable = ("status", "publish_date", "expiry_date")
    list_filter = ("status",)
    filter_horizontal = form_admin_filter_horizontal
    search_fields = ("title", "description")
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = form_admin_fieldsets

    def get_queryset(self, request):
        """
        Annotate the queryset with the entries count for use in the
        admin list view.
        """
        qs = super(FormAdmin, self).get_queryset(request)
        return qs.annotate(total_entries=Count("entries"))

    def get_urls(self):
        """
        Add the entries view to urls.
        """
        urls = super(FormAdmin, self).get_urls()
        extra_urls = [
            re_path("^(?P<form_id>\d+)/entries/$",
                self.admin_site.admin_view(self.entries_view),
                name="form_entries"),
            re_path("^(?P<form_id>\d+)/entries/show/$",
                self.admin_site.admin_view(self.entries_view),
                {"show": True}, name="form_entries_show"),
            re_path("^(?P<form_id>\d+)/entries/export/$",
                self.admin_site.admin_view(self.entries_view),
                {"export": True}, name="form_entries_export"),
            re_path("^file/(?P<field_entry_id>\d+)/$",
                self.admin_site.admin_view(self.file_view),
                name="form_file"),
        ]
        return extra_urls + urls

    def entries_view(self, request, form_id, show=False, export=False):
        """
        Displays the form entries in a HTML table with option to
        export as CSV file.
        """
        if request.POST.get("back"):
            bits = (self.model._meta.app_label, self.model.__name__.lower())
            change_url = reverse("admin:%s_%s_change" % bits, args=(form_id,))
            return HttpResponseRedirect(change_url)
        form = get_object_or_404(self.model, id=form_id)
        post = request.POST or None
        args = form, request, self.formentry_model, self.fieldentry_model, post
        entries_form = EntriesForm(*args)
        delete = "%s.delete_formentry" % self.formentry_model._meta.app_label
        can_delete_entries = request.user.has_perm(delete)
        submitted = entries_form.is_valid() or show or export
        export = export or request.POST.get("export")
        form_entries = FormEntry.objects.filter(form=form).all().order_by("-entry_time")


        if submitted:
            if export:
                response = HttpResponse(content_type="text/csv")
                fname = "%s-%s.csv" % (form.slug, slugify(now().ctime()))
                attachment = "attachment; filename=%s" % fname
                response["Content-Disposition"] = attachment
                queue = StringIO()
                try:
                    csv = writer(queue, delimiter=CSV_DELIMITER)
                    writerow = csv.writerow
                except TypeError:
                    queue = BytesIO()
                    delimiter = bytes(CSV_DELIMITER, encoding="utf-8")
                    csv = writer(queue, delimiter=delimiter)
                    writerow = lambda row: csv.writerow([c.encode("utf-8")
                        if hasattr(c, "encode") else c for c in row])
                writerow(entries_form.columns())
                for row in entries_form.rows(csv=True):
                    writerow(row)
                data = queue.getvalue()
                response.write(data)
                return response
            
            elif request.POST.get("delete") and can_delete_entries:
                selected = request.POST.getlist("selected")
                logger.debug(selected)
                if selected:
                    try:
                        from django.contrib.messages import info
                    except ImportError:
                        def info(request, message, fail_silently=True):
                            request.user.message_set.create(message=message)
                    entries = self.formentry_model.objects.filter(id__in=selected)
                    count = entries.count()
                    if count > 0:
                        entries.delete()
                        message = ungettext("1 entry deleted",
                                            "%(count)s entries deleted", count)
                        info(request, message % {"count": count})
        template = "admin/forms/entries.html"
        context = {"title": _("View Entries"), "entries_form": entries_form,
                   "opts": self.model._meta, "original": form, "form_entries": form_entries,
                   "can_delete_entries": can_delete_entries,
                   "submitted": submitted}
        return render(request, template, context)

    def file_view(self, request, field_entry_id):
        """
        Output the file for the requested field entry.
        """
        model = self.fieldentry_model
        field_entry = get_object_or_404(model, id=field_entry_id)
        path = join(fs.location, field_entry.value)
        response = HttpResponse(content_type=guess_type(path)[0])
        f = open(path, "r+b")
        response["Content-Disposition"] = "attachment; filename=%s" % f.name
        response.write(f.read())
        f.close()
        return response


admin.site.register(Form, FormAdmin)
