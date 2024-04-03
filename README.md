# Proxy Sheet Generator

The Proxy Sheet Generator is a tool designed for creating proxy sheets for non-commercial purposes. Proxy sheets allow users to print out replicas of original cards for activities such as playtesting or collecting. This tool fetches card images from the "https://lorcania.com/api/cardsSearch" endpoint, ensuring up-to-date and high-quality proxies.

## Disclaimer

This tool is intended for non-commercial use only. Users are urged to respect the intellectual property rights of the original card creators. Please use this tool responsibly.

## License

This project is licensed under the MIT License.

## Prerequisites

-   Python installed on your system.
-   Internet connection to access card data from https://lorcania.com/api/cardsSearch.

## Installation

1. Clone or download this repository to your local machine.
2. Open a terminal or command prompt and navigate to the project directory.
3. Install the required dependencies by running: `pip install -r requirements.txt`.

## Usage

1. Prepare your decklist in a .txt file following this format:

    ```
    2 Rapunzel - Letting Down Her Hair
    3 Pongo - Ol' Rascal
    3 Aladdin - Street Rat
    3 Stampede
    ```

    Each line should specify the quantity of the card followed by the card name. If the card does not have a specific title, only include the card name.

2. Ensure you have the `getDeck.py` script in your project directory.
3. Generate the proxy sheet by running:

    ```
    python getDeck.py <path_to_txt_file> <deckname> [--keep_rarest]
    ```

    - `<path_to_txt_file>`: Path to your .txt file containing the decklist.
    - `<deckname>`: The name of your deck, which will be used as the PDF file name and for naming the folder containing the card images in PNG format.
    - `--keep_rarest`: An optional flag to keep only the rarest card for each name.

The proxy sheet will be saved in an output directory in A4 PDF format, alongside a folder containing individual card images in PNG format.

## Integration with https://lorcania.com/api/cardsSearch

This tool utilizes the "https://lorcania.com/api/cardsSearch" endpoint to fetch card images. When generating proxy sheets, the script makes requests to this endpoint with the card names from your decklist. Ensure your card names match those on the Lorcania site to successfully retrieve the images.

## Contribution

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the tool or suggest new features.
