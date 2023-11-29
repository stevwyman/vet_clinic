from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.db.models import Q

from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.utils.translation import gettext as _
from django.urls import reverse, reverse_lazy

from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    TemplateView,
)
from django.views.generic.edit import UpdateView

from django.utils.formats import date_format

from django_otp.decorators import otp_required

from two_factor.views import OTPRequiredMixin
from two_factor.views.utils import class_view_decorator

from logging import getLogger

from .models import (
    Clinic,
    Owner,
    Pet,
    Species,
    Race,
    Case,
    Visit,
    Payment,
    VisitTreatment,
    TreatmentType,
    VisitMedication,
    MedicationType,
    VisitConsumable,
    ConsumablesType,
    Intolerance,
    Template,
    TemplateMedication,
    TemplateTreatment,
    TemplateConsumable,
    VisitDocument,
    CaseDocument,
    PetDocument,
)

logger = getLogger(__name__)

DEFAULT_PAGE_SIZE = 10


# external starting page
class StartView(TemplateView):
    template_name = "client/start.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = Clinic.objects.get(external_id="clinic001")
        if clinic:
            context["clinic"] = clinic.id
        return context


# internal starting page.
class HomeView(TemplateView):
    template_name = "client/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = Clinic.objects.get(external_id="clinic001")
        if clinic:
            context["clinic"] = clinic.id
        return context


class ClinicUpdateView(OTPRequiredMixin, UpdateView):
    model = Clinic

    fields = [
        "name",
        "external_id",
        "title",
        "slogan",
        "return_address",
        "street_number",
        "zip_code",
        "city",
        "iban",
        "bic",
        "phone",
        "mail",
        "url",
    ]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse_lazy("home",)

    def form_valid(self, form):
        messages.success(self.request, "The owner was updated successfully.")
        return super(ClinicUpdateView, self).form_valid(form)


# all confirmed owners for a clinic
class OwnerListView(OTPRequiredMixin, ListView):
    model = Owner

    paginate_by = DEFAULT_PAGE_SIZE

    ordering = ["lastname", "firstname"]

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(
                Q(lastname__icontains=query) & Q(clinic=self.request.user.clinic) & Q(confirmed=True)
            )
        else:
            # object_list = self.model.objects.none() # for better performance
            object_list = self.model.objects.filter(
                Q(clinic=self.request.user.clinic) & Q(confirmed=True)
            )  # for testing
        return object_list


