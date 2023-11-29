import uuid
import os

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _


from phonenumber_field.modelfields import PhoneNumberField

from datetime import date

DEFAULT_FACTOR = 1.5


class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(_("name"), max_length=100, null=False, blank=False)

    external_id = models.CharField(
        _("external identification"), max_length=100, null=False, blank=False
    )

    # the following are used for invoice creation (pdf template)
    title = models.CharField(max_length=100, null=True, blank=True)
    slogan = models.CharField(max_length=100, null=True, blank=True)

    return_address = models.CharField(max_length=100, null=True, blank=True)
    street_number = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    iban = models.CharField(max_length=100, null=True, blank=True)
    bic = models.CharField(max_length=100, null=True, blank=True)

    phone = models.CharField(max_length=100, null=True, blank=True)
    mail = models.CharField(max_length=100, null=True, blank=True)
    url = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """
    The user represents the different roles within a vet clinic
    """

    DOCTOR = 1
    ASSISTANT = 2
    BASIC = 3

    ROLE_CHOICES = (
        (DOCTOR, "Doctor"),
        (ASSISTANT, "Assistant"),
        (BASIC, "Basic"),
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, blank=False, null=False, default=DOCTOR
    )

    clinic = models.ForeignKey(
        Clinic, null=False, blank=False, on_delete=models.PROTECT, related_name="users"
    )


