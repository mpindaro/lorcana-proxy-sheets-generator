import sys
import requests
import os
from urllib.request import urlretrieve
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import argparse


def get_rarity_rank(rarity):
    """
    Converts a rarity string to a numerical rank.
    """
    rarity_ranking = {
        "promo": 6,
        "enchanted": 5,
        "super_rare": 4,
        "rare": 3,
        "uncommon": 2,
        "common": 1
    }
    return rarity_ranking.get(rarity, 0)

def generate_pdf_with_custom_cards(image_folder, output_pdf_path):
    page_width, page_height = A4
    card_width, card_height = 2.5 * inch, 3.5 * inch  # Card dimensions in points

    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    images = [f for f in os.listdir(image_folder) if f.endswith('.png')]
    images_per_row = int(page_width // card_width)
    images_per_column = int(page_height // card_height)
    x_offset = (page_width - (images_per_row * card_width)) / 2
    y_offset = (page_height - (images_per_column * card_height)) / 2

    def draw_cutting_marks(x, y):
        """Draw cutting lines and corners at (x, y) for each card."""
        c.setStrokeColorRGB(0,0,0)  # Set color to black
        c.setLineWidth(1)
        # Vertical cutting line
        c.line(x, y - 6, x, y + card_height + 6)
        c.line(x + card_width, y - 6, x + card_width, y + card_height + 6)
        # Horizontal cutting line
        c.line(x - 6, y, x + card_width + 6, y)
        c.line(x - 6, y + card_height, x + card_width + 6, y + card_height)
        # Drawing corners; adjust 'corner_length' as needed
        corner_length = 12
        for dx in (0, card_width):
            for dy in (0, card_height):
                # Horizontal part of the corner
                c.line(x + dx, y + dy, x + dx + (corner_length if dx == 0 else -corner_length), y + dy)
                # Vertical part of the corner
                c.line(x + dx, y + dy, x + dx, y + dy + (corner_length if dy == 0 else -corner_length))

    for index, image_name in enumerate(images):
        if index != 0 and index % (images_per_row * images_per_column) == 0:
            c.showPage()
        row = index % images_per_row
        column = (index // images_per_row) % images_per_column
        x = x_offset + row * card_width
        y = page_height - y_offset - (column + 1) * card_height

        image_path = os.path.join(image_folder, image_name)
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            if img_width > img_height:  # Image is horizontal
                img = img.rotate(90, expand=True)
                img.save(image_path)  # Overwrite the original image with the rotated one

        # Draw the image
        c.drawImage(image_path, x, y, width=card_width, height=card_height, preserveAspectRatio=True)
        # Draw cutting lines and corners
        draw_cutting_marks(x, y)

    c.save()
    print(f"PDF generated: {output_pdf_path}")

def download_and_convert_image(url, path_to_save):
    """
    Downloads an image from a URL, converts it to PNG, and saves it to the specified path.
    """
    try:
        # Download the image
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        # Convert the image to PNG using Pillow
        with Image.open(BytesIO(response.content)) as img:
            img.convert('RGBA').save(path_to_save, 'PNG')
        
        return True
    except Exception as e:
        print(f"Error downloading or converting image from {url}: {e}")
        return False


def parse_search_text_with_quantity(text):
    """
    Parses the search text to extract quantities, names, and titles.
    """
    lines = text.strip().split("\n")
    search_items = []
    for line in lines:
        parts = line.split(" ", 1)
        if len(parts) == 2:
            try:
                quantity = int(parts[0])
                name_title = parts[1]
                if "-" in name_title:
                    name, title = name_title.split(" - ", 1)
                    search_items.append((quantity, name.strip(), title.strip()))
                else:
                    search_items.append((quantity, name_title.strip(), None))
            except ValueError:
                continue  # Skip lines that do not start with a number
    return search_items

def generate_image_links(objects, search_text, keep_rarest=False):
    """
    Generates image links based on the parsed search text.
    Optionally filters to keep only the rarest (or most recent if rarities match) cards.
    """
    search_items = parse_search_text_with_quantity(search_text)
    image_links = []

    for quantity, name, title in search_items:
        matching_cards = [obj for obj in objects if obj.get("name") == name and (title is None or obj.get("title") == title)]
        
        if keep_rarest and matching_cards:
            # Define rarity ranking
            def get_rarity_rank(rarity):
                return {"promo": 6, "enchanted": 5, "super_rare": 4, "rare": 3, "uncommon": 2, "common": 1}.get(rarity, 0)
            
            # Sort cards by rarity and update date
            matching_cards.sort(key=lambda x: (get_rarity_rank(x["rarity"]), x["updated_at"]), reverse=True)
            
            # Select the top card after sorting
            selected_cards = matching_cards[:1]
        else:
            selected_cards = matching_cards
        
        for card in selected_cards:
            image_links.extend([card["image"]] * quantity)

    return image_links

def get_deck(path, deckname, keep_rarest=False):
    """
    Main function to get the deck, request card data, and save images.
    """
    try:
        with open(path, 'r') as file:
            contents = file.read()
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        return

    print(f"Searching for {path}:")
    print(contents)

    url = "https://lorcania.com/api/cardsSearch"
    payload = {
        "colors": [],
        "sets": [],
        "traits": [],
        "keywords": [],
        "costs": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10
        ],
        "inkwell": [],
        "rarity": [],
        "language": "English",
        "options": [],
        "sorting": "default"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # This will raise an exception for HTTP errors
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return

    data = response.json()
    if not data:
        print("No data returned from API.")
        return

    image_links = generate_image_links(data["cards"], contents, keep_rarest)
    print(f"Found {len(image_links)} images.")
    if not os.path.exists(deckname):
        os.makedirs(deckname)

    for i, link in enumerate(image_links, start=1):
        # Construct the PNG file name by replacing the original extension with ".png"
        # and append a unique identifier (the loop index) to allow duplicates.
        image_name = f"{i}_{os.path.splitext(os.path.basename(link))[0]}.png"
        file_path = os.path.join(deckname, image_name)
        
        # Download the image, convert it to PNG, and save.
        if download_and_convert_image(link, file_path):
            print(f"{i}. {image_name} downloaded and converted to PNG.")
        else:
            print(f"Failed to process {link}.")
    
    generate_pdf_with_custom_cards(deckname, f"{deckname}.pdf")



    print("All images processed.")

if __name__ == "__main__":
     # Create the parser
    parser = argparse.ArgumentParser(description='Generate a PDF with custom cards.')

    # Positional arguments
    parser.add_argument('path', type=str, help='Path to the text file containing card information.')
    parser.add_argument('deckname', type=str, help='Name of the deck (and output folder).')

    # Optional arguments
    parser.add_argument('-kr', '--keep_rarest', action='store_true', help='Keep only the rarest card for each name.')

    # Parse arguments
    args = parser.parse_args()
    
    get_deck(args.path, args.deckname, args.keep_rarest)
