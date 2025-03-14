
import argparse
from pubmed import fetch_papers, fetch_paper_details, save_to_csv

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Fetch PubMed papers by keyword.")
    parser.add_argument("query", type=str, help="Search keyword for PubMed papers")
    parser.add_argument("--max", type=int, default=10, help="Number of results to fetch (default: 10)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (prints execution details)")
    parser.add_argument("--file", type=str, help="Specify a filename to save the results (if not provided, prints to console)")

    args = parser.parse_args()

    if args.debug:
        print(f"Debug: Query = {args.query}, Max Results = {args.max}")

    # Fetch paper IDs
    paper_ids = fetch_papers(args.query, args.max)
    if not paper_ids:
        print("No results found.")
        return

    if args.debug:
        print(f"Debug: Retrieved {len(paper_ids)} paper IDs: {paper_ids}")

    # Fetch paper details
    papers = fetch_paper_details(paper_ids)

    if args.debug:
        print(f"Debug: Retrieved {len(papers)} papers with details.")

    # Save or print results
    if args.file:
        save_to_csv(papers, args.file)
        print(f"Results saved to {args.file}")
    else:
        # Print to console if no file is specified
        for paper in papers:
            print("\n----------------------")
            print(f"PubmedID: {paper['PubmedID']}")
            print(f"Title: {paper['Title']}")
            print(f"Abstract: {paper['Abstract']}")
            print(f"Publication Date: {paper['Publication Date']}")
            print(f"Non-academic Author(s): {paper.get('Non-academic Author(s)', 'N/A')}")
            print(f"Company Affiliation(s): {paper.get('Company Affiliation(s)', 'N/A')}")
            print(f"Corresponding Author Email: {paper['Corresponding Author Email']}")
        print("\n----------------------")

if __name__ == "__main__":
    main()




