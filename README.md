# 🕸️ HSG Course Scraper

This project scrapes course information from the University of St. Gallen's course catalog.

## 🚀 Getting Started

To start the scraping process:

1. Navigate to the `spiders` directory:
   ```bash
   cd spiders
   ```
2. 	Run the scraper:
   ```bash
   python getdata.py
   ```

🧪 Current Status
	•	This is a testing phase – many paths and elements are still hard-coded.
	•	The script successfully opens the Kursmerkblatt PDF (target document).
	•	Currently working on extracting and parsing PDF content.

📂 Output
	•	link to PDF
  •	PDF in crappy format
 

📌 Next Steps
	•	Dynamically extract and clean text from the downloaded PDFs.
	•	Generalize the scraper to work for all courses, not just hard-coded examples.
	•	Improve anti-bot resilience and error handling.
