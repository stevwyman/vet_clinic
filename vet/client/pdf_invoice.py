import os

from django.utils.formats import date_format
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


from fpdf import FPDF

from logging import getLogger

from .models import Clinic, Owner, Pet, Visit, Invoice

logger = getLogger(__name__)

TEXT_BODY = "Roboto"
TEXT_ADDRESS = "Courier"
TEXT_FOOTER = "Roboto"


class InvoiceDocument(FPDF):
    """
    using DIN 5008 Form A
    """

    _clinic: Clinic = None
    _visit: Visit = None
    _owner: Owner = None
    _pet: Pet = None

    def __init__(self, visit: Visit):
        super().__init__("portrait", "mm", "A4")

        self._visit = visit
        self._pet = self._visit.case.pet
        self._owner = self._pet.owner
        self._clinic = self._owner.clinic

        logger.info(f"Initialize invoice for {self._visit} - {self._clinic}")

        self.set_margins(left=25, top=17, right=20)

        path_regular = os.path.join(settings.BASE_DIR, "Roboto-Regular.ttf")
        path_medium = os.path.join(settings.BASE_DIR, "Roboto-Medium.ttf")

        self.add_font(TEXT_BODY, "", path_regular, uni=True)
        self.add_font(TEXT_BODY, "b", path_medium, uni=True)

    def header(self):
        # self.line(20, 44.7, 105, 44.7)

        path_qr = os.path.join(settings.BASE_DIR, "qr-code.png")
        self.image(path_qr, x=175, y=14, w=10, h=10, type="", link="")

        self.line(0, 87, 7, 87)
        self.line(0, 148.5, 15, 148.5)
        self.line(0, 87 + 105, 7, 87 + 105)

        # Add an address
        self.set_font(family=TEXT_BODY, size=16)
        self.cell(0, 0, txt=self._clinic.title, align="C", ln=1)

        self.set_font(family=TEXT_BODY, size=8)
        self.cell(0, 10, txt=self._clinic.slogan, align="C", ln=1)

    def footer(self):
        self.set_y(-25)

        self.set_font(family=TEXT_FOOTER, size=8)

        table_data = (
            ("", "", ""),
            (self._clinic.name, "", self._clinic.phone),
            (
                self._clinic.street_number,
                "IBAN: " + self._clinic.iban,
                self._clinic.mail,
            ),
            (
                self._clinic.zip_code + " " + self._clinic.city,
                "BIC: " + self._clinic.bic,
                self._clinic.url,
            ),
        )

        with self.table(
            text_align=("LEFT", "CENTER", "RIGHT"),
            first_row_as_headings=False,
            line_height=self.font_size * 1.2,
            borders_layout="SINGLE_TOP_LINE",
        ) as table:
            for data_row in table_data:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

    def generate_invoice(self, form):
        BORDER = 0

        try:
            invoice = self._visit.invoice
        except ObjectDoesNotExist:
            invoice = Invoice(visit=self._visit)
            invoice.save()

        self.add_page()

        # sender
        self.set_font(family=TEXT_BODY, size=6)
        self.cell(0, 13, txt="", ln=1, border=BORDER)
        self.cell(0, 5, txt=self._clinic.return_address, ln=1, border=BORDER)

        self.set_font(family=TEXT_ADDRESS, size=10)
        # address
        self.cell(
            0,
            5,
            txt="{} {}".format(self._owner.firstname, self._owner.lastname),
            ln=1,
            border=BORDER,
        )
        self.cell(
            0,
            5,
            txt=self._owner.postal_street_number,
            ln=1,
            border=BORDER,
        )
        self.cell(
            0,
            5,
            txt="{} {}".format(self._owner.postal_zipcode, self._owner.postal_city),
            ln=1,
            border=BORDER,
        )
        self.cell(0, 27, txt="{}".format(""), ln=1, border=BORDER)

        # date
        self.set_font(family=TEXT_BODY, style="", size=10)
        if form:
            self.cell(0, 6, txt=form.cleaned_data["date"], align="R", ln=1)
        else:
            self.cell(
                0,
                6,
                txt=date_format(
                    self._visit.timestamp, format="SHORT_DATE_FORMAT", use_l10n=True
                ),
                align="R",
                ln=1,
            )
        self.cell(0, 25, txt="{}".format(""), ln=1, border=BORDER)

        self.set_font(family=TEXT_BODY, style="B", size=10)
        if form:
            self.cell(
                0,
                6,
                txt="{} {}".format(_("invoice number"), form.cleaned_data["invoice"]),
                ln=1,
            )
        else:
            self.cell(0, 6, txt="{} {}".format(_("invoice number"), invoice.invoice_no), ln=1)
        self.cell(0, 12, txt="{}".format(""), ln=1, border=BORDER)

        self.set_font(family=TEXT_BODY, size=10)
        if form:
            self.cell(0, 6, txt=form.cleaned_data["address"], ln=1)
        else:
            self.cell(
                0,
                5,
                txt="Sehr geehrte(r) {} {},".format(
                    self._owner.firstname, self._owner.lastname
                ),
                ln=1,
            )
        self.cell(0, 12, txt="{}".format(""), ln=1, border=BORDER)

        if form:
            self.cell(0, 6, txt=form.cleaned_data["text"], ln=1)
        else:
            self.multi_cell(
                0,
                6,
                txt="für die Behandlung ({}) von {} erlaube ich mir die folgenden Positionen in Rechnung zu stellen: ".format(
                    self._visit.title, self._pet.call_name
                ),
                ln=1,
            )
        self.cell(0, 6, txt="{}".format(""), ln=1, border=BORDER)

        self.set_font(family=TEXT_BODY, size=7)
        table_data = list()
        first = ("Position", "Brutto Preis")
        table_data.append(first)

        for t in self._visit.visit_treatments.all():
            row = list()
            row.append(str(t))
            row.append("€ " + str(round(t.gross_price(), 2)))
            table_data.append(row)

        for t in self._visit.visit_medications.all():
            row = list()
            row.append(str(t))
            row.append("€ " + str(round(t.gross_price(), 2)))
            table_data.append(row)

        for t in self._visit.visit_consumables.all():
            row = list()
            row.append(str(t))
            row.append("€ " + str(round(t.gross_price(), 2)))
            table_data.append(row)

        last_before = ("", "")
        table_data.append(last_before)
        sum = "Summe inklusive MWSt. "
        if self._visit.included_full_tax() != 0:
            sum += f"[19% € {self._visit.included_full_tax()}]"
        if self._visit.included_reduced_tax() != 0:
            sum += f"[7% € {self._visit.included_reduced_tax()}]"
        last = sum, "€ " + str(self._visit.price())
        table_data.append(last)

        with self.table(
            text_align=("LEFT", "RIGHT"),
            line_height=self.font_size * 1.7,
            width=130,
            col_widths=(100, 30),
            borders_layout="SINGLE_TOP_LINE",
        ) as table:
            for data_row in table_data:
                if data_row == table_data[-1]:
                    self.set_font(family=TEXT_BODY, size=9)
                else:
                    self.set_font(family=TEXT_BODY, size=7)
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

        self.set_font(family=TEXT_BODY, size=10)
        self.cell(0, 12, txt="{}".format(""), ln=1, border=BORDER)
        self.cell(0, 6, txt=_("greet"), ln=1)
        self.cell(0, 18, txt="{}".format(""), ln=1, border=BORDER)
        self.cell(0, 6, txt=self._clinic.title, ln=1)
