from datetime import date
from decimal import Decimal, InvalidOperation
from xml.etree.ElementTree import Element, ParseError

from defusedxml.common import DefusedXmlException
from defusedxml.ElementTree import fromstring
from rich.console import Console

from models import LABELS, NOT_FOUND, SEPARATOR, Invoice

console = Console()

NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
}


class InvoiceParseError(Exception):
    """Error al interpretar un XML como factura electrónica."""


def get_text(root: Element, path: str) -> str | None:
    """Obtiene el texto de una etiqueta XML o None si falta."""
    element = root.find(path, NAMESPACES)

    if element is not None and element.text:
        return element.text.strip()

    return None


def to_decimal(text: str | None) -> Decimal | None:
    """Convierte un monto a Decimal; None si falta o no es numérico."""
    if text is None:
        return None

    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def to_date(text: str | None) -> date | None:
    """Convierte una fecha ISO (YYYY-MM-DD) a date; None si falta o no es válida."""
    if text is None:
        return None

    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def extract_invoice(xml_content: bytes | str) -> Invoice:
    """Extrae los datos principales de una factura electrónica."""
    try:
        root = fromstring(xml_content)
    except (ParseError, DefusedXmlException) as exc:
        message = f'XML inválido: {exc}'
        raise InvoiceParseError(message) from exc

    # Si es un AttachedDocument, buscar la factura UBL anidada.
    if root.tag.endswith('}AttachedDocument'):
        descriptions = root.findall(
            './/cac:Attachment/cac:ExternalReference/cbc:Description',
            NAMESPACES,
        )

        invoice_root = None

        for description in descriptions:
            if not description.text:
                continue

            try:
                candidate = fromstring(description.text)
            except ParseError, DefusedXmlException:
                continue

            if candidate.tag.endswith('}Invoice'):
                invoice_root = candidate
                break

        if invoice_root is None:
            message = 'No se encontró una factura UBL dentro del AttachedDocument.'
            raise InvoiceParseError(message)

        root = invoice_root

    if not root.tag.endswith('}Invoice'):
        message = 'El documento XML no corresponde a una factura UBL.'
        raise InvoiceParseError(message)

    return Invoice(
        fecha=to_date(get_text(root, 'cbc:IssueDate')),
        id_factura=get_text(root, 'cbc:ID'),
        uuid=get_text(root, 'cbc:UUID'),
        proveedor=get_text(
            root,
            'cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:RegistrationName',
        ),
        nit_proveedor=get_text(
            root,
            'cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID',
        ),
        valor_base=to_decimal(
            get_text(root, 'cac:LegalMonetaryTotal/cbc:LineExtensionAmount'),
        ),
        impuestos=to_decimal(get_text(root, 'cac:TaxTotal/cbc:TaxAmount')),
        valor_total=to_decimal(
            get_text(root, 'cac:LegalMonetaryTotal/cbc:PayableAmount'),
        ),
    )


def show_invoices(invoices: list[Invoice]) -> None:
    """Muestra las facturas encontradas en la consola."""
    if not invoices:
        console.print('[yellow]No se encontraron facturas.[/yellow]')
        return

    for invoice in invoices:
        console.print()
        console.print(SEPARATOR)

        for campo, etiqueta in LABELS:
            value = getattr(invoice, campo)

            if value is None:
                value = NOT_FOUND

            if value != '':
                console.print(f'[bold]{etiqueta}:[/bold] {value}')

        console.print(SEPARATOR)

    console.print()
    console.print(f'Total de facturas: {len(invoices)}')
