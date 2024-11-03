from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from google.oauth2.service_account import Credentials
from gspread_formatting import (
    get_frozen_row_count,
    get_frozen_column_count,
    set_frozen,
    set_row_height
)

import logging
import gspread
import gspread.utils
import time
import pandas as pd
import numpy as np
import requests
import yaml
import pytz
import re
import modules.settings as settings

with open('conf/app.yml') as f:
    app_config = yaml.safe_load(f)


class WebCrawl:
    def __init__(self):
        self.url = app_config['website']['url']
        self.user_agent = app_config['website']['user_agent']
        self.headers = {'User-Agent': self.user_agent}

    def anime_author(self, link):
        res = requests.get(link, headers=self.headers)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, 'html.parser')
        author = soup.select_one('.ACG-box1listB > li > a').text.strip()
        return author

    def anime_detail(self, link):
        res = requests.get(link, headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Score value and counts
        try:
            score = float(soup.select_one('.score-overall-number').text.strip())
            score_count = int(
                soup.select_one('.score-overall-people').text.strip().replace(',', '').replace('人評價', ''))
        except:
            score = None
            score_count = None

        # Anime types: first launched, director, agent, animator, types
        anime_types = soup.select('.type')
        first_launched_date = pd.to_datetime(anime_types[0].select_one('p').text).strftime('%Y-%m-%d')
        director = anime_types[1].select_one('p').text
        agent = anime_types[2].select_one('p').text
        animator = anime_types[3].select_one('p').text
        types = [typ.text for typ in anime_types[4].select('li')]

        link_button = soup.select_one('.link > .link-button').get('href')
        author = self.anime_author('https:' + link_button)

        return score, score_count, first_launched_date, author, director, agent, animator, types

    def all_anime(self):
        all_anime_list = []
        next_page = ''
        while not next_page.startswith('javascript:alert'):
            res = requests.get(self.url + 'animeList.php' + next_page,
                               headers=self.headers)
            res.raise_for_status()

            soup = BeautifulSoup(res.text, 'html.parser')
            anime_items = soup.select_one('.theme-list-block')
            anime_items = anime_items.select('.theme-list-main')

            for anime in anime_items:
                # Anime Name
                name = anime.select_one('.theme-name').text.strip()
                print(f'Start digging anime {name}....')
                label = anime.select_one('.label-edition')
                if label is not None and label.text.strip() == '年齡限制':
                    name += ' [年齡限制版]'

                # Anime Thumbnail
                thumbnail = anime.select_one('img').get('data-src')

                # Total View
                total_view = anime.select_one('.show-view-number > p').text.strip().replace(',', '')
                total_view = float(total_view.replace('萬', '')) * 10000 \
                    if '萬' in total_view else total_view
                total_view = int(total_view) if total_view != '統計中' else None

                # Total Episodes
                total_episode = int(anime.select_one('.theme-number').text.replace(
                    '共', '').replace('集', '').strip())

                # Average view
                avg_view = total_view / total_episode if total_view is not None else None

                # Anime Link
                link = self.url + anime.get('href')

                # Anime details
                (score, score_count, first_launched_date,
                 author, director, agent, animator, types) = self.anime_detail(link)

                # # Compute rate of score count over total view
                # score_rate = score_count / total_view if total_view is not None else None

                a = {
                    'name': name,
                    'thumbnail': thumbnail,
                    'total_view': total_view,
                    'total_episode': total_episode,
                    'avg_view': avg_view,
                    'link': link,
                    'score': score,
                    'score_count': score_count,
                    # 'score_rate': score_rate,
                    'first_launched_date': first_launched_date,
                    'author': author,
                    'director': director,
                    'agent': agent,
                    'animator': animator,
                    'types': types
                }
                all_anime_list.append(a)

                # Add a time delay
                time.sleep(2)

            next_page = soup.select_one('.next').get('href')

            # Add a time delay
            time.sleep(2)

        df_all_anime = pd.DataFrame(all_anime_list)
        df_all_anime.to_csv('./data/all_anime.csv', index=False)
        return df_all_anime

    def episode_detail(self, name, link):
        # # Set up headless mode
        # options = Options()
        # options.add_argument('--headless')  # Run Chrome in headless mode
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        #
        # # Set up Selenium with the WebDriver
        # driver = webdriver.Chrome(options=options)  # or use webdriver.Firefox() if you're using Firefox
        #
        # # Open the target URL
        # driver.get(link)
        # time.sleep(1)
        #
        # # Episode title, view, uploaded time
        # episode_item = driver.find_element(By.CLASS_NAME, 'anime_name')
        # episode_soup = BeautifulSoup(episode_item.get_attribute('innerHTML'), 'html.parser')

        res = requests.get(link, headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        episode_soup = soup.select_one('.anime_name')

        episode_name = episode_soup.select_one('h1').text.replace(name, '').strip()
        uploaded_time = pd.to_datetime(episode_soup.select_one('.uploadtime').text.replace(
            '上架時間：', '').strip()).strftime('%Y-%m-%d %H:%M')

        view = episode_soup.select('span')[-1].text
        view = float(view.replace('萬', '')) * 10000 if '萬' in view else view
        view = int(view) if view != '統計中' else None

        # Episode comment counts
        # comment_item = driver.find_element(By.CLASS_NAME, 'filter-nav')
        # comment_soup = BeautifulSoup(comment_item.get_attribute('innerHTML'), 'html.parser')

        comment_soup = soup.select_one('.filter-nav')
        comment_count = comment_soup.select_one('h5').text.replace('則留言', '').strip()
        comment_count = int(comment_count) if len(comment_count) > 0 else 0

        # # Wait until the element with class 'danmu-scroll' is present
        # wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed
        # danmu_item = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'danmu-scroll')))
        #
        # danmu_soup = BeautifulSoup(danmu_item.get_attribute('innerHTML'), 'html.parser')
        # danmu_soup = danmu_soup.select_one('.anime-tip')
        #
        # # Locate the text containing the danmu count
        # if danmu_soup is None:
        #     danmu_count = 0
        # else:
        #     danmu_text = danmu_soup.find(string=lambda x: x and "本動畫共" in x and "筆彈幕" in x)
        #     danmu_count = re.search(r'\d+', danmu_text).group()
        #     danmu_count = int(danmu_count) if len(danmu_count) > 0 else 0

        # return episode_name, uploaded_time, view, comment_count, danmu_count
        return episode_name, uploaded_time, view, comment_count

    def all_episode(self):
        df_all_anime = pd.read_csv('./data/all_anime.csv')
        all_episode_list = []
        for i, row in df_all_anime.iterrows():
            anime_name = row['name']
            anime_link = row['link']
            print(f'Start exploring each episode of {anime_name}...')

            res = requests.get(anime_link, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            episodes = soup.select('.season > ul > li > a')
            episode_links = [self.url + 'animeVideo.php' + e.get('href') for e in episodes] \
                if len(episodes) > 0 else [anime_link]

            for link in episode_links:
                for attempt in range(3):  # Allows one retry attempt
                    try:
                        (episode_name, uploaded_time, view, comment_count) = self.episode_detail(anime_name, link)

                        # Append the data if extraction was successful
                        e = {
                            'anime_name': anime_name,
                            'episode_name': episode_name,
                            'episode_link': link,
                            'uploaded_time': uploaded_time,
                            'view': view,
                            'comment_count': comment_count
                        }
                        all_episode_list.append(e)

                        # Add a time delay
                        time.sleep(1)
                        print(f'Successfully extracted episode {episode_name}!!')
                        break  # Exit loop if successful

                    except Exception as e:
                        print('Encounter exception: {}'.format(e))
                        print(f'Retry {attempt + 1}-th time')

        df_all_episode = pd.DataFrame(all_episode_list)
        df_all_episode.to_csv('./data/all_episode.csv', index=False)
        return df_all_episode


class UpdateSheet:
    def __init__(self):
        # Authenticate with Google
        self.creds = Credentials.from_service_account_file(settings.service_account_file,
                                                           scopes=settings.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open(settings.sheetname)
        self.wc = WebCrawl()

    def anime_level(self):
        df_all_anime = self.wc.all_anime()
        print('Finish extracting data from web, start import data to spreadsheet...')
        column_names = settings.column_names['anime_level']
        df_all_anime = df_all_anime.sort_values('first_launched_date', ascending=False, ignore_index=True)

        df_all_anime = df_all_anime.fillna('')

        # Step 1: Convert all values to string and handle encoding issues
        def convert_to_utf8(val):
            if isinstance(val, str):
                return val.encode('utf-8', errors='ignore').decode('utf-8')
            return str(val)

        # Create hyperlink format for Google Sheets
        def create_hyperlink(name, url):
            return f'=HYPERLINK("{url}", "{name}")'

        # Apply the hyperlink function to each row in the DataFrame
        df_all_anime['name'] = df_all_anime.apply(
            lambda row: create_hyperlink(row['name'], row['link']), axis=1)
        df_all_anime['thumbnail'] = df_all_anime['thumbnail'].apply(lambda x: f'=IMAGE("{x}", 4, 100, 75)')

        df_all_anime = df_all_anime[list(column_names.keys())]
        df_all_anime = df_all_anime.applymap(convert_to_utf8)

        worksheet = self.spreadsheet.worksheet(settings.tabnames[0])

        # Get existing frozen rows
        frozen_rows = get_frozen_row_count(worksheet) or 4
        frozen_cols = get_frozen_column_count(worksheet) or 3

        # Clean sheet
        worksheet.clear_basic_filter()
        worksheet.batch_clear(
            [f'A4:{gspread.utils.rowcol_to_a1(worksheet.row_count, worksheet.col_count)}'])

        header = [list(column_names.values())]
        values = df_all_anime.values.tolist()

        END = len(header + values) + 3

        range_end = gspread.utils.rowcol_to_a1(END, len(header[0]))
        my_range = f'A4:{range_end}'
        worksheet.batch_clear([my_range])
        worksheet.update(range_name=my_range, values=header + values, raw=False)
        if END > frozen_rows:
            worksheet.resize(rows=END)

        # Re-apply existing formats
        set_frozen(worksheet=worksheet,
                   rows=frozen_rows,
                   cols=frozen_cols)

        set_row_height(worksheet, f'5:{END}', 100)

        # Add filter
        worksheet.set_basic_filter(my_range)

        # Updated time and latest data source file
        now = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
        worksheet.update_acell('B1', now)

    def episode_level(self):
        df_all_episode = self.wc.all_episode()
        print('Finish extracting data from web, start import data to spreadsheet...')
        column_names = settings.column_names['episode_level']

        df_all_episode = df_all_episode.fillna('')

        # Step 1: Convert all values to string and handle encoding issues
        def convert_to_utf8(val):
            if isinstance(val, str):
                return val.encode('utf-8', errors='ignore').decode('utf-8')
            return str(val)

        # Create hyperlink format for Google Sheets
        def create_hyperlink(name, url):
            return f'=HYPERLINK("{url}", "{name}")'

        # Apply the hyperlink function to each row in the DataFrame
        df_all_episode['episode_name'] = df_all_episode.apply(
            lambda row: create_hyperlink(row['episode_name'], row['episode_link']), axis=1)

        df_all_episode = df_all_episode[list(column_names.keys())]
        df_all_episode = df_all_episode.map(convert_to_utf8)

        worksheet = self.spreadsheet.worksheet(settings.tabnames[1])

        # Get existing frozen rows
        frozen_rows = get_frozen_row_count(worksheet) or 4

        # Clean sheet
        worksheet.clear_basic_filter()
        worksheet.batch_clear(
            [f'A4:{gspread.utils.rowcol_to_a1(worksheet.row_count, worksheet.col_count)}'])

        header = [list(column_names.values())]
        values = df_all_episode.values.tolist()

        END = len(header + values) + 3

        range_end = gspread.utils.rowcol_to_a1(END, len(header[0]))
        my_range = f'A4:{range_end}'
        worksheet.batch_clear([my_range])
        worksheet.update(range_name=my_range, values=header + values, raw=False)
        if END > frozen_rows:
            worksheet.resize(rows=END)

        # Re-apply existing formats
        set_frozen(worksheet=worksheet,
                   rows=frozen_rows)

        # Add filter
        worksheet.set_basic_filter(my_range)

        # Updated time and latest data source file
        now = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
        worksheet.update_acell('B1', now)


if __name__ == '__main__':
    print('Start Crawling and Importing data to spreadsheet...')
    us = UpdateSheet()
    us.anime_level()
    us.episode_level()
    print('Finish!!!!!')
