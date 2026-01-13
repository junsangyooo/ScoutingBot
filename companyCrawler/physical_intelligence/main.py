from member_crawler import memberCrawler
from member_compare import memberCompare
from research_crawler import researchCrawler
from research_compare import researchCompare
from position_crawler import positionCrawler
from position_compare import positionCompare
def run():
    # Crawl and Compare Members
    members = memberCrawler()
    member_result = memberCompare(members)

    # Crawl and Compare Researches
    researches = researchCrawler()
    research_result = researchCompare(researches)

    # Crawl and Compare Positions
    positions = positionCrawler()
    position_result = positionCompare(positions)
    return {
        "company": "Physical Intelligence",
        "team": member_result,
        "research": research_result,
        "position": position_result
    }

if __name__ == "__main__":
    print(run())