from pathlib import Path
from scihub_downloader import SciHub  # Import the SciHub class

# Define paths
output_path = Path("downloads")
csv_file = Path("doi_pdfs.csv")
log_file = Path("scihub.log")
dois_file = Path("dois.txt")

def ensure_directory_exists(directory: Path) -> None:
    """Ensure the output directory exists."""
    directory.mkdir(exist_ok=True)

def read_dois_from_file(dois_file: Path) -> list[str]:
    """Read DOIs from the provided file."""
    if not dois_file.exists():
        raise FileNotFoundError(f"Error: '{dois_file}' not found. Please create the file and add DOIs.")
    with open(dois_file, "r") as file:
        return [line.strip() for line in file if line.strip()]

def process_dois(dois: list[str], output_path: Path, csv_file: Path, log_file: Path) -> None:
    """Process each DOI using the SciHub downloader."""
    for doi in dois:
        print(f"Processing DOI: {doi}")
        downloader = SciHub(doi, output_path, csv_file, log_file, rate_limit=10)
        try:
            downloader.fetch()
        except Exception as e:
            print(f"Error with DOI {doi}: {e}")

def main():
    """Main function to handle DOI processing."""
    try:
        ensure_directory_exists(output_path)
        dois = read_dois_from_file(dois_file)
        process_dois(dois, output_path, csv_file, log_file)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
