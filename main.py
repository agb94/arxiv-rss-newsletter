import requests
import xml.etree.ElementTree as ET
# import wordcloud
# from nltk.corpus import stopwords

CAT = "cs.SE"
KEYWORDS = {
    "LLM": ["Large Language Model", "LLM"],
    "FL": ["Fault Localization", "Fault Localisation", "FL"],
    "APR": ["Automated Program Repair", "APR"]
}

def get_arxiv_rss_feed(category):
    url = f"https://rss.arxiv.org/rss/{category}"
    response = requests.get(url=url)
    status = response.status_code     
    if status == 200:
        root = ET.fromstring(response.text)
        return root

def parse_arxiv_rss_feed_xml(root):
    channel = root.find("channel")
    title = channel.find("title").text
    lastBuildDate = channel.find("lastBuildDate").text

    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
    papers = []
    for item in channel.iter("item"):
        properties = {}
        for prob in ["title", "link", "description", "category"]:
            properties[prob] = item.find(prob).text
        properties["authors"] = item.find("dc:creator", namespaces=ns).text.split(", ")

        papers.append(properties)
    return title, lastBuildDate, papers

def assign_tags(papers, keywords):
    for paper in papers:
        abstract = paper["description"]
        paper["tags"] = list()
        for tag in keywords:
            # for each tag that represents a list of keywords,
            # if one of the keywords appears in the abstract,
            # assign the tag to the paper
            if any([k in abstract for k in keywords[tag]]):
                paper["tags"].append(tag)

def to_markdown(papers, output_path):
    sorted_papers = sorted(papers, key=lambda paper: -len(paper["tags"]))

    with open(output_path, 'w') as f:
        f.write(f"# {title}, {date}\n\n")
        for paper in sorted_papers:
            f.write(f"## [{paper['title']}]({paper['link']}) [[pdf]({paper['link'].replace('abs', 'pdf') + '.pdf'})]\n\n")
            f.write("Authors: " + ", ".join([f"{a}" for a in paper["authors"]]) + "\n\n")
            if paper["tags"]:
                f.write("Tags: " + ", ".join([f"`{tag}`" for tag in paper["tags"]]) + "\n\n")
            f.write("Abstract:".join(paper["description"].split("Abstract:")[1:]) + "\n\n")

if __name__ == "__main__":

    root = get_arxiv_rss_feed(CAT)
    title, date, papers = parse_arxiv_rss_feed_xml(root)
    assign_tags(papers, KEYWORDS)
    to_markdown(papers, "crawling_results.md")    