"""
Module that contains class and methods about episode comments and danmus analysis.
"""
import modules.settings as settings
import jieba.analyse
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from collections import Counter
import gspread

# Path to Chinese text files
dict_file = './words/dict.txt'
stopwords_file = './words/stopwords.txt'

# Set Jieba dictionary and stopwords
jieba.set_dictionary(dict_file)
jieba.analyse.set_stop_words(stopwords_file)


class ReviewAnalysis:
    def __init__(self):
        # Authenticate with Google
        self.creds = Credentials.from_service_account_file(settings.service_account_file,
                                                           scopes=settings.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open(settings.sheetname)
        self.worksheet = self.spreadsheet.worksheet(settings.tabnames[2])  # Tab: Episode Trend Analysis
        self.df_episode = pd.read_csv('data/all_episode.csv')  # Load episode level data

    def dynamic_web_page(self, link):
        """
        Open certain episode for further dynamic web crawl.

        :param link: url for certain episode
        """
        # Set up headless mode
        options = Options()
        options.add_argument('--headless')  # Run Chrome in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Set up Selenium with the WebDriver
        print(f'Web crawl for {link}...')
        self.driver = webdriver.Chrome(options=options)  # or use webdriver.Firefox() if you're using Firefox

        # Open the target URL
        self.driver.get(link)
        time.sleep(np.random.uniform(1, 2))

    def danmu_crawler(self):
        """
        Crawl episode danmus through dynamic web page.

        :return: a list of all danmus
        """
        # Danmu scroll
        scroll_item = self.driver.find_element(By.CLASS_NAME, 'danmu-scroll')

        # Scroll until all items are loaded
        previous_height = 0
        while True:
            # Scroll down the element
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_item)
            time.sleep(np.random.uniform(0.4, 0.8))  # Wait for items to load

            # Get the new scroll height after scrolling
            new_height = scroll_item.get_attribute('scrollHeight')

            # Break the loop if scrolling has reached the bottom (no new items loaded)
            if new_height == previous_height:
                break
            previous_height = new_height

        # Get danmu string list
        scroll_item = BeautifulSoup(scroll_item.get_attribute('innerHTML'), 'html.parser')
        danmu_list = scroll_item.select('.sub-list-li > div > .sub_content > span')
        danmus = [danmu.text.strip() for danmu in danmu_list]
        return danmus

    def comment_crawler(self):
        """
        Crawl episode comments through dynamic web page

        :return: a list of comments after clicking 7 times "read more..."
        """
        click = 0
        try:
            # Continuously find and click only the main "Load more" button for main comments
            while click < 7:
                # Locate the main "Load more" button directly under .webview_commendlist
                load_more_button = self.driver.find_element(By.CSS_SELECTOR, ".webview_commendlist > .c-more-msg")

                # Move to the button and click it
                ActionChains(self.driver).move_to_element(load_more_button).click(load_more_button).perform()

                # Increment the counter
                click += 1

                # Wait a bit to allow content to load
                time.sleep(np.random.uniform(0.4, 0.8))
        except:
            print("No more main 'Load more' button or an error occurred.")

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        comment_item = soup.select_one('.webview_commendlist')

        comments = comment_item.select('.reply-content > .reply-content__cont > p')
        comments = [c.text.strip() for c in comments if c.text.strip() != '此留言已被折疊']
        self.driver.quit()
        return comments

    def word_freq(self, text_list, type):
        """
        1. Segment words through Jeiba
        2. Compute top 20 word frequency
        3. Import to spreadsheet, tab: Episode Trend Analysis

        :param text_list: a list of danmus or comments
        :param type: danmu or comment
        :return:
        """
        print(f"Start computing {type}'s word frequency...")
        text = ' '.join(text_list)
        tags = jieba.analyse.extract_tags(text, topK=20)  # top 20 most frequent

        seg_list = jieba.lcut(text, cut_all=False)
        dictionary = Counter(seg_list)

        freq = {tag: dictionary[tag] for tag in tags}
        # freq = {}
        # for ele in dictionary:
        #     if ele in tags:
        #         freq[ele] = dictionary[ele]

        df_freq = pd.DataFrame(list(freq.items()), columns=[f'{type}_tag', f'{type}_count'])
        df_freq = df_freq.sort_values(f'{type}_count', ascending=False, ignore_index=True)  # sort by frequency

        def convert_to_utf8(val):
            if isinstance(val, str):
                return val.encode('utf-8', errors='ignore').decode('utf-8')
            return str(val)

        df_freq = df_freq.map(convert_to_utf8).fillna('')
        header = [df_freq.columns.tolist()]
        values = df_freq.values.tolist()
        sheetrange = 'B:C' if type == 'danmu' else 'D:E'
        print('Importing data into spreadsheet...')
        self.worksheet.update(range_name=sheetrange, values=header + values, raw=False)  # update spreadsheet

        return df_freq
