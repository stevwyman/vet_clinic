from django.contrib import admin
from .models import Owner, Pet, Species, Race, Visit, TreatmentType, VisitTreatment, Intolerance, MedicationType, VisitMedication, Template, TemplateTreatment, TemplateMedication

# Register your models here.
admin.site.register(Owner)
admin.site.register(Pet)
admin.site.register(Species)
admin.site.register(Race)
admin.site.register(Visit)
admin.site.register(TreatmentType)
admin.site.register(VisitTreatment)
admin.site.register(MedicationType)
admin.site.register(VisitMedication)
admin.site.register(Intolerance)
admin.site.register(Template)
admin.site.register(TemplateTreatment)
admin.site.register(TemplateMedication)
