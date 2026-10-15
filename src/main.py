import contextlib
import sys

from rich.console import Console

from menu import run_menu

console = Console()


def _configure_stdout() -> None:
    """Fuerza UTF-8 en la consola para mostrar bien los acentos en Windows."""
    stream = sys.stdout

    if stream is None or not hasattr(stream, 'reconfigure'):
        return

    with contextlib.suppress(ValueError, OSError):
        stream.reconfigure(encoding='utf-8', errors='replace')


def main() -> None:
    """Ejecuta el menú principal."""
    _configure_stdout()

    try:
        run_menu()
    except KeyboardInterrupt:
        console.print('\n[yellow]Programa finalizado por el usuario.[/yellow]')


if __name__ == '__main__':
    main()
