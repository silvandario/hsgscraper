# 🕸️ HSG Course Scraper

This project scrapes course information from the University of St. Gallen's course catalog. 

Why? 

Becasue students need answers - and thus our **chat bot** -> https://github.com/silvandario/biddingbot needs context!

## 🚀 Getting Started

The good stuff is located at hsgscraper/hsgscraper/spiders -> each master's degree has its own file for simplicity.
For example, the MBI -> getmbi.py

To start the scraping process:

1. Navigate to the `spiders` directory:
   ```bash
   cd hsgscraper/hsgscraper/spiders
   ```
2. 	Run the scraper:
   ```bash
   	python getmbi.py
   ```

The scraper opens each node of the tree structure, follows all links to the individual courses in a new tab, retrieves the link to each Kursmerkblatt, opens the Kursmerkblatt with a http get request and extracts the content in a way that the pdf is preserved! Initial attempts resulted in a choas of raw html code instead of the actual pdf. 