class OwnerCreateView(LoginRequiredMixin, CreateView):
    model = Owner

    fields = [
        "firstname",
        "lastname",
        "postal_street_number",
        "postal_zipcode",
        "postal_city",
        "billing_street_number",
        "billing_zipcode",
        "billing_city",
        "mobile",
        "fixed",
        "email",
        "note",
        "dsgv_accepted",
    ]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.clinic = request.user.clinic
        return super(OwnerCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        owner_id = self.object.id
        return reverse_lazy("owner-detail", kwargs={"pk": owner_id})

    def form_valid(self, form):
        form.instance.clinic = self.clinic
        form.instance.confirmed = True
        messages.success(self.request, "The owner was created successfully.")
        return super(OwnerCreateView, self).form_valid(form)


class OwnerUpdateView(OTPRequiredMixin, UpdateView):
    model = Owner

    fields = [
        "firstname",
        "lastname",
        "postal_street_number",
        "postal_city",
        "postal_zipcode",
        "billing_street_number",
        "billing_city",
        "billing_zipcode",
        "mobile",
        "fixed",
        "email",
        "note",
        "dsgv_accepted",
    ]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        owner_id = self.kwargs["pk"]
        return reverse_lazy("owner-detail", kwargs={"pk": owner_id})

    def form_valid(self, form):
        messages.success(self.request, "The owner was updated successfully.")
        return super(OwnerUpdateView, self).form_valid(form)


class OwnerDetailView(OTPRequiredMixin, DetailView):
    model = Owner


class SpeciesListView(LoginRequiredMixin, ListView):
    model = Species
    paginate_by = DEFAULT_PAGE_SIZE
    ordering = ["name"]


class SpeciesCreateView(LoginRequiredMixin, CreateView):
    model = Species
    fields = ["name", "description"]
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("species")


class SpeciesUpdateView(LoginRequiredMixin, UpdateView):
    model = Species
    fields = ["name", "description"]
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("species")


class RaceListView(LoginRequiredMixin, ListView):
    model = Race
    paginate_by = DEFAULT_PAGE_SIZE
    ordering = ["name"]


class RaceCreateView(LoginRequiredMixin, CreateView):
    model = Race
    fields = ["name", "description", "species"]
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("races")


class RaceUpdateView(LoginRequiredMixin, UpdateView):
    model = Race
    fields = ["name", "description", "species"]
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("races")


class PetCreateView(LoginRequiredMixin, CreateView):
    model = Pet

    fields = [
        "call_name",
        "birth_name",
        "birth_date",
        "deceased_date",
        "sex",
        "chip_id",
        "species",
        "race",
        "castrated",
        "sterilized",
        "intolerance",
        "note",
        "insurance",
    ]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.owner = get_object_or_404(Owner, pk=self.kwargs["owner_id"])
        return super(PetCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pet_id = self.object.id
        return reverse_lazy("pet-detail", kwargs={"pk": pet_id})

    def form_valid(self, form):
        form.instance.owner = (
            self.owner
        )  # if the article is not a required field, otherwise you can use the commit=False way
        messages.success(self.request, "Pet has been successfully created.")
        return super(PetCreateView, self).form_valid(form)


class PetUpdateView(OTPRequiredMixin, UpdateView):
    model = Pet

    fields = [
        "call_name",
        "birth_name",
        "birth_date",
        "deceased_date",
        "sex",
        "chip_id",
        "species",
        "race",
        "castrated",
        "sterilized",
        "intolerance",
        "note",
        "insurance",
    ]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        pet_id = self.kwargs["pk"]
        return reverse_lazy("pet-detail", kwargs={"pk": pet_id})

    def form_valid(self, form):
        messages.success(self.request, "The pet was updated successfully.")
        return super(PetUpdateView, self).form_valid(form)


class PetDetailView(OTPRequiredMixin, DetailView):
    model = Pet


class CaseDetailView(OTPRequiredMixin, DetailView):
    model = Case


class CaseCreateView(LoginRequiredMixin, CreateView):
    model = Case

    fields = ["title", "description"]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.pet = get_object_or_404(Pet, pk=self.kwargs["pet_id"])
        return super(CaseCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        case_id = self.object.id
        return reverse_lazy("case-detail", kwargs={"pk": case_id})

    def form_valid(self, form):
        form.instance.pet = self.pet
        messages.success(self.request, "Case has been successfully created.")
        return super(CaseCreateView, self).form_valid(form)


class CaseUpdateView(OTPRequiredMixin, UpdateView):
    model = Case

    fields = ["timestamp", "title", "description"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        case_id = self.kwargs["pk"]
        return reverse_lazy("case-detail", kwargs={"pk": case_id})

    def form_valid(self, form):
        messages.success(self.request, "The case was updated successfully.")
        return super(CaseUpdateView, self).form_valid(form)


class VisitDetailView(OTPRequiredMixin, DetailView):
    model = Visit


class VisitCreateView(LoginRequiredMixin, CreateView):
    model = Visit

    fields = ["title", "anamneses", "weight", "size", "temperature"]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Case, pk=self.kwargs["case_id"])
        return super(VisitCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        visit_id = self.object.id
        return reverse_lazy("visit-detail", kwargs={"pk": visit_id})

    def form_valid(self, form):
        form.instance.case = self.case
        messages.success(self.request, "Visit has been successfully created.")
        return super(VisitCreateView, self).form_valid(form)


class VisitUpdateView(OTPRequiredMixin, UpdateView):
    model = Visit

    fields = ["title", "anamneses", "weight", "size", "temperature", "timestamp"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        visit_id = self.kwargs["pk"]
        return reverse_lazy("visit-detail", kwargs={"pk": visit_id})

    def form_valid(self, form):
        messages.success(self.request, "The visit was updated successfully.")
        return super(VisitUpdateView, self).form_valid(form)


from django.utils.timezone import datetime


@class_view_decorator(never_cache)
class VisitListView(OTPRequiredMixin, ListView):
    model = Visit
    paginate_by = DEFAULT_PAGE_SIZE
    ordering = ["name"]

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            query_date = datetime.strptime(query, "%d.%m.%Y").date()
            object_list = self.model.objects.filter(timestamp__date=query_date)
        else:
            # object_list = self.model.objects.none() # for better performance
            object_list = self.model.objects.filter(
                timestamp__date=datetime.now().date()
            )  # for testing
        return object_list


class PaymentAddView(LoginRequiredMixin, CreateView):
    model = Payment

    fields = ["amount", "payment_type", "invoice_number"]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.visit = get_object_or_404(Visit, pk=self.kwargs["visit_id"])
        return super(PaymentAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        visit_id = self.kwargs["visit_id"]
        return reverse_lazy("visit-detail", kwargs={"pk": visit_id})

    def form_valid(self, form):
        form.instance.visit = self.visit
        messages.success(self.request, "Payment has been successfully created.")
        return super(PaymentAddView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["visit"] = self.visit
        return context


class PaymentUpdateView(OTPRequiredMixin, UpdateView):
    model = Payment

    fields = ["amount", "payment_type", "invoice_number", "timestamp"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})

    def form_valid(self, form):
        messages.success(self.request, "The treatment was updated successfully.")
        return super(PaymentUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["visit"] = self.object.visit
        return context


class PaymentRemoveView(OTPRequiredMixin, DeleteView):
    model = Payment

    template_name = "client/visit_generic_confirm_delete.html"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})


class VisitTreatmentAddView(OTPRequiredMixin, CreateView):
    model = VisitTreatment

    fields = [
        "type",
        "comment",
        "quantity",
        "tax",
        "overwrite_gross_price",
        "overwrite_net_price",
    ]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.visit = get_object_or_404(Visit, pk=self.kwargs["visit_id"])
        return super(VisitTreatmentAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        visit_id = self.kwargs["visit_id"]
        return reverse_lazy("visit-detail", kwargs={"pk": visit_id})

    def form_valid(self, form):
        form.instance.visit = self.visit
        form.instance.price_per_unit = form.instance.type.price_per_unit
        messages.success(self.request, "Treatment has been successfully created.")
        return super(VisitTreatmentAddView, self).form_valid(form)


class VisitTreatmentUpdateView(OTPRequiredMixin, UpdateView):
    model = VisitTreatment

    fields = ["comment", "overwrite_gross_price", "overwrite_net_price"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})

    def form_valid(self, form):
        messages.success(self.request, "The treatment was updated successfully.")
        return super(VisitTreatmentUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gross_minimum"] = self.object.type.price_per_unit * (
            1 + self.object.tax / 100
        )
        context["gross_factor"] = (
            self.object.quantity
            * self.object.type.price_per_unit
            * (1 + self.object.tax / 100)
        )
        context["gross_maximum"] = (
            4 * self.object.type.price_per_unit * (1 + self.object.tax / 100)
        )
        context["net_minimum"] = self.object.type.price_per_unit
        context["net_factor"] = self.object.quantity * self.object.type.price_per_unit
        context["net_maximum"] = 4 * self.object.type.price_per_unit
        return context


class VisitTreatmentRemoveView(OTPRequiredMixin, DeleteView):
    model = VisitTreatment

    template_name = "client/visit_generic_confirm_delete.html"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})


class TreatmentTypeView(OTPRequiredMixin, ListView):
    model = TreatmentType

    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(
                Q(description__icontains=query) | Q(code__iexact=query)
            )
        else:
            # object_list = self.model.objects.all() # for better performance
            object_list = self.model.objects.all()  # for testing
        return object_list


class TreatmentTypeCreateView(OTPRequiredMixin, CreateView):
    model = TreatmentType

    fields = ["code", "description", "price_per_unit", "current"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        treatment_type_id = self.object.id
        return reverse_lazy("treatment-types")

    def form_valid(self, form):
        messages.success(self.request, "The treatment type was created successfully.")
        return super(TreatmentTypeCreateView, self).form_valid(form)


class TreatmentTypeUpdateView(OTPRequiredMixin, UpdateView):
    model = TreatmentType

    fields = ["code", "description", "price_per_unit", "current"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        treatment_type_id = self.kwargs["pk"]
        return reverse_lazy("treatment-types")

    def form_valid(self, form):
        messages.success(self.request, "The treatment type was updated successfully.")
        return super(TreatmentTypeUpdateView, self).form_valid(form)


class VisitMedicationAddView(OTPRequiredMixin, CreateView):
    model = VisitMedication

    fields = [
        "type",
        "comment",
        "quantity",
        "tax",
        "overwrite_gross_price",
        "overwrite_net_price",
    ]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.visit = get_object_or_404(Visit, pk=self.kwargs["visit_id"])
        return super(VisitMedicationAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        visit_id = self.kwargs["visit_id"]
        return reverse_lazy("visit-detail", kwargs={"pk": visit_id})

    def form_valid(self, form):
        form.instance.visit = self.visit
        form.instance.price_per_unit = form.instance.type.price_per_unit
        messages.success(self.request, "Medication has been successfully created.")
        return super(VisitMedicationAddView, self).form_valid(form)


class VisitMedicationUpdateView(OTPRequiredMixin, UpdateView):
    model = VisitMedication

    fields = ["comment", "quantity", "overwrite_gross_price", "overwrite_net_price"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})

    def form_valid(self, form):
        messages.success(self.request, "The medication was updated successfully.")
        return super(VisitMedicationUpdateView, self).form_valid(form)


class VisitMedicationRemoveView(OTPRequiredMixin, DeleteView):
    model = VisitMedication

    template_name = "client/visit_generic_confirm_delete.html"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})


class MedicationTypeView(OTPRequiredMixin, ListView):
    model = MedicationType

    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(description__icontains=query)
        else:
            # object_list = self.model.objects.all() # for better performance
            object_list = self.model.objects.all()  # for testing
        return object_list


class MedicationTypeCreateView(OTPRequiredMixin, CreateView):
    model = MedicationType

    fields = ["code", "description", "price_per_unit", "current"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        medication_type_id = self.object.id
        return reverse_lazy("medication-types")

    def form_valid(self, form):
        messages.success(self.request, "The medication type was created successfully.")
        return super(MedicationTypeCreateView, self).form_valid(form)


class MedicationTypeUpdateView(OTPRequiredMixin, UpdateView):
    model = MedicationType

    fields = ["description"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        medication_type_id = self.kwargs["pk"]
        return reverse_lazy("medication-types")

    def form_valid(self, form):
        messages.success(self.request, "The medication type was updated successfully.")
        return super(MedicationTypeUpdateView, self).form_valid(form)


class VisitConsumableAddView(OTPRequiredMixin, CreateView):
    model = VisitConsumable

    fields = [
        "type",
        "comment",
        "quantity",
        "tax",
        "overwrite_gross_price",
        "overwrite_net_price",
    ]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.visit = get_object_or_404(Visit, pk=self.kwargs["visit_id"])
        return super(VisitConsumableAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        visit_id = self.kwargs["visit_id"]
        return reverse_lazy("visit-detail", kwargs={"pk": visit_id})

    def form_valid(self, form):
        form.instance.visit = self.visit
        form.instance.price_per_unit = form.instance.type.price_per_unit
        messages.success(self.request, "Medication has been successfully created.")
        return super(VisitConsumableAddView, self).form_valid(form)


class VisitConsumableUpdateView(OTPRequiredMixin, UpdateView):
    model = VisitConsumable

    fields = ["comment", "quantity", "overwrite_gross_price", "overwrite_net_price"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})

    def form_valid(self, form):
        messages.success(self.request, "The medication was updated successfully.")
        return super(VisitConsumableUpdateView, self).form_valid(form)


class VisitConsumableRemoveView(OTPRequiredMixin, DeleteView):
    model = VisitConsumable

    template_name = "client/visit_generic_confirm_delete.html"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})


class ConsumablesTypeView(OTPRequiredMixin, ListView):
    model = ConsumablesType

    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(description__icontains=query)
        else:
            # object_list = self.model.objects.all() # for better performance
            object_list = self.model.objects.all()  # for testing
        return object_list


class ConsumablesTypeCreateView(OTPRequiredMixin, CreateView):
    model = ConsumablesType

    fields = ["code", "description", "price_per_unit", "current"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse_lazy("consumables-types")

    def form_valid(self, form):
        messages.success(self.request, "The consumable type was created successfully.")
        return super(ConsumablesTypeCreateView, self).form_valid(form)


class ConsumablesTypeUpdateView(OTPRequiredMixin, UpdateView):
    model = ConsumablesType

    fields = ["description"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse_lazy("consumables-types")

    def form_valid(self, form):
        messages.success(self.request, "The consumable type was updated successfully.")
        return super(ConsumablesTypeUpdateView, self).form_valid(form)


"""
Intolerance management
"""


class IntoleranceListView(LoginRequiredMixin, ListView):
    model = Intolerance
    context_object_name = "all_intolerance"

    paginate_by = DEFAULT_PAGE_SIZE

    ordering = ["name"]

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(ingredient__icontains=query)
        else:
            # object_list = self.model.objects.all() # for better performance
            object_list = self.model.objects.all()  # for testing
        return object_list


class IntoleranceCreateView(LoginRequiredMixin, CreateView):
    model = Intolerance

    fields = [
        "ingredient",
    ]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        intolerance_id = self.object.id
        return reverse_lazy("intolerance")

    def form_valid(self, form):
        messages.success(self.request, "The intolerance was created successfully.")
        return super(IntoleranceCreateView, self).form_valid(form)


class IntoleranceUpdateView(OTPRequiredMixin, UpdateView):
    model = Intolerance

    fields = ["ingredient"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        ingredient_id = self.kwargs["pk"]
        return reverse_lazy("intolerance")

    def form_valid(self, form):
        messages.success(self.request, "The intolerance was updated successfully.")
        return super(IntoleranceUpdateView, self).form_valid(form)


"""
Templates management

A template defines a set of treatments and medication as a bundle for easy access
"""


class TemplateListView(LoginRequiredMixin, ListView):
    model = Template

    paginate_by = DEFAULT_PAGE_SIZE

    ordering = ["name"]

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(
                Q(description__icontains=query) & Q(clinic=self.request.user.clinic)
            )
        else:
            # object_list = self.model.objects.all() # for better performance
            object_list = self.model.objects.filter(
                Q(clinic=self.request.user.clinic)
            )  # for testing
        return object_list


class TemplateCreateView(LoginRequiredMixin, CreateView):
    model = Template

    fields = ["name", "description"]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.clinic = request.user.clinic
        return super(TemplateCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        template_id = self.object.id
        return reverse_lazy("template-detail", kwargs={"pk": template_id})

    def form_valid(self, form):
        form.instance.clinic = self.clinic
        messages.success(self.request, "The template was created successfully.")
        return super(TemplateCreateView, self).form_valid(form)


class TemplateUpdateView(OTPRequiredMixin, UpdateView):
    model = Template

    fields = ["name", "description"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        template_id = self.kwargs["pk"]
        return reverse_lazy("template-detail", kwargs={"pk": template_id})

    def form_valid(self, form):
        messages.success(self.request, "The template was updated successfully.")
        return super(TemplateUpdateView, self).form_valid(form)


class TemplateDetailView(OTPRequiredMixin, DetailView):
    model = Template


class TemplateMedicationAddView(OTPRequiredMixin, CreateView):
    model = TemplateMedication

    fields = ["type", "quantity", "tax"]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.template = get_object_or_404(Template, pk=self.kwargs["template_id"])
        return super(TemplateMedicationAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        template_id = self.kwargs["template_id"]
        return reverse_lazy("template-detail", kwargs={"pk": template_id})

    def form_valid(self, form):
        form.instance.template = self.template
        messages.success(self.request, "Medication has been successfully added.")
        return super(TemplateMedicationAddView, self).form_valid(form)


class TemplateMedicationUpdateView(OTPRequiredMixin, UpdateView):
    model = TemplateMedication

    fields = ["comment", "overwrite_net_price", "overwrite_gross_price"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        template = self.object.template
        return reverse_lazy("template-detail", kwargs={"pk": template.id})

    def form_valid(self, form):
        messages.success(self.request, "The medication was updated successfully.")
        return super(TemplateMedicationUpdateView, self).form_valid(form)


class TemplateMedicationRemoveView(OTPRequiredMixin, DeleteView):
    model = TemplateMedication

    def get_success_url(self):
        template = self.object.template
        return reverse_lazy("template-detail", kwargs={"pk": template.id})


class TemplateTreatmentAddView(OTPRequiredMixin, CreateView):
    model = TemplateTreatment

    fields = ["type", "quantity", "tax"]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.template = get_object_or_404(Template, pk=self.kwargs["template_id"])
        return super(TemplateTreatmentAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        template_id = self.kwargs["template_id"]
        return reverse_lazy("template-detail", kwargs={"pk": template_id})

    def form_valid(self, form):
        form.instance.template = self.template
        messages.success(
            self.request, "Treatment has been successfully added to template."
        )
        return super(TemplateTreatmentAddView, self).form_valid(form)


class TemplateTreatmentUpdateView(OTPRequiredMixin, UpdateView):
    model = TemplateTreatment

    fields = ["comment", "overwrite_net_price", "overwrite_gross_price"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        template = self.object.template
        return reverse_lazy("template-detail", kwargs={"pk": template.id})

    def form_valid(self, form):
        messages.success(self.request, "The treatment was updated successfully.")
        return super(TemplateTreatmentUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gross_minimum"] = self.object.type.price_per_unit * (
            1 + self.object.tax / 100
        )
        context["gross_factor"] = (
            self.object.quantity
            * self.object.type.price_per_unit
            * (1 + self.object.tax / 100)
        )
        context["gross_maximum"] = (
            4 * self.object.type.price_per_unit * (1 + self.object.tax / 100)
        )
        context["net_minimum"] = self.object.type.price_per_unit
        context["net_factor"] = self.object.quantity * self.object.type.price_per_unit
        context["net_maximum"] = 4 * self.object.type.price_per_unit
        return context


class TemplateTreatmentRemoveView(OTPRequiredMixin, DeleteView):
    model = TemplateTreatment

    def get_success_url(self):
        template = self.object.template
        return reverse_lazy("template-detail", kwargs={"pk": template.id})


class TemplateConsumableAddView(OTPRequiredMixin, CreateView):
    model = TemplateConsumable

    fields = ["type", "quantity", "tax"]

    template_name_suffix = "_update_form"

    def dispatch(self, request, *args, **kwargs):
        self.template = get_object_or_404(Template, pk=self.kwargs["template_id"])
        return super(TemplateConsumableAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        template_id = self.kwargs["template_id"]
        return reverse_lazy("template-detail", kwargs={"pk": template_id})

    def form_valid(self, form):
        form.instance.template = self.template
        messages.success(
            self.request, "Treatment has been successfully added to template."
        )
        return super(TemplateConsumableAddView, self).form_valid(form)


class TemplateConsumableRemoveView(OTPRequiredMixin, DeleteView):
    model = TemplateConsumable

    def get_success_url(self):
        template = self.object.template
        return reverse_lazy("template-detail", kwargs={"pk": template.id})


class TemplateConsumableUpdateView(OTPRequiredMixin, UpdateView):
    model = TemplateConsumable

    fields = ["comment", "overwrite_net_price", "overwrite_gross_price"]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        template = self.object.template
        return reverse_lazy("template-detail", kwargs={"pk": template.id})

    def form_valid(self, form):
        messages.success(self.request, "The consumable was updated successfully.")
        return super(TemplateConsumableUpdateView, self).form_valid(form)


#
# managing documents
#
class VisitDocumentAddView(LoginRequiredMixin, CreateView):
    model = VisitDocument

    fields = ["document", "comment"]

    template_name = "client/document_update_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.visit = get_object_or_404(Visit, pk=self.kwargs["visit_id"])
        return super(VisitDocumentAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        visit_id = self.kwargs["visit_id"]
        return reverse_lazy("visit-detail", kwargs={"pk": visit_id})

    def form_valid(self, form):
        form.instance.visit = self.visit
        messages.success(self.request, "Document has been successfully added to visit.")
        return super(VisitDocumentAddView, self).form_valid(form)


class VisitDocumentUpdateView(OTPRequiredMixin, UpdateView):
    model = VisitDocument

    fields = ["document", "comment"]

    template_name = "client/document_update_form.html"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})

    def form_valid(self, form):
        messages.success(self.request, "The document was updated successfully.")
        return super(VisitDocumentUpdateView, self).form_valid(form)


class VisitDocumentRemoveView(OTPRequiredMixin, DeleteView):
    model = VisitDocument

    template_name = "client/document_generic_confirm_delete.html"

    def get_success_url(self):
        visit = self.object.visit
        return reverse_lazy("visit-detail", kwargs={"pk": visit.id})


class PetDocumentAddView(LoginRequiredMixin, CreateView):
    model = PetDocument

    fields = ["document", "comment"]

    template_name = "client/document_update_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.pet = get_object_or_404(Pet, pk=self.kwargs["pet_id"])
        return super(PetDocumentAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pet_id = self.kwargs["pet_id"]
        return reverse_lazy("pet-detail", kwargs={"pk": pet_id})

    def form_valid(self, form):
        form.instance.pet = self.pet
        messages.success(self.request, "Document has been successfully added to pet.")
        return super(PetDocumentAddView, self).form_valid(form)


class PetDocumentUpdateView(OTPRequiredMixin, UpdateView):
    model = PetDocument

    fields = ["document", "comment"]

    template_name = "client/document_update_form.html"

    def get_success_url(self):
        pet = self.object.pet
        return reverse_lazy("pet-detail", kwargs={"pk": pet.id})

    def form_valid(self, form):
        messages.success(self.request, "The document was updated successfully.")
        return super(PetDocumentUpdateView, self).form_valid(form)


class PetDocumentRemoveView(OTPRequiredMixin, DeleteView):
    model = PetDocument

    template_name = "client/document_generic_confirm_delete.html"

    def get_success_url(self):
        pet = self.object.pet
        return reverse_lazy("pet-detail", kwargs={"pk": pet.id})


class CaseDocumentAddView(LoginRequiredMixin, CreateView):
    model = CaseDocument

    fields = ["document", "comment"]

    template_name = "client/document_update_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Case, pk=self.kwargs["case_id"])
        return super(CaseDocumentAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        case_id = self.kwargs["case_id"]
        return reverse_lazy("case-detail", kwargs={"pk": case_id})

    def form_valid(self, form):
        form.instance.case = self.case
        messages.success(self.request, "Document has been successfully added to case.")
        return super(CaseDocumentAddView, self).form_valid(form)


class CaseDocumentUpdateView(OTPRequiredMixin, UpdateView):
    model = CaseDocument

    fields = ["document", "comment"]

    template_name = "client/document_update_form.html"

    def get_success_url(self):
        case = self.object.case
        return reverse_lazy("case-detail", kwargs={"pk": case.id})

    def form_valid(self, form):
        messages.success(self.request, "The document was updated successfully.")
        return super(CaseDocumentUpdateView, self).form_valid(form)


class CaseDocumentRemoveView(OTPRequiredMixin, DeleteView):
    model = CaseDocument

    template_name = "client/document_generic_confirm_delete.html"

    def get_success_url(self):
        case = self.object.case
        return reverse_lazy("case-detail", kwargs={"pk": case.id})


#
# Waiting room management
#
from .forms import WaitingCustomer
# an owner can self-register here, two step approach: first owner, followed by pet
class OwnerWaitView(CreateView):
    
    model = Owner
    form_class = WaitingCustomer

    template_name = "client/waiting_room_register.html"

    def dispatch(self, request, *args, **kwargs):
        self.clinic = get_object_or_404(Clinic, pk=self.kwargs["pk"])
        return super(OwnerWaitView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        owner_id = self.object.id
        return reverse_lazy("register-pet", kwargs={"pk": owner_id})

    def form_valid(self, form):
        form.instance.clinic = self.clinic
        messages.success(self.request, "The owner was created successfully.")
        return super(OwnerWaitView, self).form_valid(form)


class PetWaitCreateView(CreateView):
    model = Pet

    fields = [
        "call_name",
        "birth_date",
        "sex",
        "species",
        "castrated",
        "sterilized",
        "note"
    ]

    template_name = "client/waiting_room_register.html"

    def dispatch(self, request, *args, **kwargs):
        self.owner = get_object_or_404(Owner, pk=self.kwargs["pk"])
        return super(PetWaitCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pet_id = self.object.id
        return reverse_lazy("registration-thank", kwargs={"pk": pet_id})

    def form_valid(self, form):
        form.instance.owner = (
            self.owner
        )  # if the article is not a required field, otherwise you can use the commit=False way
        messages.success(self.request, "Pet has been successfully created.")
        return super(PetWaitCreateView, self).form_valid(form)


class Registration_Thank(TemplateView):
    template_name = "client/thanks.html"

    def get_context_data(self, **kwargs):
        context = super(Registration_Thank, self).get_context_data(**kwargs)
        context["pet"] = get_object_or_404(Pet, pk=self.kwargs["pk"])
        return context
                                                

# owner that have the flag confirmed set to false, as they have registered them selfs
class WaitingRoomListView(OTPRequiredMixin, ListView):
    model = Owner

    paginate_by = DEFAULT_PAGE_SIZE

    ordering = ["lastname", "firstname"]

    template_name = "client/waiting_room.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(
                Q(lastname__icontains=query) & Q(clinic=self.request.user.clinic) & Q(confirmed=False)
            )
        else:
            # object_list = self.model.objects.none() # for better performance
            object_list = self.model.objects.filter(
                Q(clinic=self.request.user.clinic) & Q(confirmed=False)
            )  # for testing
        return object_list


# view for the doc to check a new customer from the waiting room list
class CallOwnerUpdateView(OTPRequiredMixin, UpdateView):
    model = Owner

    fields = [
        "firstname",
        "lastname",
        "postal_street_number",
        "postal_city",
        "postal_zipcode",
        "billing_street_number",
        "billing_city",
        "billing_zipcode",
        "mobile",
        "fixed",
        "email",
        "note",
        "dsgv_accepted",
    ]

    template_name_suffix = "_update_form"

    def get_success_url(self):
        owner_id = self.kwargs["pk"]
        return reverse_lazy("owner-detail", kwargs={"pk": owner_id})

    def form_valid(self, form):
        form.instance.confirmed = True
        messages.success(self.request, "The owner was updated successfully.")
        return super(CallOwnerUpdateView, self).form_valid(form)


# drop an owner from the waiting room; in case they entered wrong data
class OwnerWaitRemoveView(OTPRequiredMixin, DeleteView):
    model = Owner

    template_name = "client/visit_generic_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("waiting-room")


@otp_required()
def add_template(request, visit_id):
    """
    in the get scenario, a list is being provided to choose a template for this visit
    in the post scenario, the data from the chosen template is being added to the visit
    """
    # show a page with a dropdown list of templates
    if request.method == "GET":
        visit = get_object_or_404(Visit, pk=visit_id)
        templates = Template.objects.all()

        return render(
            request,
            "client/template_choose_form.html",
            {"templates": templates, "visit": visit},
        )
    elif request.method == "POST":
        try:
            visit_pk = request.POST.get("visit_id")
            visit = get_object_or_404(Visit, pk=visit_pk)

            template_pk = request.POST.get("template_id")
            template = get_object_or_404(Template, pk=template_pk)

        except RuntimeError as rt:
            messages.warning(request, "Either visit_id or template_id not found")
            return HttpResponseRedirect(reverse("owners"))

        for treatment in template.template_treatments.all():
            visit_treatment = VisitTreatment(
                visit=visit,
                type=treatment.type,
                tax=treatment.tax,
                quantity=treatment.quantity,
                price_per_unit=treatment.type.price_per_unit,
                overwrite_net_price=treatment.overwrite_net_price,
                overwrite_gross_price=treatment.overwrite_gross_price,
            )  # Case of update
            visit_treatment.save()
        for medication in template.template_medications.all():
            visit_medication = VisitMedication(
                visit=visit,
                type=medication.type,
                tax=medication.tax,
                quantity=medication.quantity,
                price_per_unit=medication.type.price_per_unit,
                overwrite_net_price=medication.overwrite_net_price,
                overwrite_gross_price=medication.overwrite_gross_price,
            )  # Case of update
            visit_medication.save()
        for consumable in template.template_consumables.all():
            visit_consumable = VisitConsumable(
                visit=visit,
                type=consumable.type,
                tax=consumable.tax,
                quantity=consumable.quantity,
                price_per_unit=consumable.type.price_per_unit,
                overwrite_net_price=consumable.overwrite_net_price,
                overwrite_gross_price=consumable.overwrite_gross_price,
            )  # Case of update
            visit_consumable.save()

        messages.info(request, f"Template '{template}' added to visit.")

        return HttpResponseRedirect(reverse("visit-detail", kwargs={"pk": visit_pk}))


@otp_required()
def fit(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)

    first_treatment = visit.visit_treatments.first()

    price = visit.price()
    rest = price - int(price)

    if first_treatment is None or rest == 0:
        messages.warning(request, "Nothing to adjust")
    else:

        # special case if the net price has been overwritten
        # then we need to do the calculation based on that
        if first_treatment.overwrite_net_price:
            original_price = first_treatment.gross_price()
            net_price = first_treatment.overwrite_net_price

            first_treatment.overwrite_net_price = net_price - rest / (1 + first_treatment.tax / 100)
            first_treatment.save(update_fields=["overwrite_net_price"])

            pass
        else:
            original_price = first_treatment.gross_price()

            first_treatment.overwrite_gross_price = original_price - rest
            first_treatment.save(update_fields=["overwrite_gross_price"])

    return HttpResponseRedirect(reverse("visit-detail", kwargs={"pk": visit.id}))


@otp_required()
def media_view(request, type, media_id):
    if not request.user.is_authenticated:
        logger.warning(
            request, f"someone calling {type} {media_id} without being authenticated"
        )
        return HttpResponseRedirect(reverse("home"))

    try:
        if type == "pet":
            media = get_object_or_404(PetDocument, pk=media_id)
        elif type == "case":
            media = get_object_or_404(CaseDocument, pk=media_id)
        elif type == "visit":
            media = get_object_or_404(VisitDocument, pk=media_id)
        else:
            logger.warning(
                request, f"someone calling {type} {media_id} with the wrong type"
            )
    except ValidationError:
        logger.warning(
            request, f"someone calling {type} {media_id}, but the id is not valid"
        )
        return HttpResponseRedirect(reverse("home"))

    try:
        return FileResponse(open(media.document.path, "rb"))
    except FileNotFoundError:
        logger.warning(
            request, f"someone calling {type} {media_id}, but the file is not existing"
        )
        return HttpResponseRedirect(reverse("home"))


from .pdf_invoice import InvoiceDocument


@otp_required()
def generate_simple_invoice(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)

    pdf = InvoiceDocument(visit)
    pdf.generate_invoice(form=None)

    response = HttpResponse(bytes(pdf.output()), content_type="application/pdf")
    # response['Content-Disposition'] = "attachment; filename=myfilename.pdf"           # use this to directly download the generated pdf

    return response


from .forms import InvoiceForm


@otp_required()
def generate_advanced_invoice(request, visit_id):
    # GET provides the form for manual overwrite
    if request.method == "GET":
        visit = get_object_or_404(Visit, pk=visit_id)

        try:
            invoice_no = visit.invoice.invoice_no
        except ObjectDoesNotExist:
            invoice_no = ""

        form = InvoiceForm(
            initial={
                "date": date_format(
                    visit.timestamp, format="SHORT_DATE_FORMAT", use_l10n=True
                ),
                "address": visit.case.pet.owner.lastname,
                "text": visit.title,
                "invoice": invoice_no
            }
        )

        return render(
            request,
            "client/invoice_prepare.html",
            {"form": form, "visit": visit, "owner": visit.case.pet.owner},
        )

    # POST generates the invoice
    elif request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            visit = get_object_or_404(Visit, pk=visit_id)

            pdf = InvoiceDocument(visit)
            pdf.generate_invoice(form)

            response = HttpResponse(bytes(pdf.output()), content_type="application/pdf")
            # response['Content-Disposition'] = "attachment; filename=myfilename.pdf"        # use this to directly download the generated pdf

            return response


#
# managing participants
#


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))
