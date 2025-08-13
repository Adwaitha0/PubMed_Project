PubMed Papers Fetcher

This project fetches research papers from PubMed based on a given search query and extracts details such as the title, publication date, non-academic authors, company affiliations, and corresponding author emails. The results are saved in a CSV file.


📁 Project Structure

pubmed_papers/

│── fetch_papers.py   # Main script to fetch and process PubMed papers

│── pyproject.toml    # Poetry configuration file for managing dependencies

│── poetry.lock       # Dependency lock file

│── .gitignore        # Files and directories to be ignored in Git

│── README.md         # Project documentation

│── papers.csv        # Output file containing fetched paper details


⚙️ Installation and Setup

1.Ensure you have Python 3.12+ and Poetry installed.

2.Install Poetry (if not installed):

    pip install poetry

3.Install Dependencies 

    3.1.Clone the repository:
    
        git clone https://github.com/yourusername/pubmed-papers-fetcher.git
        
    3.2.cd pubmed-papers-fetcher
    
    3.3.Install dependencies using Poetry:
    
        poetry install

    Required Ddependencies:
    
        requests → Fetch data from PubMed API.
        
        pandas → Save data in a CSV file.
        
        xmltodict → Parse XML responses from PubMed API.


4.To run the script, activate the virtual environment and execute the program:

    poetry run python fetch_papers.py

5.Enter a search query when prompted, and the results will be saved in papers.csv.



🛠️ Tools & Libraries Used

Python 3.12+: Core programming language.

Poetry: Dependency management (Docs).

Requests: For making HTTP requests to PubMed API (Docs).

re (Regular Expressions): For extracting email addresses from text (Docs).

CSV Module: To store the results in a structured format.


📝 Notes
The script fetches a limited number of papers (default: 5). Modify max_results in fetch_papers.py if needed.

Some corresponding author emails may not be available in PubMed’s metadata.

Ensure you have an active internet connection while running the script.
