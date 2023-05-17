from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import StaleElementReferenceException
import pandas as pd


def ucsb_login(browser, username: str, password: str):

    # get around cookies
    try:
        manage_cookies_button = browser.find_element(by=By.XPATH, value='//*[@id="onetrust-pc-btn-handler"]')
        manage_cookies_button.click()
        confirm_choice_button = browser.find_element(by=By.XPATH, value='//*[@id="onetrust-pc-sdk"]/div/div[3]/div[1]/button')
        confirm_choice_button.click()
    except:
        pass

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
        browser.find_element(by=By.XPATH, value='//*[@id="username"]').send_keys(username)
        browser.find_element(by=By.XPATH, value='//*[@id="password"]').send_keys(password)
        browser.find_element(by=By.XPATH, value='//*[@id="fm1"]/input[4]').click()
    except:
        print('UCSB Log In not found, check if required')


def scrape_searchResults(browser, num_pages: int) -> pd.DataFrame:
    allPage_resultsTitles = []
    allPage_resultsAuthors = []
    allPage_resultsJournals = []

    pages_scraped = 0
    while True:

        try:
            page_results_container = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#lor_container > div.resultListContainer.ltr > ul'))
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
            page_navigator = browser.find_element(by=By.CSS_SELECTOR,
                                                  value='#updateForm > nav > ul')

            page_navigator_children = page_navigator.find_elements(by=By.TAG_NAME,
                                                                   value='a')
            next_page_button = [button for button in page_navigator_children if button.get_attribute('title') == 'Next Page']

            if next_page_button:
                next_page_button[0].click()
                browser.implicitly_wait(20)
            else:
                raise 'No Next Page button'

        except:
            if pages_scraped < num_pages:
                raise 'Did not scrape all search results'
            else:
                print('All possible search results scraped')
                break

    allPage_resultsTitles = [title for sublist in allPage_resultsTitles for title in sublist]
    allPage_resultsAuthors = [author for sublist in allPage_resultsAuthors for author in sublist]
    allPage_resultsJournals = [journal for sublist in allPage_resultsJournals for journal in sublist]

    search_resultsDf = pd.DataFrame(
        list(zip(allPage_resultsTitles, allPage_resultsAuthors, allPage_resultsJournals)),
        columns=['Title', 'Authors', 'Journal'])

    return search_resultsDf
