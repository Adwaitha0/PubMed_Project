import argparse
import requests
import xml.etree.ElementTree as ET
import re
import csv

def fetch_papers(query: str, max_results: int = 10):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=xml"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    return [id_elem.text for id_elem in root.findall(".//Id")]

def extract_email(text: str):
    if not text:
        return "No Email Found"
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else "No Email Found"

def fetch_paper_details(paper_ids):
    """Fetches details for given PubMed paper IDs and extracts relevant fields."""
    ids = ",".join(paper_ids)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
    response = requests.get(url)
    root = ET.fromstring(response.content)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        pubmed_id = article.find(".//PMID").text if article.find(".//PMID") is not None else "Unknown"
        title_elem = article.find(".//ArticleTitle")
        abstract_elem = article.find(".//AbstractText")
        pub_date_elem = article.find(".//PubDate")

        title = title_elem.text if title_elem is not None else "No Title"
        abstract = abstract_elem.text if abstract_elem is not None else "No Abstract"
        publication_date = pub_date_elem.find("Year").text if pub_date_elem is not None and pub_date_elem.find("Year") is not None else "Unknown"

        # Extract Author Information
        authors = []
        affiliations = []
        non_academic_authors = []
        company_affiliations = []
        possible_email_sources = []

        for author in article.findall(".//Author"):
            last_name = author.find("LastName")
            fore_name = author.find("ForeName")
            full_name = f"{(last_name.text if last_name is not None else '')} {(fore_name.text if fore_name is not None else '')}".strip()
            authors.append(full_name)

            affiliation_elem = author.find(".//Affiliation")
            if affiliation_elem is not None:
                affiliation = affiliation_elem.text.strip()
                affiliations.append(affiliation)

                # Identify company affiliations based on keywords
                if any(word in affiliation.lower() for word in ["pharma", "biotech", "inc", "ltd", "corp", "company"]):
                    non_academic_authors.append(full_name)
                    company_affiliations.append(affiliation)

                # Possible email sources
                possible_email_sources.append(affiliation)

        # Extract email from potential sources
        email = "Not Available"
        for source in possible_email_sources:
            email = extract_email(source)
            if email != "Not Available":
                break

        papers.append({
            "PubmedID": pubmed_id,
            "Title": title,
            "Abstract": abstract,
            "Publication Date": publication_date,
            "Non-academic Author(s)": ", ".join(non_academic_authors) if non_academic_authors else "None",
            "Company Affiliation(s)": ", ".join(set(company_affiliations)) if company_affiliations else "None",
            "Corresponding Author Email": email
        })

    return papers



def save_to_csv(papers, filename="papers.csv"):
    """Saves the paper details to a CSV file."""
    if not papers:
        print("No data to save.")
        return
    print(f"Saving {len(papers)} papers to {filename}...")
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["PubmedID", "Title", "Abstract", "Publication Date", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"])
        writer.writeheader()
        writer.writerows(papers)
    print("CSV file saved successfully.")



def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed papers by keyword.")
    parser.add_argument("query", type=str, help="Search keyword for PubMed papers")
    parser.add_argument("--max", type=int, default=10, help="Number of results to fetch (default: 10)")
    args = parser.parse_args()

    paper_ids = fetch_papers(args.query, args.max)
    if not paper_ids:
        print("No results found.")
        return

    papers = fetch_paper_details(paper_ids)
    save_to_csv(papers)
    print("Results saved to papers.csv")

if __name__ == "__main__":
    main()





