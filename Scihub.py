import logging
import csv
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

class SciHub:
    def __init__(self, doi: str, path: Path, csv_path: Path, log_path: Path, url: str = 'https://sci-hub.se/', timeout: int = 60, rate_limit: int = 10):
        self.url = url
        self.timeout = timeout
        self.path = path
        self.csv_path = csv_path
        self.rate_limit = rate_limit  # Time in seconds between requests
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        self.payload = {'sci-hub-plugin-check': '', 'request': doi}

        # Set up logging
        logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.last_request_time = 0

    def _throttle_requests(self):
        """Throttle requests to comply with rate limits."""
        elapsed_time = time.time() - self.last_request_time
        if elapsed_time < self.rate_limit:
            time.sleep(self.rate_limit - elapsed_time)

    def _send_request(self) -> requests.Response | None:
        """Send a POST request to the Sci-Hub server."""
        self._throttle_requests()
        try:
            res = requests.post(self.url, headers=self.headers, data=self.payload, timeout=self.timeout)
            res.raise_for_status()
            self.last_request_time = time.time()
            return res
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None

    def _extract_url(self, response: requests.Response) -> str | None:
        """Extract the URL of the PDF from the response."""
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            content_url = soup.find(id='pdf').get('src', '').replace('#navpanes=0&view=FitH', '').replace('//', '/')
            if not content_url.endswith('.pdf'):
                raise ValueError("Invalid PDF URL format.")
            return f'https://sci-hub.se{content_url}' if content_url.startswith('/downloads') else f'https:/{content_url}'
        except (AttributeError, ValueError) as e:
            self.logger.error(f"Failed to extract PDF URL: {e}")
            return None

    def _save_to_csv(self, doi: str, pdf_url: str) -> None:
        """Save the DOI and PDF URL to a CSV file."""
        try:
            with self.csv_path.open('a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([doi, pdf_url])
        except IOError as e:
            self.logger.error(f"Failed to write to CSV: {e}")

    def _download_pdf(self, pdf_url: str, pdf_path: Path) -> None:
        """Download the PDF from the extracted URL."""
        try:
            pdf_content = requests.get(pdf_url, headers=self.headers).content
            pdf_path.write_bytes(pdf_content)
            self.logger.info(f"PDF downloaded successfully: {pdf_path.name}")
        except requests.RequestException as e:
            self.logger.error(f"Failed to download PDF: {e}")

    def fetch(self):
        """Fetch the PDF for the given DOI."""
        self.logger.info(f"Fetching DOI: {self.payload['request']}")
        response = self._send_request()
        pdf_url = self._extract_url(response)
        if not pdf_url:
            self.logger.warning(f"No PDF URL found for DOI: {self.payload['request']}")
            return

        pdf_name = pdf_url.split('/')[-1]
        pdf_path = self.path / pdf_name
        self._download_pdf(pdf_url, pdf_path)
        self._save_to_csv(self.payload['request'], pdf_url)
