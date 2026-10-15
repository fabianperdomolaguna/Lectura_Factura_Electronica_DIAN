import zipfile
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from rich.progress import Progress

from invoice import InvoiceParseError, extract_invoice
from models import Invoice


def read_xml_file(path: Path) -> Invoice:
    """Lee una factura desde un archivo XML."""
    invoice = extract_invoice(path.read_bytes())
    return replace(invoice, archivo=path.name)


def read_zip_file(path: Path) -> tuple[list[Invoice], list[str]]:
    """Lee las facturas XML encontradas dentro de un ZIP."""
    invoices = []
    errors = []

    try:
        with zipfile.ZipFile(path) as archive:
            xml_files = [
                name
                for name in archive.namelist()
                if name.lower().endswith('.xml') and not name.endswith('/')
            ]

            if not xml_files:
                errors.append(f'{path.name}: NO contiene archivos XML.')

            for name in xml_files:
                try:
                    invoice = extract_invoice(archive.read(name))
                    invoices.append(
                        replace(invoice, zip=path.name, archivo=name),
                    )
                except (InvoiceParseError, OSError, zipfile.BadZipFile) as exc:
                    errors.append(f'{path.name} / {name}: {exc}')

    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f'{path.name}: {exc}')

    return invoices, errors


def read_folder(
    folder: Path,
    suffix: str,
    read_one: Callable[[Path], tuple[list[Invoice], list[str]]],
) -> tuple[list[Invoice], list[str]]:
    """Lee todos los archivos con el sufijo indicado, con barra de progreso."""
    invoices = []
    errors = []

    paths = [
        path
        for path in sorted(folder.rglob('*'))
        if path.is_file() and path.suffix.lower() == suffix
    ]

    with Progress(transient=True) as progress:
        task = progress.add_task('Leyendo...', total=len(paths))

        for path in paths:
            progress.update(task, description=f'Leyendo {path.name}')

            found, failed = read_one(path)

            invoices.extend(found)
            errors.extend(failed)

            progress.advance(task)

    return invoices, errors


def read_xml_folder(folder: Path) -> tuple[list[Invoice], list[str]]:
    """Lee todos los XML de una carpeta y sus subcarpetas."""

    def read_one(path: Path) -> tuple[list[Invoice], list[str]]:
        try:
            invoice = read_xml_file(path)
            return [replace(invoice, archivo=str(path.relative_to(folder)))], []
        except (InvoiceParseError, OSError) as exc:
            return [], [f'{path}: {exc}']

    return read_folder(folder, '.xml', read_one)


def read_zip_folder(folder: Path) -> tuple[list[Invoice], list[str]]:
    """Lee todos los ZIP de una carpeta y sus subcarpetas."""
    return read_folder(folder, '.zip', read_zip_file)
