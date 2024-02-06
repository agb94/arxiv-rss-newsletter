import requests
import xml.etree.ElementTree as ET

CAT = "cs.SE"

def get_rss_feed(category):
    url = f"https://rss.arxiv.org/rss/{category}"
    response = requests.get(url=url)
    status = response.status_code     
    if status == 200:
        root = ET.fromstring(response.text)
        return root

if __name__ == "__main__":

    root = get_rss_feed(CAT)

    text_properties = ["title", "link", "description", "category"]
    channel = root.find("channel")
    title = channel.find("title").text
    lastBuildDate = channel.find("lastBuildDate").text

    ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
    papers = []
    for item in channel.iter("item"):
        properties = {}
        for prob in ["title", "link", "description", "category"]:
            properties[prob] = item.find(prob).text
        properties["authors"] = []
        for author in item.find("dc:creator", namespaces=ns).iter("a"):
            properties["authors"].append(author.text)
        papers.append(properties)
        
    with open("crawling_results.md", 'w') as f:
        f.write(f"# {title}, {lastBuildDate}\n\n")

        for paper in papers:
            f.write(f"## [{paper['title']}]({paper['link']})\n\n")
            f.write(", ".join(paper.authors) + "\n\n")
            f.write(paper.description)
