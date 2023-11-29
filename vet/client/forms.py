from django import forms
from django.utils.translation import gettext as _

from .models import Owner


class InvoiceForm(forms.Form):
    date = forms.CharField(label=_("date"), max_length=100)
    invoice = forms.CharField(label=_("invoice number"), max_length=100)
    address = forms.CharField(label=_("letter address"), max_length=100)
    text = forms.CharField(label=_("text"), max_length=400)


class WaitingCustomer(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = Owner
        fields = [
            "firstname",
            "lastname",
            "postal_street_number",
            "postal_zipcode",
            "postal_city",
            "mobile",
            "fixed",
            "email",
            "dsgv_accepted",
        ]
        required = [
            "firstname",
            "lastname",
            "postal_street_number",
            "postal_city",
            "postal_zipcode",
            # "mobile",
            "dsgv_accepted",
        ]
