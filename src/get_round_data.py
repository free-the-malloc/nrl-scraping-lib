from bs4 import BeautifulSoup
from selenium import webdriver
import time

from src.get_match_data import get_match_data

def get_round_data(round: int,year: int, attributes: list[str]) -> list[dict]:
    url = f"https://www.nrl.com/draw/?competition=111&round={round}&season={year}"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--blink-settings=imagesEnabled=false')
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(10)
    
    # Request the page a maximum of 3 times before quitting
    for i in range(3):
        try:
            driver.get(url)
        except:
            driver.quit()
            continue
    
        page_source = driver.page_source
        driver.quit()

        time.sleep(2)

        soup = BeautifulSoup(page_source, "html.parser")
        
        # Get each match tile
        matches = soup.find_all("div", class_="match o-rounded-box o-shadowed-box")

        # Array to hold the stats from each match in the round
        round_data = []

        for match in matches:
            # Get the extension for the match
            match_extension = match.find("a", class_="match--highlighted u-flex-column u-flex-align-items-center u-width-100")

            match_general = {}
            
            attribute_tag = ["h3", "p", 
                            "p", "div", 
                            "p", "div"]
            
            attribute_class = ["u-visually-hidden", "match-header__title", 
                            "match-team__name--home", "match-team__score--home", 
                            "match-team__name--away", "match-team__score--away"]
            
            attribute_name = ["Details","Date",
                            "Home","Home Score",
                            "Away","Away Score"]
            
            match_general["Round"] = round

            for i in range(0,6):
                match_general[attribute_name[i]] = match.find(attribute_tag[i],class_=attribute_class[i]).text.strip()

            match_general["Details"] = match_general["Details"].replace("Match: ","")            
            match_general["Home Score"] = int(match_general["Home Score"].replace("Scored","").replace("points","").strip())
            match_general["Away Score"] = int(match_general["Away Score"].replace("Scored","").replace("points","").strip())

            # Get the statistics for the match
            match_stats = get_match_data(match_extension["href"],attributes)
            
            # If the stats from a round couldn't be scraped, return none
            if match_stats == None:
                return None
            # Otherwise append the match stats to the array
            round_data.append({**match_general,**match_stats})
        return round_data
    
    return None
