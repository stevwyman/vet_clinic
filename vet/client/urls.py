from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.views import LogoutView
from two_factor.urls import urlpatterns as tf_urls

from . import default_init, views

urlpatterns = [

    path("home", views.HomeView.as_view(), name="home"),

    path("owners/", views.OwnerListView.as_view(), name="owners"),

    path("owner/<pk>", views.OwnerDetailView.as_view(), name="owner-detail"),
    path("owner_create/", views.OwnerCreateView.as_view(), name="owner-create"),
    path("owner_update/<pk>", views.OwnerUpdateView.as_view(), name="owner-update"),

    path("pet/<pk>", views.PetDetailView.as_view(), name="pet-detail"),
    path("pet_create/<owner_id>", views.PetCreateView.as_view(), name="pet-create"),
    path("pet_update/<pk>", views.PetUpdateView.as_view(), name="pet-update"),

    # manage the documents within a pet
    path("pet_document_add/<pet_id>", views.PetDocumentAddView.as_view(), name="pet-add-document"),
    path("pet_document_update/<pk>", views.PetDocumentUpdateView.as_view(), name="pet-update-document"),
    path("pet_document_remove/<pk>", views.PetDocumentRemoveView.as_view(), name="pet-remove-document"),

    path("species/", views.SpeciesListView.as_view(), name="species"),
    path("species_create/", views.SpeciesCreateView.as_view(), name="species-create"),
    path("species_update/<pk>", views.SpeciesUpdateView.as_view(), name="species-update"),

    path("races/", views.RaceListView.as_view(), name="races"),
    path("race_create/", views.RaceCreateView.as_view(), name="race-create"),
    path("race_update/<pk>", views.RaceUpdateView.as_view(), name="race-update"),

    path("intolerance/", views.IntoleranceListView.as_view(), name="intolerance"),
    path("intolerance_create/", views.IntoleranceCreateView.as_view(), name="intolerance-create"),
    path("intolerance_update/<pk>", views.IntoleranceUpdateView.as_view(), name="intolerance-update"),

    ## treatments
    path("treatment_types/", views.TreatmentTypeView.as_view(), name="treatment-types"),
    path("treatment_type_create/", views.TreatmentTypeCreateView.as_view(), name="treatment-type-create"),
    path("treatment_type_update/<pk>", views.TreatmentTypeUpdateView.as_view(), name="treatment-type-update"),

    ## medications
    path("medication_types/", views.MedicationTypeView.as_view(), name="medication-types"),
    path("medication_type_create/", views.MedicationTypeCreateView.as_view(), name="medication-type-create"),
    path("medication_type_update/<pk>", views.MedicationTypeUpdateView.as_view(), name="medication-type-update"),

    ## consumables
    path("consumables_types/", views.ConsumablesTypeView.as_view(), name="consumables-types"),
    path("consumables_type_create/", views.ConsumablesTypeCreateView.as_view(), name="consumables-type-create"),
    path("consumables_type_update/<pk>", views.ConsumablesTypeUpdateView.as_view(), name="consumables-type-update"),

    #
    # Cases
    #
    path("case_create/<pet_id>", views.CaseCreateView.as_view(), name="case-create"),
    path("case/<pk>", views.CaseDetailView.as_view(), name="case-detail"),
    path("case_update/<pk>", views.CaseUpdateView.as_view(), name="case-update"),

    # manage the documents within a case
    path("case_document_add/<case_id>", views.CaseDocumentAddView.as_view(), name="case-add-document"),
    path("case_document_update/<pk>", views.CaseDocumentUpdateView.as_view(), name="case-update-document"),
    path("case_document_remove/<pk>", views.CaseDocumentRemoveView.as_view(), name="case-remove-document"),

    #
    # Visits
    #
    path("visit_create/<case_id>", views.VisitCreateView.as_view(), name="visit-create"),
    path("visit/<pk>", views.VisitDetailView.as_view(), name="visit-detail"),
    path("visit_update/<pk>", views.VisitUpdateView.as_view(), name="visit-update"),

    # manage the treatment within a visit
    path("visit_treatment_add/<visit_id>", views.VisitTreatmentAddView.as_view(), name="visit-add-treatment"),
    path("visit_treatment_remove/<pk>", views.VisitTreatmentRemoveView.as_view(), name="visit-remove-treatment"),
    path("visit_treatment_update/<pk>", views.VisitTreatmentUpdateView.as_view(), name="visit-update-treatment"),
    
    # manage the medication within a visit
    path("visit_medication_add/<visit_id>", views.VisitMedicationAddView.as_view(), name="visit-add-medication"),
    path("visit_medication_remove/<pk>", views.VisitMedicationRemoveView.as_view(), name="visit-remove-medication"),
    path("visit_medication_update/<pk>", views.VisitMedicationUpdateView.as_view(), name="visit-update-medication"),

    # manage the consumable within a visit
    path("visit_consumable_add/<visit_id>", views.VisitConsumableAddView.as_view(), name="visit-add-consumable"),
    path("visit_consumable_remove/<pk>", views.VisitConsumableRemoveView.as_view(), name="visit-remove-consumable"),
    path("visit_consumable_update/<pk>", views.VisitConsumableUpdateView.as_view(), name="visit-update-consumable"),

    # manage the documents within a visit
    path("visit_document_add/<visit_id>", views.VisitDocumentAddView.as_view(), name="visit-add-document"),
    path("visit_document_update/<pk>", views.VisitDocumentUpdateView.as_view(), name="visit-update-document"),
    path("visit_document_remove/<pk>", views.VisitDocumentRemoveView.as_view(), name="visit-remove-document"),

    # manage the payment within a visit
    path("payment_add/<visit_id>", views.PaymentAddView.as_view(), name="visit-add-payment"),
    path("payment_remove/<pk>", views.PaymentRemoveView.as_view(), name="visit-remove-payment"),
    path("payment_update/<pk>", views.PaymentUpdateView.as_view(), name="visit-update-payment"),

    path("visits", views.VisitListView.as_view(), name="visits"),

    # 
    # Templates
    #
    path("templates/", views.TemplateListView.as_view(), name="templates"),

    path("template_create/", views.TemplateCreateView.as_view(), name="template-create"),
    path("template/<pk>", views.TemplateDetailView.as_view(), name="template-detail"),
    path("template_update/<pk>", views.TemplateUpdateView.as_view(), name="template-update"),

    # manage the treatment within a template
    path("template_treatment_add/<template_id>", views.TemplateTreatmentAddView.as_view(), name="template-add-treatment"),
    path("template_treatment_remove/<pk>", views.TemplateTreatmentRemoveView.as_view(), name="template-remove-treatment"),
    path("template_treatment_update/<pk>", views.TemplateTreatmentUpdateView.as_view(), name="template-update-treatment"),

    # manage the medication within a template
    path("template_medication_add/<template_id>", views.TemplateMedicationAddView.as_view(), name="template-add-medication"),
    path("template_medication_remove/<pk>", views.TemplateMedicationRemoveView.as_view(), name="template-remove-medication"),
    path("template_medication_update/<pk>", views.TemplateMedicationUpdateView.as_view(), name="template-update-medication"),

    # manage the consumables within a template
    path("template_consumable_add/<template_id>", views.TemplateConsumableAddView.as_view(), name="template-add-consumable"),
    path("template_consumable_remove/<pk>", views.TemplateConsumableRemoveView.as_view(), name="template-remove-consumable"),
    path("template_consumable_update/<pk>", views.TemplateConsumableUpdateView.as_view(), name="template-update-consumable"),

    # adding the content of a template to a visit
    path("template_2_visit/<visit_id>", views.add_template, name="add_template_to_visit" ),

    path("fit/<visit_id>", views.fit, name="fit"),
    path("media_view/<str:type>/<media_id>", views.media_view, name="media-view"),

    path("invoice/<visit_id>", views.generate_simple_invoice , name="invoice"),
    path("invoice_advanced/<visit_id>", views.generate_advanced_invoice , name="invoice-advanced"),


    # waiting room - self register for new owner
    path("", views.StartView.as_view(), name="start"),
    path("register_owner/<pk>", views.OwnerWaitView.as_view(), name="register-owner"),
    path("register_pet/<pk>", views.PetWaitCreateView.as_view(), name="register-pet"),
    path("registration_thank/<pk>", views.Registration_Thank.as_view(), name="registration-thank"),

    # waiting room - doc calling new owner and confirms his/her data
    path("waiting_room", views.WaitingRoomListView.as_view(), name="waiting-room"),
    path("call_owner/<pk>", views.CallOwnerUpdateView.as_view(), name="call-owner"),
    path("remove_owner/<pk>", views.OwnerWaitRemoveView.as_view(), name="remove-owner"),
    
    # initial set-up of clinic, user, some species/races and line-items
    path("initial", default_init.initial, name="initial"),
    path("clinic_update/<pk>", views.ClinicUpdateView.as_view(), name="clinic-update"),

    # managing participants
    #path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    #path("register", views.register, name="register")

    #path("account/register/", views.RegistrationView.as_view(), name="registration"),
    #path("account/register/done/", views.RegistrationCompleteView.as_view(), name="registration_complete"),
    
    path('', include(tf_urls)),

]