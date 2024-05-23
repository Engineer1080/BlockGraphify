import os
from PIL import Image, \
    ImageOps  # Falls nicht vorhanden kann man im Terminal bzw. in der Konsole dies eingeben: pip install Pillow

# Standardfarben in GameView
# Diese sollten nicht bearbeitet werden
predefined_colors = {
    (0, 0, 0): 'L',  # Schwarz
    (255, 255, 255): 'W',  # Weiß
    (255, 0, 0): 'R',  # Rot
    (255, 128, 128): 'r',  # Helles Rot
    (0, 255, 0): 'G',  # Grün
    (128, 255, 128): 'g',  # Helles Grün
    (0, 0, 255): 'B',  # Blau
    (128, 128, 255): 'b',  # Helles Blau
    (255, 255, 0): 'Y',  # Gelb
    (255, 255, 128): 'y',  # Helles Gelb
    (255, 192, 203): 'P',  # Pink
    (255, 182, 193): 'p',  # Helles Pink
    (0, 255, 255): 'C',  # Cyan
    (128, 255, 255): 'c',  # Helles Cyan
    (255, 0, 255): 'M',  # Magenta
    (255, 128, 255): 'm',  # Helles Magenta
    (255, 165, 0): 'O',  # Orange
    (255, 200, 128): 'o',  # Helles Orange
}

# Neue Farben können hier einfach definiert werden
# Die Farben sind 8-Bit-RGB-Werte (0 bis 255)
custom_colors = {
    (128, 0, 0): 'D',  # Dunkelrot
    (255, 69, 0): 'F',  # Feuerrot
    (0, 128, 0): 'H',  # Dunkelgrün
    (0, 255, 127): 'I',  # Frühlinggrün
    (0, 0, 128): 'J',  # Dunkelblau
    (70, 130, 180): 'K',  # Stahlblau
    (255, 215, 0): 'N',  # Gold
    (218, 165, 32): 'Q',  # Goldbraun
    (199, 21, 133): 'S',  # Mittelviolettrot
    (75, 0, 130): 'T',  # Indigo
    (244, 164, 96): 'U',  # Sandbraun
    (0, 191, 255): 'V',  # Himmelblau
    (128, 128, 0): 'X',  # Oliv
    (128, 0, 128): 'Z',  # Violett
    (128, 128, 128): 'G',  # Grau
    (255, 105, 180): 'f',  # Helles Feuerrot
    (144, 238, 144): 'i',  # Helles Frühlingsgrün
    (173, 216, 230): 'v',  # Helles Himmelblau
}

color_map = {**predefined_colors, **custom_colors}


def generate_java_colors_file(filepath):
    with open(filepath, 'w') as f:
        for rgb, char in custom_colors.items():
            color_string = ', '.join(str(e) for e in rgb)
            f.write(f"setColorForBlockImage('{char}', new Color({color_string}));\n")
    print(f"'{filepath}' wurde erfolgreich erstellt.")


def closest_color(rgb):
    # Die ähnlichste Farbe finden
    return min(color_map.keys(), key=lambda c: sum((sc - ic) ** 2 for sc, ic in zip(c, rgb)))


def remove_border(blockgraphic, neg_mode):
    if neg_mode:
        blockgraphic = blockgraphic.replace('W', ' ')
    else:
        blockgraphic = blockgraphic.replace('L', ' ')

    lines = blockgraphic.split("\n")

    # Finde die minimale Anzahl an führenden Leerzeichen in den Zeilen
    min_leading_spaces = min(len(line) - len(line.lstrip(' ')) for line in lines if line.strip())

    # Verringere die Einrückung aller Zeilen um die minimale Anzahl an führenden Leerzeichen
    lines = [line[min_leading_spaces:] for line in lines]

    # Entferne alle leeren Zeilen am Anfang und Ende
    while not lines[0].strip():
        lines.pop(0)
    while not lines[-1].strip():
        lines.pop(-1)

    new_blockgraphic = "\n".join(lines)

    return new_blockgraphic


def image_to_blockgraphic(image, bw_mode=False, neg_mode=False, bl_mode=False):
    # Schwarz-Weiß-Modus
    if bw_mode:
        image = image.convert('L')

    # Negativ-Modus. Invertiert Farben
    if neg_mode:
        image = ImageOps.invert(image)

    pixels = image.load()

    blockgraphic = []

    for y in range(image.height):
        line = []
        for x in range(image.width):
            color = pixels[x, y]
            if image.mode == 'L':
                color = (color, color, color)

            line.append(color_map[closest_color(color)])

        blockgraphic.append(''.join(line))

    # Erzeugt einen String aus der Blockgrafik
    blockgraphic = '\n'.join(blockgraphic)

    # Randlos-Modus
    if bl_mode:
        blockgraphic = remove_border(blockgraphic, neg_mode)

    return blockgraphic


def escape_java_string(s):
    # Für Zeilenumbrüche
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def process_images_in_directory(directory, block_size=1, bw_mode=False, neg_mode=False, bl_mode=False):
    java_commands = []
    counter = 0
    if not [f for f in os.listdir(directory) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]:
        return java_commands

    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image = Image.open(os.path.join(directory, filename)).convert('RGB')
            image = image.resize((image.width // block_size, image.height // block_size), Image.NEAREST)
            shortened_filename = ''.join([char for char in filename[:-4].upper() if char.isalpha()])
            if len(shortened_filename) == 0:
                print("Warnung: Dateiname enthält keine Buchstaben, verwende die Bezeichnung 'IMAGE'.")
                shortened_filename = "IMAGE" + str(counter)
                counter += 1
            blockgraphic = image_to_blockgraphic(image, bw_mode, neg_mode, bl_mode)
            escaped_blockgraphic = escape_java_string(blockgraphic)
            # Java-Befehl erstellen
            command = f'public static final String {shortened_filename} = "{escaped_blockgraphic}";'
            java_commands.append(command)

    return java_commands
