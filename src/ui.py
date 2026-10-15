import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog

import questionary
from rich.console import Console
from rich.prompt import Prompt

console = Console()

MENU_STYLE = questionary.Style(
    [
        ('question-mark', 'cyan'),
        ('pointer', 'fg:cyan bold'),
        ('highlighted', 'fg:cyan bold'),
        ('answer', 'fg:cyan bold'),
    ]
)

ROUTE_CHOICES = ['Buscar con el explorador', 'Escribir la ruta', 'Volver al menú principal']


def _ask_dialog(dialog: Callable[..., str], **kwargs: str) -> Path | None:
    """Ejecuta un diálogo del SO, siempre visible encima de las ventanas."""
    root = tk.Tk()
    root.withdraw()
    root.attributes(topmost=True)

    try:
        selected = dialog(**kwargs)
    finally:
        root.destroy()

    if not selected:
        console.print('[yellow]Selección cancelada.[/yellow]')
        return None

    return Path(selected)


def browse_file(title: str, filetypes: list[tuple[str, str]]) -> Path | None:
    """Abre el explorador de archivos del sistema operativo."""
    return _ask_dialog(filedialog.askopenfilename, title=title, filetypes=filetypes)


def browse_folder(title: str) -> Path | None:
    """Abre el explorador de carpetas del sistema operativo."""
    return _ask_dialog(filedialog.askdirectory, title=title)


def browse_save_file(suggested: Path) -> Path | None:
    """Abre el diálogo Guardar como del sistema operativo."""
    return _ask_dialog(
        filedialog.asksaveasfilename,
        title='Guardar Excel como',
        defaultextension='.xlsx',
        initialfile=suggested.name,
        filetypes=[('Archivo Excel', '*.xlsx')],
    )


def ask_route(message: str, choices: list[str]) -> str | None:
    """Pregunta al usuario con un selector; devuelve None si cancela o vuelve."""
    answer = questionary.select(message, choices=choices, style=MENU_STYLE).ask()

    if answer is None or answer == 'Volver al menú principal':
        return None

    return answer


def ask_path(message: str, *, must_be_dir: bool = False) -> Path | None:
    """Solicita y valida una ruta escrita por el usuario."""
    raw_path = Prompt.ask(message).strip().strip('"')
    path = Path(raw_path).expanduser()

    exists = path.is_dir() if must_be_dir else path.exists()

    if not exists:
        console.print('[red]La ruta indicada no existe.[/red]')
        return None

    return path


def ask_file(
    title: str,
    prompt: str,
    filetypes: list[tuple[str, str]],
) -> Path | None:
    """Permite elegir un archivo con el explorador, escribir su ruta o volver."""
    mode = ask_route('¿Cómo quieres indicar el archivo?', ROUTE_CHOICES)

    if mode is None:
        return None

    if mode == 'Buscar con el explorador':
        return browse_file(title, filetypes)

    return ask_path(prompt)


def ask_folder(title: str, prompt: str) -> Path | None:
    """Permite elegir una carpeta con el explorador, escribir su ruta o volver."""
    mode = ask_route('¿Cómo quieres indicar la carpeta?', ROUTE_CHOICES)

    if mode is None:
        return None

    if mode == 'Buscar con el explorador':
        return browse_folder(title)

    return ask_path(prompt)
