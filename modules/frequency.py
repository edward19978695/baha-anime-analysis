import modules.settings as settings
import jieba.analyse
import pandas as pd
import numpy as np
from google.oauth2.service_account import Credentials
from PIL import Image
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from collections import Counter
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import gspread

dict_file = './words/dict.txt'
stopwords_file = './words/stopwords.txt'

# Set Jieba dictionary and stopwords
jieba.set_dictionary(dict_file)
jieba.analyse.set_stop_words(stopwords_file)


class WordFrequency:
    def __init__(self):
        # Authenticate with Google
        self.creds = Credentials.from_service_account_file(settings.service_account_file,
                                                           scopes=settings.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open(settings.sheetname)
        self.worksheet = self.spreadsheet.worksheet(settings.tabnames[2])
        self.df_episode = pd.read_csv('data/all_episode.csv')

    def crawl_comment_and_danmu(self, link):
        # Set up headless mode
        options = Options()
        options.add_argument('--headless')  # Run Chrome in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Set up Selenium with the WebDriver
        print(f'Web crawl for {link}...')
        driver = webdriver.Chrome(options=options)  # or use webdriver.Firefox() if you're using Firefox

        # Open the target URL
        driver.get(link)
        time.sleep(np.random.uniform(0.5, 1))

        # Danmu scroll
        scroll_item = driver.find_element(By.CLASS_NAME, 'danmu-scroll')

        # Scroll until all items are loaded
        previous_height = 0
        while True:
            # Scroll down the element
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_item)
            time.sleep(np.random.uniform(0.5, 1))  # Wait for items to load

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

        # Find and click "Load more" buttons to expand hidden comments, if they exist
        while True:
            try:
                # Locate the "Load more" button or similar to load hidden comments
                load_more_button = driver.find_element(By.CLASS_NAME, 'c-more-msg')
                ActionChains(driver).move_to_element(load_more_button).click(load_more_button).perform()

                # Wait for the content to load after clicking
                time.sleep(np.random.uniform(0.5, 1))
            except:
                # Exit loop if there is no more button to click
                break

        # Comment string list
        comment_item = driver.find_element(By.CLASS_NAME, 'webview_commendlist')
        comment_item = BeautifulSoup(comment_item.get_attribute('innerHTML'), 'html.parser')

        comments = comment_item.select('.reply-content > .reply-content__cont > p')
        comments = [c.text.strip() for c in comments]

        # Close the WebDriver session
        driver.quit()

        # Print or process the episode_dict as needed
        print(f'Successfully obtained {len(comments)} comments and {len(danmus)} danmus!!!')
        return comments, danmus

    def word_freq(self, text_list, type):
        print(f"Start computing {type}'s word frequency...")
        text = ' '.join(text_list)
        tags = jieba.analyse.extract_tags(text, topK=20)

        seg_list = jieba.lcut(text, cut_all=False)
        dictionary = Counter(seg_list)

        freq = {}
        for ele in dictionary:
            if ele in tags:
                freq[ele] = dictionary[ele]

        df_freq = pd.DataFrame(list(freq.items()), columns=[f'{type}_tag', f'{type}_count'])
        df_freq = df_freq.sort_values(f'{type}_count', ascending=False, ignore_index=True)

        def convert_to_utf8(val):
            if isinstance(val, str):
                return val.encode('utf-8', errors='ignore').decode('utf-8')
            return str(val)

        df_freq = df_freq.map(convert_to_utf8)

        return df_freq


# Define a Pydantic model for the input
class LinkRequest(BaseModel):
    anime_name: str
    episode_name: str


app = FastAPI(title='Baha Anime Anlysis API',
              description='API to compute comment and danmu word frequency.')

# Create an instance of your word cloud generator
wf = WordFrequency()


# @app.get('/', description='Root endpoint for testing.')
# async def get_root():
#     return {}


@app.post('/word_freq',
          description='Count word frequency')
async def count_word_freq(request: LinkRequest):
    try:
        wf.worksheet.batch_clear(['B:E'])
        df = wf.df_episode.copy()
        anime_name = request.anime_name
        episode_name = request.episode_name
        print('Get episode link...')
        link = df.loc[(df['anime_name'] == anime_name) &
                      (df['episode_name'] == episode_name), 'episode_link'].iloc[0]

        # Crawl comments and danmus
        comments, danmus = wf.crawl_comment_and_danmu(link)

        df_comment = wf.word_freq(comments, 'comment')
        df_danmu = wf.word_freq(danmus, 'danmu')

        df = pd.concat([df_comment, df_danmu], axis=1)
        # df.to_csv('./data/df.csv', index=False)
        df = df.fillna('')

        header = [df.columns.tolist()]
        values = df.values.tolist()

        print('Importing data into spreadsheet...')
        wf.worksheet.update(range_name='B:E', values=header + values, raw=False)


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
