<h1 align="center">Lectura Información Factura Electrónica - DIAN</h1>

<p align="center">
  <img src="https://img.shields.io/github/license/fabianperdomolaguna/Lectura_Factura_Electronica_DIAN?style=for-the-badge" alt="alt text">
  <img src="https://img.shields.io/badge/Python->_3.14-FFFF00?style=for-the-badge&logo=Python&logoColor=white" alt="alt text">
</p>

---

Este proyecto es una aplicación de consola que lee facturas electrónicas de la DIAN en formato XML — ya sea el archivo `.xml` directamente, un `.zip` que contenga el XML en su interior, o carpetas completas — y extrae información relevante como proveedor, NIT, valores, impuestos y UUID. Los resultados se visualizan en la consola o se exportan a un archivo `.xlsx` para su posterior análisis.

---

## ✨ Features

- 🗂️ **Menú interactivo:** Navega las opciones con las teclas **↑** y **↓** y confirma con **Enter**; la opción seleccionada se resalta en pantalla.
- 📂 **Selector del sistema:** Elige archivos y carpetas con el explorador gráfico de Windows o Linux, o escribe la ruta a mano si lo prefieres.
- 📦 **XML y ZIP:** Procesa facturas en `.xml` sueltos, archivos `.zip` con uno o varios XML en su interior, y carpetas completas de XML o de ZIP.
- 🔙 **Nunca te pierdes:** Todas las pantallas ofrecen "Volver al menú principal" para corregir una opción equivocada sin reiniciar el programa.
- 📊 **Salida clara en consola:** Cada factura se muestra como pares "Campo: valor" con separadores, fácil de leer.
- 📈 **Barra de progreso:** Al leer carpetas grandes ves el avance en una sola línea (por ejemplo, `357/1000`) sin llenar la consola.
- 📁 **Excel donde tú quieras:** Exporta a `.xlsx` eligiendo con el explorador o la ruta dónde guardarlo, con nombre sugerido por fecha. Incluye una hoja de facturas y, si los hay, una hoja de errores.
- 🎨 **Interfaz con color:** Salida en terminal formateada con `rich` y `questionary`.

---

## 🚀 Requisitos

- Python 3.14 o superior
- [uv](https://docs.astral.sh/uv/) como gestor de dependencias

## 🛠️ Instalación

Clona el repositorio y sincroniza las dependencias:

```bash
git clone https://github.com/fabianperdomolaguna/Lectura_Factura_Electronica_DIAN.git
cd Lectura_Factura_Electronica_DIAN
uv sync
```

## ▶️ Uso

Inicia la aplicación:

```bash
uv run src/main.py
```

1. Con las teclas **↑** y **↓** elige una opción del menú y presiona **Enter**.
2. Indica el archivo o carpeta: selecciona **"Buscar con el explorador"** para usar el diálogo gráfico del sistema, o **"Escribir la ruta"** para digitarla.
3. Revisa los datos en consola o elige **"Exportar a Excel"** y decide dónde guardarlo.
4. En cualquier momento puedes elegir **"Volver al menú principal"** para cambiar de opción, o presionar **Ctrl + C** para salir.

<h1 align="center">
  <img src=".github/images/app_template.png" />
</h1>
