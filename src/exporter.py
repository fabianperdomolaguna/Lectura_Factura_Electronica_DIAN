from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from models import LABELS, SEPARATOR, Invoice
from ui import ask_path, ask_route, browse_save_file

console = Console()


def choose_save_folder() -> Path | None:
    """Elige la carpeta destino del Excel: actual, ruta escrita o volver."""
    mode = ask_route(
        '¿En qué carpeta quieres guardar el Excel?',
        [
            'Carpeta del proyecto (actual)',
            'Escribir la ruta de la carpeta',
            'Volver al menú principal',
        ],
    )

    if mode is None:
        return None

    if mode == 'Carpeta del proyecto (actual)':
        return Path.cwd()

    return ask_path('Ruta de la carpeta de destino', must_be_dir=True)


def ask_save_path() -> Path | None:
    """Pide dónde guardar el Excel: explorador, carpeta y nombre escritos, o volver."""
    suggested = Path(f'facturas_{datetime.now().astimezone():%Y}.xlsx')

    mode = ask_route(
        '¿Dónde quieres guardar el Excel?',
        [
            'Guardar con el explorador',
            'Escribir la ruta',
            'Volver al menú principal',
        ],
    )

    if mode is None:
        return None

    if mode == 'Guardar con el explorador':
        return browse_save_file(suggested)

    folder = choose_save_folder()

    if folder is None:
        return None

    name = (
        Prompt.ask(
            'Nombre del archivo Excel',
            default=suggested.name,
        )
        .strip()
        .strip('"')
    )

    if not name:
        console.print('[red]El nombre no puede estar vacío.[/red]')
        return None

    if Path(name).suffix.lower() != '.xlsx':
        name = f'{name}.xlsx'

    output_path = folder / name

    if output_path.exists():
        answer = ask_route(
            f'Ya existe {output_path}. ¿Qué quieres hacer?',
            ['Sobrescribirlo', 'Cancelar'],
        )

        if answer != 'Sobrescribirlo':
            console.print('[yellow]Exportación cancelada.[/yellow]')
            return None

    return output_path


def export_to_excel(
    invoices: list[Invoice],
    errors: list[str] | None = None,
) -> None:
    """Exporta las facturas y los errores a un archivo Excel."""
    import pandas as pd

    errors = errors or []

    if not invoices and not errors:
        console.print('[yellow]No hay datos para exportar.[/yellow]')
        return

    output_path = ask_save_path()

    if output_path is None:
        return

    df = pd.DataFrame(
        [asdict(invoice) for invoice in invoices],
        columns=[campo for campo, _ in LABELS],
    ).rename(columns=dict(LABELS))

    for column in ['Valor_Base', 'Impuestos', 'Valor_Total']:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(
                writer,
                sheet_name='Facturas',
                index=False,
            )

            fecha_col = [campo for campo, _ in LABELS].index('fecha') + 1
            sheet = writer.sheets['Facturas']
            for row in sheet.iter_rows(min_row=2, min_col=fecha_col, max_col=fecha_col):
                for cell in row:
                    cell.number_format = 'yyyy-mm-dd'

            if errors:
                pd.DataFrame({'Error': errors}).to_excel(
                    writer,
                    sheet_name='Errores',
                    index=False,
                )

        console.print(
            f'\n{SEPARATOR}\n'
            '[green]Excel creado correctamente:[/green]\n'
            f'{output_path.resolve()}\n'
            f'{SEPARATOR}',
        )

    except (OSError, PermissionError, ValueError) as exc:
        console.print(f'[red]No se pudo crear el Excel: {exc}[/red]')
