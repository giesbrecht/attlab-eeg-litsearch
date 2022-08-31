from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import math
import os
import argparse
from selenium.common.exceptions import TimeoutException
from utils import ucsb_login, scrape_searchResults

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--chrome", default=False, action="store_true",
                        help="Use Chrome *Note Proper chromedriver must be installed")

    args = parser.parse_args()

    args.chrome = True

    if args.chrome:

        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=C:\\Users\\Jordan\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")

        browser = webdriver.Chrome(executable_path=r'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe',
                                   chrome_options=options)

    else:
        browser = webdriver.Safari()

    cwd = os.getcwd()
    saveDir = os.path.join(cwd, r'proquest_searches\topic_trends')

    browser.maximize_window()

    proquest_url = 'https://www.proquest.com/login'

    browser.get(proquest_url)

    browser.implicitly_wait(5)

    username = 'jordangarrett'
    password = 'Neurobball23'
    ucsb_login(browser, username, password)

    topics = ['Mobile', 'Decoding', 'TF', 'ERP']

    topic_search_prefixes = [
        'su(Electroencephalography OR EEG) AND su(mobile brain imaging OR ambulatory OR locomotion)',
        'su(Electroencephalography OR EEG) AND su(pattern classification OR decoding OR machine learning)',
        'su(Electroencephalography OR EEG) AND su(Oscillations OR time frequency analysis)',
        'su(Electroencephalography OR EEG) AND su(event related potentials OR ERP)']

    search_filters = ' AND rtype.exact("Journal Article") AND PEER(yes)'

    # search for papers from 01/01/2000 to 12/31/2021
    search_years = range(2000, 2022)

    for i, topic in enumerate(topics):

        if i < 3:
            continue

        print(f'Scraping for EEG topic: {topic}')
        alert_page = False

        for j, year in enumerate(search_years):

            print(f'Searching for articles in year {year}...')

            # input search string
            search_year = f' AND pd({year}0101-{year}1231)'

            search_string = topic_search_prefixes[i] + search_filters + search_year

            # first search
            if (i == 3 and j == 0) or alert_page:
                search_bar = browser.find_element(by=By.CSS_SELECTOR, value='#queryTermField')
                search_bar.clear()
                search_bar.send_keys(search_string)
                browser.find_element(by=By.CSS_SELECTOR, value='#searchToResultPage').click()
                alert_page = False
            else:
                search_bar = browser.find_element(by=By.CSS_SELECTOR, value='#searchTerm')
                search_bar.clear()
                search_bar.send_keys(search_string)
                browser.find_element(by=By.CSS_SELECTOR, value='#expandedSearch').click()

            browser.implicitly_wait(15)

            # check if no results returned by search
            try:
                no_results = browser.find_element(by=By.CSS_SELECTOR,
                                                        value='#start > div > div > div.pagingBoxNoResultMain.clear_left.alert.alert-warning')
                if no_results:
                    alert_page = True
                    print(f'No results found for search topic {topic} in {year}.')
                    continue
            except EC.NoSuchElementException:
                # if alert not detected
                pass

            num_results_string = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="pqResultsCount"]')
                )
            )

            num_results_string = num_results_string.text

            num_results = int(''.join(filter(str.isdigit, num_results_string)))

            print(f'{num_results} results returned')

            display_num = 20
            if num_results > 50:
                display_num = 100
            elif num_results > 20:
                display_num = 50

            if display_num:
                # Switch Display Range to 100
                n_display = WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#itemsPerPage')
                    )
                )
                n_display_selector = Select(n_display)
                n_display_selector.select_by_value(str(display_num))
                try:
                    browser.find_element(by=By.CSS_SELECTOR, value='#itemsPerPage').submit()
                except EC.StaleElementReferenceException:
                    browser.refresh()
                    browser.find_element(by=By.CSS_SELECTOR, value='#itemsPerPage').submit()

            # proquest will only show 10000 results
            if num_results > 10000:
                num_pages = 100
            else:
                num_pages = math.ceil(num_results / display_num)

            search_resultsDf = scrape_searchResults(browser, num_pages)

            search_fileName = f'{topic}_{year}_scrape.csv'
            search_resultsDf.to_csv(os.path.join(saveDir, topic, search_fileName), index=False)

