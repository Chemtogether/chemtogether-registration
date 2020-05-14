import json
import logging
import os

from django.utils import timezone
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template import RequestContext
from django.utils.http import urlquote
from django.utils.html import format_html, format_html_join, mark_safe, escape, strip_tags
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.core.files import File
from django.core.mail import EmailMessage
from django.template import Context
from django.template import Template
from django import forms

from .forms import FormForForm, FormEntry
from .models import Form, STATUS_DRAFT, STATUS_PUBLISHED
from .signals import form_invalid, form_valid
from .utils import split_choices
from . import fields


logger = logging.getLogger("ct_registration.forms_builder.views")


class FormDetail(TemplateView):

    template_name = "forms/detail.html"

    def get_context_data(self, **kwargs):
        context = super(FormDetail, self).get_context_data(**kwargs)
        published = Form.objects.published(for_user=self.request.user)
        context["form"] = get_object_or_404(published, slug=kwargs["slug"])
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if not request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, 'Please log in to view this form.')
            return redirect("login")
        if not (request.user.is_company_is_accepted() or request.user.is_staffmember()):
            messages.add_message(request, messages.WARNING, 'You are not allowed to view this form. If you believe this is an error, please contact us via email.')
            return redirect("/")
        if request.user.is_staffmember():
            messages.add_message(request, messages.INFO, 'You are logged in as a staff member. You may look at this form, but cannot submit it.')

        status_published = bool(FormEntry.objects.filter(author=request.user.company.get()).filter(form=context['form']).filter(status=STATUS_PUBLISHED).all())
        if context['form'].expiry_date:
            form_expired = timezone.now() > context['form'].expiry_date
            has_expiry = True
        else:
            form_expired = False
            has_expiry = False

        if has_expiry:
            if form_expired:
                messages.add_message(request, messages.WARNING, 'The submission deadline for this form has passed. You may still view your submission, but you cannot make any changes. If you want to change or submit anything, please contact us via email instead.')
            elif status_published:
                messages.add_message(request, messages.INFO, 'You have already submitted this form before. You may make any changes and resubmit it until the deadline has passed.')
            else:
                messages.add_message(request, messages.INFO, 'You have not submitted this form yet. Please fill out this form and submit it before the deadline. You may save any progress without submitting and continue editing later on.')
        else:
            if status_published:
                messages.add_message(request, messages.INFO, 'You have already submitted this form before. You may make any changes and resubmit it.')
            else:
                messages.add_message(request, messages.INFO, 'You have not submitted this form yet. Please fill out this form and submit it upon completion. You may save any progress without submitting and continue editing later on.')

        context['status_published'] = status_published
        context['form_expired'] = form_expired

        return self.render_to_response(context)



    def post(self, request, *args, **kwargs):
        published = Form.objects.published(for_user=request.user)
        form = get_object_or_404(published, slug=kwargs["slug"])
        form_for_form = FormForForm(form, RequestContext(request), request.POST or None, request.FILES or None)

        # kick out unwanted guests
        if not request.user.is_authenticated:
            messages.add_message(request, messages.WARNING, 'Please log in to view this form.')
            return redirect("login")
        if not request.user.is_company_is_accepted():
            messages.add_message(request, messages.WARNING, 'You are not allowed to submit this form. If you believe this is an error, please contact us.')
            return redirect("/")

        # check if form has expired
        if form.expiry_date and timezone.now() > form.expiry_date:
            messages.add_message(request, messages.ERROR, 'You cannot submit this form, as its deadline has passed.')
            return redirect("/")


        # check form status and alter form for validation if draft
        previous_published = bool(FormEntry.objects.filter(author=request.user.company.get()).filter(form=form).filter(status=STATUS_PUBLISHED).all())
        if 'save_draft' in request.POST and not previous_published:
            status = STATUS_DRAFT
            for field in form_for_form.fields:  # if it is a draft submission, remove the condition that all required entries are present
                form_for_form.fields[field].required = False
        else:
            status = STATUS_PUBLISHED

        previous_files = []
        if FormEntry.objects.filter(author=request.user.company.get()).filter(form=form).all():
            existing_fields = FormEntry.objects.filter(author=request.user.company.get()).filter(form=form).get().fields.all()

            for field in form.fields.all():
                if field.field_type == fields.FILE and field.slug in request.POST:
                    value = existing_fields.filter(field_id=field.id).get().value
                    previous_files.append({'slug': field.slug, 'id': field.id, 'value': value})
                    if value:
                        form_for_form.fields[field.slug].required = False

        if not form_for_form.is_valid():
            logger.debug("Form is invalid.")
            form_invalid.send(sender=request, form=form_for_form)
        else:
            # Attachments read must occur before model save, or seek() will fail on large uploads.
            attachments = []
            for f in form_for_form.files.values():
                f.seek(0)
                attachments.append((f.name, f.read()))

            try:
                FormEntry.objects.filter(author=request.user.company.get()).filter(form=form).all().delete()
            except:
                pass
            entry = form_for_form.save()

            for previous_file in previous_files:
                try:
                    entry.fields.filter(field_id=previous_file['id']).update(value=previous_file['value'])
                except Exception as e:
                    logger.error(e)

            # assign user and form status
            entry.author = request.user.company.get()
            entry.status = status
            entry.save()
            
            form_valid.send(sender=request, form=form_for_form, entry=entry)
            self.send_emails(request, form_for_form, form, entry, attachments)
            if not self.request.is_ajax():
                if status == STATUS_DRAFT:
                    messages.add_message(request, messages.INFO, 'Your form has been saved as a draft.')
                else:
                    messages.add_message(request, messages.INFO, 'Your form has been submitted.')
                return redirect('/')
        
        context = {"form": form, "form_for_form": form_for_form}
        return self.render_to_response(context)



    def render_to_response(self, context, **kwargs):
        if self.request.method == "POST" and self.request.is_ajax():
            json_context = json.dumps({
                "errors": context["form_for_form"].errors,
                "form": context["form_for_form"].as_p(),
                "message": context["form"].response,
            })
            if context["form_for_form"].errors:
                return HttpResponseBadRequest(json_context, content_type="application/json")
            return HttpResponse(json_context, content_type="application/json")
        return super(FormDetail, self).render_to_response(context, **kwargs)



    def send_emails(self, request, form_for_form, form, entry, attachments):

        if not form.send_email_to_company and not form.send_email_to_staff and not form.email_copies:
            return

        company = entry.author
        username = entry.author.email
        try:
            staff = company.staff_user
        except:
            staff = None

        to = []
        if form.send_email_to_company:
            to.append(company.email)
        if form.send_email_to_staff and staff:
            to.append(staff.email)
        
        subject = form.email_subject
        template = Template(form.email_message)
        context = Context({
            'username': username,
            'company': company,
            'form_name': form.title,
            'data': DataToEmailHTML(form, entry)
        })
        message = template.render(context)
        email = EmailMessage(subject, message, to=to, bcc=[form.email_copies])
        email.content_subtype = "html"
        email.send()






def compileFormData(form, entry):

    data = []

    for field in form.fields.all():
        label = field.label


        if field.is_a(fields.FILE):
            value_type = "url"
        elif field.is_a(fields.CHECKBOX):
            value_type = "boolean"
        else:
            value_type = "text"
            
        value = entry.fields.filter(field_id=field.id).get().value
        data.append({'label': label, 'value_type': value_type, 'value': value})
    return data



def DataToEmailHTML(form, entry):
    data = compileFormData(form, entry)

    html = "<table>\n"
    for entry in data:
        label = escape(entry['label'])
        value = entry['value']
        value_type = entry['value_type']

        if value_type == "url":
            formatted_value = format_html("<a href=/media/{}>{}</a>", value, os.path.basename(value))
        elif value_type == "boolean":
            formatted_value = format_html("{}", "Yes" if value == "True" else "No")
        else:
            formatted_value = format_html("{}", value).replace('\n', '<br>\n')

        html += "<tr>\n<td><strong>%s</strong></td>\n<td>%s</td>\n</tr>\n\n" % (label, formatted_value)

    html += "</table>"

    return mark_safe(html)