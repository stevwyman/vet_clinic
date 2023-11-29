from django.test import TestCase

from decimal import Decimal

from .models import TreatmentType, MedicationType, ConsumablesType, Template, Invoice, Clinic, TemplateTreatment, Owner, Pet, Visit, Species, Case

# Create your tests here.
class AbstractTypes(TestCase):

    def test_create_treatment_type(self):
        treatment_1 = TreatmentType.objects.create(code=1, description="a simple treatment", price_per_unit=12.34 )
        treatment_2 = TreatmentType.objects.create(code=2, description="another treatment", price_per_unit=56.78 )

        self.assertIsNotNone(treatment_1)
        self.assertEqual(treatment_1.code, 1)
        self.assertEqual(treatment_1.description, "a simple treatment")
        self.assertEqual(treatment_1.price_per_unit, 12.34)

        treatment_1_read = TreatmentType.objects.get(code=1)
        self.assertIsNotNone(treatment_1)
        self.assertEqual(treatment_1_read.code, 1)
        self.assertEqual(treatment_1_read.description, "a simple treatment")
        self.assertEqual(treatment_1_read.price_per_unit, Decimal("12.34"))

        treatment_2_read = TreatmentType.objects.get(code=2)
        self.assertIsNotNone(treatment_1)
        self.assertEqual(treatment_2_read.code, 2)
        self.assertEqual(treatment_2_read.description, "another treatment")
        self.assertEqual(treatment_2_read.price_per_unit, Decimal("56.78"))

    def test_create_medication_type(self):
        medication_1 = MedicationType.objects.create(code=1, description="a simple medication", price_per_unit=12.34 )
        medication_2 = MedicationType.objects.create(code=2, description="another medication", price_per_unit=56.78 )

        self.assertIsNotNone(medication_1)
        self.assertEqual(medication_1.code, 1)
        self.assertEqual(medication_1.description, "a simple medication")
        self.assertEqual(medication_1.price_per_unit, 12.34)

        medication_1_read = MedicationType.objects.get(code=1)
        self.assertIsNotNone(medication_1_read)
        self.assertEqual(medication_1_read.code, 1)
        self.assertEqual(medication_1_read.description, "a simple medication")
        self.assertEqual(medication_1_read.price_per_unit, Decimal("12.34"))

        medication_2_read = MedicationType.objects.get(code=2)
        self.assertIsNotNone(medication_2_read)
        self.assertEqual(medication_2_read.code, 2)
        self.assertEqual(medication_2_read.description, "another medication")
        self.assertEqual(medication_2_read.price_per_unit, Decimal("56.78"))

    def test_create_consumable_type(self):
        consumable_1 = ConsumablesType.objects.create(code=1, description="a simple consumable", price_per_unit=12.34 )
        consumable_2 = ConsumablesType.objects.create(code=2, description="another consumable", price_per_unit=56.78 )

        self.assertIsNotNone(consumable_1)
        self.assertEqual(consumable_1.code, 1)
        self.assertEqual(consumable_1.description, "a simple consumable")
        self.assertEqual(consumable_1.price_per_unit, 12.34)

        consumable_1_read = ConsumablesType.objects.get(code=1)
        self.assertIsNotNone(consumable_1_read)
        self.assertEqual(consumable_1_read.code, 1)
        self.assertEqual(consumable_1_read.description, "a simple consumable")
        self.assertEqual(consumable_1_read.price_per_unit, Decimal("12.34"))

        consumable_2_read = ConsumablesType.objects.get(code=2)
        self.assertIsNotNone(consumable_2_read)
        self.assertEqual(consumable_2_read.code, 2)
        self.assertEqual(consumable_2_read.description, "another consumable")
        self.assertEqual(consumable_2_read.price_per_unit, Decimal("56.78"))

class Templates(TestCase):

    def setUp(self) -> None:

        Clinic.objects.create(external_id = "abc")

        TreatmentType.objects.create(code=1, description="a simple treatment", price_per_unit=12.34 )
        MedicationType.objects.create(code=1, description="a simple medication", price_per_unit=12.34 )
        ConsumablesType.objects.create(code=1, description="a simple consumable", price_per_unit=12.34 )

    def test_create_template(self):

        clinic = Clinic.objects.get(external_id = "abc")
        print(clinic)
        treatment_type = TreatmentType.objects.get(code = 1)
        print(treatment_type)

        template = Template.objects.create(clinic=clinic)

        TemplateTreatment.objects.create(template=template, type=treatment_type)

        print(template.price)


class Invoices(TestCase):

    def test_increment(self):

        dog = Species.objects.create(name="Dog")

        clinic = Clinic.objects.create(external_id = "abc")

        owner = Owner.objects.create(clinic=clinic)

        pet = Pet.objects.create(species=dog, owner=owner)

        case_1 = Case.objects.create(pet=pet)
        case_2 = Case.objects.create(pet=pet)

        visit_1 = Visit.objects.create(case=case_1)
        visit_2 = Visit.objects.create(case=case_2)
        visit_3 = Visit.objects.create(case=case_2)

        invoice_1 = Invoice.objects.create(visit=visit_1)
        invoice_2 = Invoice.objects.create(visit=visit_2)
        invoice_3 = Invoice.objects.create(visit=visit_3)

        print(invoice_1.invoice_no)
        print(invoice_2.invoice_no)
        print(invoice_3.invoice_no)
