import questionary
from rich.console import Console
from rich.panel import Panel

from exporter import export_to_excel
from invoice import InvoiceParseError, show_invoices
from models import Invoice
from reader import (
    read_xml_file,
    read_xml_folder,
    read_zip_file,
    read_zip_folder,
)
from ui import MENU_STYLE, ask_file, ask_folder

console = Console()

XML_FILETYPES = [
    ('Facturas XML', '*.xml'),
    ('Todos los archivos', '*.*'),
]

ZIP_FILETYPES = [
    ('Archivos ZIP', '*.zip'),
    ('Todos los archivos', '*.*'),
]


def choose_output(invoices: list[Invoice], errors: list[str]) -> None:
    """Permite mostrar, exportar o volver al menú principal."""
    if errors:
        console.print(
            f'[yellow]Se encontraron {len(errors)} errores.[/yellow]',
        )
        for error in errors:
            console.print(f'[red]- {error}[/red]')

    if not invoices:
        console.print('[yellow]No se encontraron facturas válidas.[/yellow]')
        return

    option = questionary.select(
        '¿Qué deseas hacer?',
        choices=[
            'Ver resultados en consola',
            'Exportar a Excel',
            'Volver al menú principal',
        ],
        style=MENU_STYLE,
    ).ask()

    if option is None or option == 'Volver al menú principal':
        return

    if option == 'Ver resultados en consola':
        show_invoices(invoices)
    else:
        export_to_excel(invoices, errors)


def choose_folder_output(invoices: list[Invoice], errors: list[str]) -> None:
    """Permite exportar las facturas de una carpeta o volver al menú."""
    option = questionary.select(
        '¿Qué deseas hacer?',
        choices=[
            'Exportar a Excel',
            'Volver al menú principal',
        ],
        style=MENU_STYLE,
    ).ask()

    if option is None or option == 'Volver al menú principal':
        return

    export_to_excel(invoices, errors)


def process_single_xml() -> None:
    """Lee un archivo XML elegido por el usuario."""
    path = ask_file(
        'Selecciona un archivo XML',
        'Ruta del archivo XML',
        XML_FILETYPES,
    )

    if path is None:
        return

    if not path.is_file() or path.suffix.lower() != '.xml':
        console.print('[red]Debes seleccionar un archivo XML.[/red]')
        return

    try:
        invoice = read_xml_file(path)
        choose_output([invoice], [])
    except (InvoiceParseError, OSError) as exc:
        console.print(f'[red]Error al leer el XML: {exc}[/red]')


def process_single_zip() -> None:
    """Lee un archivo ZIP elegido por el usuario."""
    path = ask_file(
        'Selecciona un archivo ZIP',
        'Ruta del archivo ZIP',
        ZIP_FILETYPES,
    )

    if path is None:
        return

    if not path.is_file() or path.suffix.lower() != '.zip':
        console.print('[red]Debes seleccionar un archivo ZIP.[/red]')
        return

    invoices, errors = read_zip_file(path)
    choose_output(invoices, errors)


def process_xml_folder() -> None:
    """Lee todos los XML de una carpeta elegida por el usuario."""
    folder = ask_folder(
        'Selecciona la carpeta con archivos XML',
        'Ruta de la carpeta con archivos XML',
    )

    if folder is None:
        return

    if not folder.is_dir():
        console.print('[red]Debes seleccionar una carpeta.[/red]')
        return

    invoices, errors = read_xml_folder(folder)

    console.print(f'Facturas encontradas: {len(invoices)}')
    console.print(f'Errores: {len(errors)}')

    choose_folder_output(invoices, errors)


def process_zip_folder() -> None:
    """Lee todos los ZIP de una carpeta elegida por el usuario."""
    folder = ask_folder(
        'Selecciona la carpeta con archivos ZIP',
        'Ruta de la carpeta con archivos ZIP',
    )

    if folder is None:
        return

    if not folder.is_dir():
        console.print('[red]Debes seleccionar una carpeta.[/red]')
        return

    invoices, errors = read_zip_folder(folder)

    console.print(f'Facturas encontradas: {len(invoices)}')
    console.print(f'Errores: {len(errors)}')

    choose_folder_output(invoices, errors)


MAIN_CHOICES = {
    'Leer un archivo XML': process_single_xml,
    'Leer un archivo ZIP': process_single_zip,
    'Leer una carpeta con múltiples XML': process_xml_folder,
    'Leer una carpeta con múltiples ZIP': process_zip_folder,
    'Salir': None,
}


def run_menu() -> None:
    """Ejecuta el menú principal hasta que el usuario salga."""
    while True:
        console.print(
            Panel(
                '[bold cyan]LECTURA DE FACTURAS ELECTRÓNICAS DIAN[/bold cyan]',
                title='Menú principal',
                border_style='cyan',
            ),
        )

        option = questionary.select(
            '',
            choices=list(MAIN_CHOICES),
            style=MENU_STYLE,
        ).ask()

        if option is None or option == 'Salir':
            console.print('[cyan]Hasta luego.[/cyan]')
            break

        try:
            MAIN_CHOICES[option]()
        except (OSError, ValueError) as exc:
            console.print(f'[red]Error: {exc}[/red]')

        console.print()
