# Analysis of government contracts

**Project Description: Collection and analysis of data from the public procurement website to identify inflated purchase prices.**

**Overview:** Contracts Parser is a Python project designed for automated parsing of contract data from a government procurement website. The project consists of several scripts that perform various tasks related to parsing and analyzing contract data.

**Project Files:**

1. `lib_gz.py`: A library module containing utility functions for data conversion, file handling, and logging. Other scripts in the project import functions from this module to perform specific tasks.
    
2. `st1_contracts_parsing.py`: A script focused on parsing contract data from a procurement website. It retrieves contract information, extracts relevant data from HTML pages, and stores the parsed data in a database for further analysis or reporting.
    
3. `st2_get_contract_numbers_by_item_names.py`: This script retrieves contract numbers based on specific item names. It reads a list of item names from a file, searches for corresponding contracts on a procurement website, and saves the contract numbers to output files.
    
4. `st3_get_positions_for_analysis.py`: This script parses position details from contracts for analysis purposes. It retrieves contracts, extracts position data from their web pages, and stores the parsed data in a database or output files. The collected position data can be further analyzed or used to generate reports.

**Technologies:**

- Python
- BeautifulSoup
- SQLite

**Installation and Setup:** To set up the Contracts Analysis Toolkit locally, follow these steps:

1. Clone the project repository from GitHub.
2. Install the required dependencies and libraries as specified in the project's `requirements.txt` file.
3. Configure the project settings, such as database connections or file paths, as per your environment.
4. Run the desired script(s) using a Python interpreter.