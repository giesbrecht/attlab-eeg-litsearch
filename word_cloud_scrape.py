import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import StaleElementReferenceException
import math
import os
import argparse

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

        browser = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe',
                                   chrome_options=options)

    else:
        browser = webdriver.Safari()

    saveDir = r'D:\EEG_Review\attlab-eeg-litsearch\proquest_searches'

    browser.maximize_window()

    proquest_url = 'https://www.proquest.com/login'

    browser.get(proquest_url)

    browser.implicitly_wait(5)

    # Log in
    try:
        # recent institution not saved
        find_institution = browser.find_element(by=By.XPATH, value='//*[@id="institutionName"]')
        find_institution.send_keys('University of California, Santa Barbara')
        find_institution.submit()
        browser.implicitly_wait(5)
        institution_link = browser.find_element(by=By.XPATH,
                                                value='//*[@id="institution-layer-modal"]/ul/div/li/div/a/span[2]')
        institution_link.click()
    except:
        # recent institution saved
        browser.find_element(by=By.XPATH, value='//*[@id="recent-institution-layer-modal"]/ul/li/a[1]').click()

    try:
        browser.find_element(by=By.XPATH, value='//*[@id="username"]').send_keys('jordangarrett')
        browser.find_element(by=By.XPATH, value='//*[@id="password"]').send_keys('Neurobball23')
        browser.find_element(by=By.XPATH, value='//*[@id="fm1"]/input[4]').click()
    except:
        print('UCSB Log In not found, check if required')

    # search for papers from 01/01/2000 to 12/31/2021
    search_years = range(2015, 2022)

    for i, year in enumerate(search_years):

        print(f'Searching for articles in year {year}...')

        # input search string
        search_string = f'su(Electroencephalography OR EEG) AND rtype.exact("Journal Article") AND me.exact("Brain Imaging" OR "Empirical Study" OR "Experimental Replication" OR "Field Study") AND PEER(yes) AND pd({year}0101-{year}1231)'

        # first search
        if i == 0:
            search_bar = browser.find_element(by=By.CSS_SELECTOR, value='#queryTermField')
            search_bar.send_keys(search_string)
            browser.find_element(by=By.CSS_SELECTOR, value='#searchToResultPage').click()
        else:
            search_bar = browser.find_element(by=By.CSS_SELECTOR, value='#searchTerm')
            search_bar.clear()
            search_bar.send_keys(search_string)
            browser.find_element(by=By.CSS_SELECTOR, value='#expandedSearch').click()

        num_results_string = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="pqResultsCount"]')
            )
        )

        num_results_string = num_results_string.text

        num_results = int(''.join(filter(str.isdigit, num_results_string)))

        print(f'{num_results} results returned')

        # Switch Display Range to 100
        # browser.implicitly_wait(60)
        n_display = browser.find_element(by=By.CSS_SELECTOR, value='#itemsPerPage')
        n_display_selector = Select(n_display)
        n_display_selector.select_by_value('100')
        n_display.submit()

        # proquest will only show 10000 results
        if num_results > 10000:
            num_pages = 100
        else:
            num_pages = math.ceil(num_results / 100)

        allPage_resultsTitles = []
        allPage_resultsAuthors = []
        allPage_resultsJournals = []

        pages_scraped = 0
        while True:

            try:
                page_results_container = WebDriverWait(browser, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#lor_container > div.resultListContainer.ltr > ul'))
                )
                page_results = page_results_container.find_elements(by=By.XPATH, value='./child::*')
                header_test = page_results[0].find_element(by=By.CLASS_NAME, value='resultHeader')
            except StaleElementReferenceException:
                browser.refresh()
                browser.implicitly_wait(30)
                page_results_container = WebDriverWait(browser, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#lor_container > div.resultListContainer.ltr > ul'))
                )
                page_results = page_results_container.find_elements(by=By.XPATH, value='./child::*')


            page_resultsTitles = []
            page_resultsAuthors = []
            page_resultsJournals = []
            for result in page_results:

                header = result.find_element(by=By.CLASS_NAME, value='resultHeader')
                header_children = header.find_elements(by=By.XPATH, value='./child::*')

                page_resultsTitles.append(header_children[0].text)
                page_resultsAuthors.append(header_children[1].text)
                page_resultsJournals.append(header_children[2].text)

            allPage_resultsTitles.append(page_resultsTitles)
            allPage_resultsAuthors.append(page_resultsAuthors)
            allPage_resultsJournals.append(page_resultsJournals)

            pages_scraped += 1
            print(f'Scraped Page {pages_scraped}')

            try:
                browser.find_element(by=By.CSS_SELECTOR, value='#updateForm > nav > ul > li:nth-child(9) > a').click()
                browser.implicitly_wait(20)
            except:
                if pages_scraped < num_pages:
                    # raise('Did not scrape all search results')
                    break
                else:
                    print('All possible search results scraped')
                    break

        allPage_resultsTitles = [title for sublist in allPage_resultsTitles for title in sublist]
        allPage_resultsAuthors = [author for sublist in allPage_resultsAuthors for author in sublist]
        allPage_resultsJournals = [journal for sublist in allPage_resultsJournals for journal in sublist]

        search_resultsDf = pd.DataFrame(
            list(zip(allPage_resultsTitles, allPage_resultsAuthors, allPage_resultsJournals)),
            columns=['Title', 'Authors', 'Journal'])

        search_fileName = f'{year}_scrape.csv'
        search_resultsDf.to_csv(os.path.join(saveDir, search_fileName), index=False)
