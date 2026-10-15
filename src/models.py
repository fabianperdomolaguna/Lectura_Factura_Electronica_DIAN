from dataclasses import dataclass
from datetime import date
from decimal import Decimal

NOT_FOUND = 'No encontrado'
SEPARATOR = '-' * 60


@dataclass(frozen=True, slots=True)
class Invoice:
    """Modelo de una factura electrónica leída."""

    fecha: date | None
    id_factura: str | None
    uuid: str | None
    proveedor: str | None
    nit_proveedor: str | None
    valor_base: Decimal | None
    impuestos: Decimal | None
    valor_total: Decimal | None
    zip: str = ''
    archivo: str = ''


LABELS: tuple[tuple[str, str], ...] = (
    ('fecha', 'Fecha'),
    ('id_factura', 'Id_Factura'),
    ('uuid', 'UUID'),
    ('proveedor', 'Proveedor'),
    ('nit_proveedor', 'NIT_Proveedor'),
    ('valor_base', 'Valor_Base'),
    ('impuestos', 'Impuestos'),
    ('valor_total', 'Valor_Total'),
    ('zip', 'ZIP'),
    ('archivo', 'Archivo'),
)