# Owner
class Owner(models.Model):
    """
    The owner is the human who has one or many pets
    """

    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    clinic = models.ForeignKey(
        Clinic,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="clinic_owners",
    )

    firstname = models.CharField(
        _("firstname"), max_length=100, null=False, blank=False
    )
    lastname = models.CharField(_("lastname"), max_length=100, null=False, blank=False)

    postal_street_number = models.CharField(
        _("postal street number"), max_length=100, null=False, blank=False
    )

    postal_zipcode = models.CharField(
        _("postal zipcode"), max_length=5, null=False, blank=False
    )
    postal_city = models.CharField(
        _("postal city"), max_length=100, null=False, blank=False
    )


    billing_street_number = models.CharField(
        _("billing street number"), max_length=100, null=True, blank=True
    )
    billing_zipcode = models.CharField(
        _("billing zipcode"), max_length=5, null=True, blank=True
    )
    billing_city = models.CharField(
        _("billing city"), max_length=100, null=True, blank=True
    )


    mobile = PhoneNumberField(_("mobile"), null=True, blank=True, unique=True, region="DE")
    fixed = PhoneNumberField(_("fixed"), null=True, blank=True, unique=False)
    email = models.EmailField(
        _("email"), max_length=254, null=True, blank=True, unique=True
    )

    note = models.CharField(_("note"), max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    dsgv_accepted = models.BooleanField(_("dsgv accepted"), default=False)

    confirmed = models.BooleanField(_("confirmed"), default=False)

    class Meta:
        ordering = ["lastname", "firstname"]

    def __str__(self):
        return self.lastname + ", " + self.firstname

    def last_visit(self):
        """
        based on the last visit of each pet, return the last visit of the owner
        return None, if no visits occurred so far
        """
        visits: list = []
        for pet in self.pets.all():
            if pet.last_visit():
                visits.append(pet.last_visit())

        if len(visits) == 0:
            return None
        else:
            return sorted(visits, key=lambda x: x.timestamp)[0]

    def balance(self):
        balance = 0
        for pet in self.pets.all():
            balance += pet.balance()
        return balance


# Pet data
class Species(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        _("species"), max_length=100, null=False, blank=False, unique=True
    )
    translation_key = models.CharField(
        _("species translated"), max_length=100, null=False, blank=False
    )

    description = models.CharField(
        _("description"), max_length=100, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Race(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(
        _("race"), max_length=100, null=False, blank=False, unique=True
    )
    translation_key = models.CharField(
        _("race translated"), max_length=100, null=False, blank=False
    )

    description = models.CharField(
        _("description"), max_length=100, null=True, blank=True
    )

    species = models.ForeignKey(
        Species, on_delete=models.PROTECT, null=False, blank=False
    )

    def __str__(self):
        return self.name


class Intolerance(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ingredient = models.CharField(max_length=100, null=False, blank=False, unique=True)

    def __str__(self):
        return self.ingredient

    class Meta:
        ordering = ["ingredient"]


class Pet(models.Model):
    """
    The pet is the representation of the "customer",
    therefore the visits are related to the pet not the owner
    """

    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        Owner, null=False, blank=False, on_delete=models.CASCADE, related_name="pets"
    )
    call_name = models.CharField(
        _("call name"), max_length=100, null=False, blank=False
    )
    birth_name = models.CharField(
        _("birth name"), max_length=100, null=True, blank=True
    )
    birth_date = models.DateField(_("birth date"), null=True, blank=True)
    deceased_date = models.DateField(_("deceased date"), null=True, blank=True)

    SEX_CHOICES = (("&male;", _("male")), ("&female;", _("female")))
    sex = models.CharField(
        _("sex"),
        max_length=8,
        choices=SEX_CHOICES,
        blank=False,
        null=False,
        default="&male;",
    )

    castrated = models.BooleanField(_("castrated"), default=False)
    sterilized = models.BooleanField(_("sterilized"), default=False)

    chip_id = models.CharField(_("chip id"), max_length=20, null=True, blank=True)

    species = models.ForeignKey(Species, on_delete=models.PROTECT)
    race = models.ForeignKey(Race, on_delete=models.PROTECT, null=True, blank=True)

    intolerance = models.ManyToManyField(Intolerance, _("intolerance"), blank=True)

    note = models.CharField(_("note"), max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    insurance = models.CharField(_("insurance"), max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["call_name", "birth_date"]

    def __str__(self):
        return self.call_name + " von " + self.owner.__str__()

    def last_visit(self):
        all_visits: list = []
        for case in self.cases.all():
            if case.last_visit():
                all_visits.append(case.last_visit())

        if len(all_visits) > 0:
            return sorted(all_visits, key=lambda x: x.timestamp)[0]
        else:
            return None

    def calculate_age(self):
        today = date.today()
        if self.birth_date:
            return (
                today.year
                - self.birth_date.year
                - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            )
        else:
            return "n/a"

    def balance(self):
        balance = 0
        for case in self.cases.all():
            case_balance = case.balance()
            if case_balance > 0:
                balance += case_balance
            elif case_balance < 0:
                balance += case_balance
        return balance


TAX_CHOICES = ((7.0, "7%"), (19.0, "19%"), (0.0, _("no tax")))


#
# We distinguish in terms of a visit the actual treatment and used medication
# they are both identical in terms of attributes, so we can use one abstract object
#
class AbstractType(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.PositiveBigIntegerField(
        _("number"), null=False, blank=False, unique=True
    )
    description = models.CharField(
        _("description"), max_length=255, null=False, blank=False
    )
    price_per_unit = models.DecimalField(_("ppu"), max_digits=6, decimal_places=2)
    current = models.BooleanField(_("current"), default=True)

    def __str__(self):
        return str(self.code) + " - " + self.description

    class Meta:
        abstract = True
        ordering = ["code"]


class TreatmentType(AbstractType):
    pass


class MedicationType(AbstractType):
    pass


class ConsumablesType(AbstractType):
    pass


#
# Abstract Treatment and Medication (see above)
#
class AbstractPosition(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.ForeignKey(
        AbstractType, on_delete=models.PROTECT, related_name="%(class)s_%(app_label)s"
    )

    tax = models.DecimalField(
        choices=TAX_CHOICES,
        blank=False,
        null=False,
        default=19.0,
        max_digits=4,
        decimal_places=2,
    )

    quantity = models.DecimalField(
        _("factor"),
        max_digits=6,
        decimal_places=2,
        default=DEFAULT_FACTOR,
        validators=[MaxValueValidator(4), MinValueValidator(1)],
    )

    price_per_unit = models.DecimalField(
        _("ppu"), max_digits=6, decimal_places=2, null=True, blank=True
    )

    comment = models.CharField(_("comment"), max_length=255, null=True, blank=True)

    overwrite_gross_price = models.DecimalField(
        _("overwrite gross price"),
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    overwrite_net_price = models.DecimalField(
        _("overwrite net price"), max_digits=6, decimal_places=2, null=True, blank=True
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.type)

    def save(self, *args, **kwargs):
        if (
            self.overwrite_gross_price is not None
            and self.overwrite_net_price is not None
        ):
            raise Exception("Please only fill either one")

        return super().save()

    def net_price(self):
        """
        returns the net price
        """
        if self.overwrite_net_price:
            # net price has been overwritten
            return self.overwrite_net_price
        elif self.overwrite_net_price is None and self.overwrite_gross_price is None:
            # no overwrite at all
            if self.price_per_unit:
                return self.quantity * self.price_per_unit
            else:
                return self.quantity * self.type.price_per_unit
        else:
            # gross price is overwritten
            return self.overwrite_gross_price / (1 + self.tax / 100)

    def gross_price(self):
        """
        gross including tax
        """
        if self.overwrite_gross_price:
            # gross price is overwritten
            return self.overwrite_gross_price
        elif self.overwrite_gross_price is None and self.overwrite_net_price is None:
            if self.price_per_unit:
                return round(self.quantity * self.price_per_unit * (1 + (self.tax / 100)),2)
            else:
                return round(self.quantity * self.type.price_per_unit * (1 + (self.tax / 100)),2)
        else:
            # net price is overwritten
            return round(self.overwrite_net_price * (1 + (self.tax / 100)),2)

    def included_tax(self):
        return self.gross_price() - self.net_price()

    class Meta:
        abstract = True
        ordering = ["type__code"]


class Treatment(AbstractPosition):
    type = models.ForeignKey(
        TreatmentType, on_delete=models.PROTECT, related_name="%(class)s_%(app_label)s"
    )


class Medication(AbstractPosition):
    type = models.ForeignKey(
        MedicationType, on_delete=models.PROTECT, related_name="%(class)s_%(app_label)s"
    )

    quantity = models.DecimalField(
        _("quantity"),
        max_digits=6,
        decimal_places=2,
        default=DEFAULT_FACTOR,
        validators=[MaxValueValidator(10000), MinValueValidator(0)],
    )


class Consumable(AbstractPosition):
    type = models.ForeignKey(
        ConsumablesType,
        on_delete=models.PROTECT,
        related_name="%(class)s_%(app_label)s",
    )

    quantity = models.DecimalField(
        _("quantity"),
        max_digits=6,
        decimal_places=2,
        default=DEFAULT_FACTOR,
        validators=[MaxValueValidator(10000), MinValueValidator(0)],
    )


# Case data
class Case(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    timestamp = models.DateTimeField(default=timezone.now)

    title = models.CharField(_("title"), max_length=60, null=False, blank=False)

    description = models.CharField(
        _("description"), max_length=255, null=True, blank=True
    )

    pet = models.ForeignKey(
        Pet, null=False, blank=False, on_delete=models.PROTECT, related_name="cases"
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return str(self.timestamp) + ", " + self.title

    def last_visit(self):
        return self.visits.order_by("timestamp").last()

    def balance(self):
        balance = 0
        for visit in self.visits.all():
            visit_balance = visit.balance()
            if visit_balance > 0:
                balance += visit_balance
            elif visit_balance < 0:
                balance += visit_balance
        return balance


# Visit data
class Visit(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    case = models.ForeignKey(
        Case, null=False, blank=False, on_delete=models.PROTECT, related_name="visits"
    )

    timestamp = models.DateTimeField(default=timezone.now)

    weight = models.DecimalField(
        _("weight"), max_digits=6, decimal_places=2, blank=True, null=True
    )
    size = models.DecimalField(
        _("size"), max_digits=6, decimal_places=2, blank=True, null=True
    )
    temperature = models.DecimalField(
        _("temperature"), max_digits=3, decimal_places=1, blank=True, null=True
    )

    title = models.CharField(_("title"), max_length=63, null=False, blank=False)

    anamneses = models.CharField(_("anamneses"), max_length=255, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return str(self.case.pet) + ": " + self.title

    def price(self):
        """
        return the gross price for the visit
        """
        sum = 0
        for t in self.visit_treatments.all():
            sum += t.gross_price()
        for t in self.visit_medications.all():
            sum += t.gross_price()
        for t in self.visit_consumables.all():
            sum += t.gross_price()

        return round(sum, 2)

    def balance(self):
        if hasattr(self, "payment"):
            return self.payment.amount - self.price()
        else:
            return -1 * self.price()
        
    def included_full_tax(self):
        sum = 0
        for t in self.visit_treatments.all():
            if t.tax == 19:
                sum += t.included_tax()
        for t in self.visit_medications.all():
            if t.tax == 19:
                sum += t.included_tax()
        for t in self.visit_consumables.all():
            if t.tax == 19:
                sum += t.included_tax()
        return round(sum, 2)

    def included_reduced_tax(self):
        sum = 0
        for t in self.visit_treatments.all():
            if t.tax == 7:
                sum += t.included_tax()
        for t in self.visit_medications.all():
            if t.tax == 7:
                sum += t.included_tax()
        for t in self.visit_consumables.all():
            if t.tax == 7:
                sum += t.included_tax()
        return round(sum, 2)


class VisitTreatment(Treatment):
    visit = models.ForeignKey(
        Visit,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="visit_treatments",
    )


class VisitMedication(Medication):
    visit = models.ForeignKey(
        Visit,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="visit_medications",
    )


class VisitConsumable(Consumable):
    visit = models.ForeignKey(
        Visit,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="visit_consumables",
    )


class Payment(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    visit = models.OneToOneField(Visit, on_delete=models.PROTECT)

    timestamp = models.DateField(default=date.today)

    invoice_number = models.CharField(
        _("invoice number"), max_length=255, null=True, blank=True
    )

    amount = models.DecimalField(
        _("amount"),
        max_digits=6,
        decimal_places=2,
        blank=False,
        null=False,
        default=0.0,
    )

    CASH = 1
    CARD = 2
    INVOICE = 3

    PAYMENT_TYPE_CHOICES = (
        (CASH, _("cash")),
        (CARD, _("card")),
        (INVOICE, _("invoice")),
    )

    payment_type = models.PositiveSmallIntegerField(
        _("payment type"),
        choices=PAYMENT_TYPE_CHOICES,
        blank=False,
        null=False,
        default=CASH,
    )


def increment_invoice_number():
    last_invoice = Invoice.objects.all().order_by("invoice_no").last()
    if not last_invoice:
         return "TRW0001"
    invoice_no = last_invoice.invoice_no
    invoice_int = int(invoice_no.split("TRW")[-1])
    new_invoice_int = invoice_int + 1
    new_invoice_no = "TRW" + str(new_invoice_int).zfill(4)
    return new_invoice_no


class Invoice(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    visit = models.OneToOneField(Visit, on_delete=models.PROTECT, related_name="invoice")

    invoice_no = models.CharField(_("invoice number"), max_length=12, default=increment_invoice_number, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


#
# Templates
# used to preset some treatments and medications, such as standard procedures (castration)
# to add them as a package to the visit, so the doctor does not always fill in the complete
# data
#
class Template(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    clinic = models.ForeignKey(
        Clinic,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="clinic_templates",
    )

    name = models.CharField(
        _("name"), max_length=48, null=False, blank=False, unique=True
    )
    description = models.CharField(
        _("description"), max_length=255, null=False, blank=False
    )

    def price(self):
        sum = 0
        for t in self.template_treatments.all():
            sum += t.gross_price()
        for t in self.template_medications.all():
            sum += t.gross_price()
        for t in self.template_consumables.all():
            sum += t.gross_price()

        return sum

    def __str__(self):
        return self.name + " - € " + str(round(self.price(), 2))

    class Meta:
        ordering = ["name"]


class TemplateTreatment(Treatment):
    template = models.ForeignKey(
        Template,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="template_treatments",
    )


class TemplateMedication(Medication):
    template = models.ForeignKey(
        Template,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="template_medications",
    )


class TemplateConsumable(Consumable):
    template = models.ForeignKey(
        Template,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="template_consumables",
    )


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<id>/<filename>
    if isinstance(instance, VisitDocument):
        return "{0}/{1}".format(instance.visit.id, filename)
    elif isinstance(instance, CaseDocument):
        return "{0}/{1}".format(instance.case.id, filename)
    elif isinstance(instance, PetDocument):
        return "{0}/{1}".format(instance.pet.id, filename)
    else:
        raise RuntimeError("wrong type for saving a document for")


class Document(models.Model):
    # the id for that case
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    comment = models.CharField(_("comment"), max_length=255, null=True, blank=True)

    document = models.FileField(upload_to=user_directory_path)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def filename(self):
        return os.path.basename(self.document.name)

    def delete(self):
        os.remove(self.document.path)
        return super(Document, self).delete()

    class Meta:
        abstract = True
        ordering = ["created"]


class VisitDocument(Document):
    visit = models.ForeignKey(
        Visit,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="visit_documents",
    )


class CaseDocument(Document):
    case = models.ForeignKey(
        Case,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="case_documents",
    )


class PetDocument(Document):
    pet = models.ForeignKey(
        Pet,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="pet_documents",
    )
