"""
swap_ascii_for_gif.py

Troca a arte ASCII (bloco <text class="ascii">) dos SVGs do template
"neofetch style" (dark_mode.svg / light_mode.svg) por um GIF embutido
como base64, mantendo intactos os dados dinâmicos gerados pelo today.py.

Uso:
    python swap_ascii_for_gif.py caminho/para/seu.gif

Rode este script dentro da pasta do seu fork clonado (onde estão
dark_mode.svg e light_mode.svg). Ele sobrescreve os dois arquivos.
"""

import base64
import re
import sys
from pathlib import Path

ASCII_BLOCK_PATTERN = re.compile(
    r'<text x="15" y="30" fill="[^"]*" class="ascii">.*?</text>',
    re.DOTALL,
)

EXISTING_IMAGE_PATTERN = re.compile(
    r'<image x="15" y="15"[^>]*/>',
)

IMG_X, IMG_Y = 15, 15
IMG_WIDTH, IMG_HEIGHT = 360, 500

FIT_MODE = "slice" 


def build_image_tag(gif_path: Path) -> str:
    gif_bytes = gif_path.read_bytes()
    size_mb = len(gif_bytes) / (1024 * 1024)
    if size_mb > 5:
        print(f"Aviso: o GIF tem {size_mb:.1f}MB. Vale considerar comprimir "
              f"pra deixar o carregamento do perfil mais rápido.")

    b64 = base64.b64encode(gif_bytes).decode("ascii")
    data_uri = f"data:image/gif;base64,{b64}"
    preserve = "xMidYMid slice" if FIT_MODE == "slice" else "xMidYMid meet"

    return (
        f'<image x="{IMG_X}" y="{IMG_Y}" width="{IMG_WIDTH}" '
        f'height="{IMG_HEIGHT}" preserveAspectRatio="{preserve}" '
        f'href="{data_uri}"/>'
    )


def swap_in_file(svg_path: Path, image_tag: str) -> None:
    if not svg_path.exists():
        print(f"Aviso: {svg_path.name} não encontrado nesta pasta, pulando.")
        return

    svg_text = svg_path.read_text(encoding="utf-8")

    if ASCII_BLOCK_PATTERN.search(svg_text):
        new_svg = ASCII_BLOCK_PATTERN.sub(image_tag, svg_text, count=1)
    elif EXISTING_IMAGE_PATTERN.search(svg_text):
        new_svg = EXISTING_IMAGE_PATTERN.sub(image_tag, svg_text, count=1)
    else:
        print(f"Aviso: nem a arte ASCII nem uma imagem anterior foram "
              f"encontradas em {svg_path.name}. Nenhuma mudança feita.")
        return

    svg_path.write_text(new_svg, encoding="utf-8")
    print(f"OK: {svg_path.name} atualizado com o GIF.")


def main():
    if len(sys.argv) != 2:
        print("Uso: python swap_ascii_for_gif.py caminho/para/seu.gif")
        sys.exit(1)

    gif_path = Path(sys.argv[1])
    if not gif_path.exists():
        print(f"Erro: arquivo '{gif_path}' não encontrado.")
        sys.exit(1)

    image_tag = build_image_tag(gif_path)

    for filename in ("dark_mode.svg", "light_mode.svg"):
        swap_in_file(Path(filename), image_tag)


if __name__ == "__main__":
    main()