from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from django.db import IntegrityError

from django.utils.translation import gettext as _

from django.shortcuts import render


from logging import getLogger

logger = getLogger(__name__)

from .models import (
    Clinic,
    User,
    Owner,
    Pet,
    Species,
    Race,
    TreatmentType,
    Template,
    TemplateTreatment,
)


def initial(request):
    try:
        praxis_weimann = Clinic.objects.get(external_id="clinic001")
    except ObjectDoesNotExist:
        praxis_weimann = Clinic.objects.create(external_id="clinic001")
        logger.info(f"Created initial clinic {praxis_weimann.external_id}")

    try:
        admin = User.objects.get(username="vet_admin")
    except ObjectDoesNotExist:
        admin = User.objects.create_user(
            username="vet_admin",
            email="admin@admin.de",
            password="_admin-123",
            clinic=praxis_weimann,
        )
        admin.role = 1
        admin.save()
        logger.info(f"Created initial user {admin.username}")

    try:
        felis = Species.objects.get(name="Katze")
    except ObjectDoesNotExist:
        felis = Species.objects.create(name="Katze", description="Felis catus")

    try:
        ehk = Race.objects.create(name="europäische Hauskatze", species=felis)
        british_shorthair = Race.objects.create(name="Britisch Kurzhaar", species=felis)
    except IntegrityError:
        pass

    try:
        canis = Species.objects.get(name="Hund")
    except ObjectDoesNotExist:
        canis = Species.objects.create(
            name="Hund", description="Canis lupus familiaris"
        )

    try:
        mix = Race.objects.create(name="Mischling", species=canis)
    except IntegrityError:
        pass

    try:
        caviidae = Species.objects.get(name="Meerschweinchen")
    except ObjectDoesNotExist:
        caviidae = Species.objects.create(
            name="Meerschweinchen", description="Caviidae"
        )

    try:
        cricetinae = Species.objects.get(name="Hamster")
    except ObjectDoesNotExist:
        cricetinae = Species.objects.create(name="Hamster", description="Cricetinae")

    try:
        lepores = Species.objects.get(name="Kaninchen")
    except ObjectDoesNotExist:
        lepores = Species.objects.create(name="Kaninchen", description="Lepores")

    try:
        avis = Species.objects.get(name="Vogel")
    except ObjectDoesNotExist:
        avis = Species.objects.create(name="Vogel", description="Avis")

    try:
        max_mustermann = Owner.objects.get(lastname="Mustermann", firstname="Max")
    except ObjectDoesNotExist:
        max_mustermann = Owner.objects.create(
            clinic=praxis_weimann,
            firstname="Max",
            lastname="Mustermann",
            postal_street_number="Musterstraße 1a",
            postal_zipcode="22559",
            postal_city="Hamburg",
            confirmed=True,
        )

    try:
        miezi = Pet.objects.get(owner=max_mustermann, call_name="Miezi")
    except ObjectDoesNotExist:
        Pet.objects.create(
            owner=max_mustermann,
            call_name="Miezi",
            birth_date="2020-01-01",
            sex="&male;",
            species=felis,
        )

    try:
        castration_cat_template = Template.objects.get(name="Kastration Kater")
    except ObjectDoesNotExist:
        castration_cat_template = Template(
            name="Kastration Kater",
            description="Eine Kastration für einen Kater basierend auf dem Faktor 1.5",
            clinic=praxis_weimann,
        )
        castration_cat_template.save()

        TemplateTreatment.objects.create(
            template=castration_cat_template,
            type=TreatmentType.objects.get(code=16),
            tax=19.0,
            quantity=1.5,
        )
        TemplateTreatment.objects.create(
            template=castration_cat_template,
            type=TreatmentType.objects.get(code=221),
            tax=19.0,
            quantity=1.5,
        )
        TemplateTreatment.objects.create(
            template=castration_cat_template,
            type=TreatmentType.objects.get(code=310),
            tax=19.0,
            quantity=1.5,
        )
        TemplateTreatment.objects.create(
            template=castration_cat_template,
            type=TreatmentType.objects.get(code=378),
            tax=19.0,
            quantity=1.5,
        )

    try:
        tollwut_vac_template = Template.objects.get(name="Tollwutimpfung Hund")
    except ObjectDoesNotExist:
        tollwut_vac_template = Template(
            name="Tollwutimpfung Hund",
            description="Eine Tollwut Impfung für einen Hund basierend auf dem Faktor 1.5, einfache Dokumentation",
            clinic=praxis_weimann,
        )
        tollwut_vac_template.save()

        TemplateTreatment.objects.create(
            template=tollwut_vac_template,
            type=TreatmentType.objects.get(code=16),
            tax=19.0,
            quantity=1.5,
        )
        TemplateTreatment.objects.create(
            template=tollwut_vac_template,
            type=TreatmentType.objects.get(code=221),
            tax=19.0,
            quantity=1.5,
        )
        TemplateTreatment.objects.create(
            template=tollwut_vac_template,
            type=TreatmentType.objects.get(code=240),
            tax=19.0,
            quantity=1.5,
        )
        TemplateTreatment.objects.create(
            template=tollwut_vac_template,
            type=TreatmentType.objects.get(code=87),
            tax=19.0,
            quantity=1.5,
        )

    messages.info(request, "All done")
    return render(request, "client/index.html")
