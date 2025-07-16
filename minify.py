#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def minify_html(html):
    # Eliminar comentarios HTML
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

    # Minificar contenido de <script>...</script>
    def minify_script(match):
        script = match.group(1)
        # Quitar comentarios de línea
        script = re.sub(r'//.*', '', script)
        # Quitar comentarios multilínea
        script = re.sub(r'/\*.*?\*/', '', script, flags=re.DOTALL)
        # Quitar espacios y líneas en blanco
        script = re.sub(r'\s+', ' ', script)
        return f"<script>{script.strip()}</script>"

    html = re.sub(r"<script>(.*?)</script>", minify_script, html, flags=re.DOTALL)

    # Quitar espacios entre tags
    html = re.sub(r'>\s+<', '><', html)
    # Quitar espacios múltiples
    html = re.sub(r'\s{2,}', ' ', html)
    return html.strip()

def format_size(bytes_count):
    if bytes_count < 1024:
        return f"{bytes_count} B"
    elif bytes_count < 1024**2:
        return f"{bytes_count / 1024:.1f} KB"
    else:
        return f"{bytes_count / 1024**2:.1f} MB"

def main():
    if len(sys.argv) != 2:
        print("Uso: minify.py archivo.html")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
        print(f"❌ Archivo no encontrado: {input_path}")
        sys.exit(1)

    output_path = input_path.with_name(input_path.stem + "_minified.html")
    original = input_path.read_text(encoding="utf-8")
    minified = minify_html(original)

    input_size = len(original.encode("utf-8"))
    output_size = len(minified.encode("utf-8"))
    saved_bytes = input_size - output_size
    saved_pct = 100 * saved_bytes / input_size if input_size else 0

    output_path.write_text(minified, encoding="utf-8")

    print(f"✅ HTML minificado guardado en: {output_path}")
    print(f"📦 Tamaño original:  {format_size(input_size)}")
    print(f"📉 Tamaño minificado: {format_size(output_size)}")
    print(f"💾 Ahorro: {format_size(saved_bytes)} ({saved_pct:.1f}%)")

if __name__ == "__main__":
    main()
