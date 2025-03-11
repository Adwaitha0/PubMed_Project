import requests
import xmltodict
import json
import csv
import re
from typing import List, Dict

# API Endpoints
PUBMED_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def fetch_papers(query: str, max_results: int = 10) -> List[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "xml"
    }

    response = requests.get(PUBMED_API, params=params)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    data = xmltodict.parse(response.text)
    paper_ids = data['eSearchResult'].get('IdList', {}).get('Id', [])
    return paper_ids


def extract_email(text):
    if not isinstance(text, str):  
        text = json.dumps(text)  

    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return email_match.group(0) if email_match else "Not Available"



def fetch_paper_details(paper_ids: List[str]) -> List[Dict]:
    if not paper_ids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(paper_ids),
        "retmode": "xml"
    }

    response = requests.get(PUBMED_FETCH_API, params=params)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}")

    data = xmltodict.parse(response.text)
    
    papers = []
    for article in data['PubmedArticleSet']['PubmedArticle']:
        medline = article['MedlineCitation']
        article_info = medline['Article']
        
        # Extract Pubmed ID
        pubmed_id = medline['PMID']['#text']

        # Extract Publication Date
        pub_date = article_info.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        year = pub_date.get("Year", "Unknown")
        month = pub_date.get("Month", "Unknown")
        day = pub_date.get("Day", "Unknown")
        publication_date = f"{year}-{month}-{day}"

        # Extract Title
        title = article_info.get("ArticleTitle", "No title available")

        # Extract Author Information
        authors = article_info.get("AuthorList", {}).get("Author", [])
        if not isinstance(authors, list):
            authors = [authors]  # Convert single author to list
        
        non_academic_authors = []
        company_affiliations = []
        corresponding_author_email = "Not Available"

        # Check additional fields for emails
        possible_email_sources = []

        for author in authors:
            if isinstance(author, dict):
                last_name = author.get("LastName", "")
                fore_name = author.get("ForeName", "")
                full_name = f"{last_name} {fore_name}".strip()

                affiliation_info = author.get("AffiliationInfo", [])
                if isinstance(affiliation_info, dict): 
                    affiliation_info = [affiliation_info]  # Convert to list
                
                for aff in affiliation_info:
                    affiliation = aff.get("Affiliation", "")

                    # Identify non-academic authors (based on keywords)
                    if any(word in affiliation.lower() for word in ["pharma", "biotech", "inc", "ltd", "corp"]):
                        non_academic_authors.append(full_name)
                        company_affiliations.append(affiliation)

                    # Extract email from affiliation
                    possible_email_sources.append(affiliation)

        # Check `CommentsCorrections` Field for Corresponding Author Email
        comments_corrections = medline.get("CommentsCorrectionsList", {}).get("CommentsCorrections", {})
        if isinstance(comments_corrections, dict):
            comments_corrections = [comments_corrections]
        for item in comments_corrections:
            if "correspondence" in str(item).lower():
                possible_email_sources.append(str(item))

        #  Check `Abstract` Field for Corresponding Author Email
        abstract_text = article_info.get("Abstract", {}).get("AbstractText", "")
        if isinstance(abstract_text, list):
            abstract_text = " ".join([item.get("#text", "") if isinstance(item, dict) else str(item) for item in abstract_text])
        possible_email_sources.append(abstract_text)


        #  Extract email from all possible sources
        for source in possible_email_sources:
            email = extract_email(source)
            if email != "Not Available":
                corresponding_author_email = email
                break

        paper_info = {
            "PubmedID": pubmed_id,
            "Title": title,
            "Publication Date": publication_date,
            "Non-academic Author(s)": ", ".join(non_academic_authors) if non_academic_authors else "None",
            "Company Affiliation(s)": ", ".join(set(company_affiliations)) if company_affiliations else "None",
            "Corresponding Author Email": corresponding_author_email
        }

        papers.append(paper_info)

    return papers


def save_to_csv(papers: List[Dict], filename: str = "papers.csv"):
    """Save the research papers to a CSV file with structured format."""
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "PubmedID", "Title", "Publication Date", "Non-academic Author(s)", 
            "Company Affiliation(s)", "Corresponding Author Email"
        ])
        writer.writeheader()
        writer.writerows(papers)
    print(f"✅ Data saved to {filename}")


if __name__ == "__main__":
    query = input("🔍 Enter search query: ")
    paper_ids = fetch_papers(query, max_results=5)

    if not paper_ids:
        print("❌ No papers found.")
    else:
        papers = fetch_paper_details(paper_ids)

        for idx, paper in enumerate(papers, start=1):
            print(f"\n{idx}. {paper['Title']}")
            print(f"   🏛 Publication Date: {paper['Publication Date']}")
            print(f"   👨‍🔬 Non-academic Authors: {paper['Non-academic Author(s)']}")
            print(f"   🏢 Company Affiliations: {paper['Company Affiliation(s)']}")
            print(f"   📧 Corresponding Author Email: {paper['Corresponding Author Email']}")

        save_to_csv(papers)
