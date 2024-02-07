import requests
import xml.etree.ElementTree as ET
# import wordcloud
# from nltk.corpus import stopwords

CAT = "cs.SE"

def get_rss_feed(category):
    url = f"https://rss.arxiv.org/rss/{category}"
    response = requests.get(url=url)
    status = response.status_code     
    if status == 200:
        root = ET.fromstring(response.text)
        return root

def parse_xml(root):
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
            properties["authors"].append((author.text, author.attrib["href"]))
        papers.append(properties)
    return title, lastBuildDate, papers

if __name__ == "__main__":

    root = get_rss_feed(CAT)

    title, date, papers = parse_xml(root)

    # wc = wordcloud.WordCloud(stopwords=stopwords.words('english') + ["using", "based", "code", "software", "system", "model"])
    # wc.generate(text="\n".join([p["description"] for p in papers]))
    # print(wc.words_)

    with open("crawling_results.md", 'w') as f:
        f.write(f"# {title}, {date}\n\n")

        for paper in papers:
            f.write(f"## [{paper['title']}]({paper['link']}) [[pdf]({paper['link'].replace('abs', 'pdf') + '.pdf'})]\n\n")
            f.write("Authors: " + ", ".join([f"[{a}]({l})" for a, l in paper["authors"]]) + "\n\n")
            f.write(paper["description"]+ "\n\n")

    