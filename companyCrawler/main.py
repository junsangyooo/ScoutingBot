from companyCrawler.physical_intelligence.main import run as run_pi
# from companyCrawler.skilld_ai.main import run as run_skilld

def crawlCompany():
    results = []
    results.append(run_pi())
    #results.append(run_skilld())

if __name__ == "__main__":
    crawlCompany()