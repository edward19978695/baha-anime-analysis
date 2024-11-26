# Animation Crazy Analysis

Animation Crazy ([巴哈姆特動畫瘋](https://ani.gamer.com.tw/)) is one of the most popular Japanese animation streaming
platform in Taiwan.
As a big user of it, I have built this project to crawl some anime viewing data and also utilize these information to
built other functionalities like review analysis and anime recommendation.
The results could be viewed in
the [Google Sheet](https://docs.google.com/spreadsheets/d/1F94CV-TTa628TumABt3DOF_beqJxQTJ-Mjp1nHkWQDE/edit?usp=sharing).

**Disclaimer:**
This project is developed for personal interests, isn't used on any business purposes.

---

## Contents <a name="contents"></a>
- [Web Crawler](#webCrawler)
  1. [Anime-level](#animeLevel)
  2. [Episode-level](#episodeLevel)
- [Review Analysis](#reviewAnalysis)
- [Recommendation System](#recommendation)
- [APIs](#apis)
- [Google Sheet Development](#googleSheet)


---

## Web Crawler <a name="webCrawler"></a>
Coding details could be seen in `data.py` script in `modules` folder.

### 1. Anime-level <a name="animeLevel"></a>

All animations that are authorized could be seen in all anime list ([所有動畫](https://ani.gamer.com.tw/animeList.php)) tab of Animation Crazy website.
![All Anime](plots/all_anime_list.png)
As the above screenshot shows, we could scratch anime's `total view`, `total episodes`, ... etc information.
While click into each anime, could also get more detail metrics includes `launched date`, `score`, ... etc.
![Anime Details](plots/anime_detail.png)
All these information could be easily scratch through static web crawl methods (`requests` and `BeautifulSoup`) and
results are stored at **Anime-Level Data** tab
of [Google Sheet](https://docs.google.com/spreadsheets/d/1F94CV-TTa628TumABt3DOF_beqJxQTJ-Mjp1nHkWQDE/edit?usp=sharing).
Below is the simple explanation of each column:

| **Column** | **Explanation**                                                                            |
|------------|--------------------------------------------------------------------------------------------|
| 動畫名稱       | The animation name                                                                         |
| 縮圖         | The thumbnail                                                                              |
| 首播日期       | The first launched data                                                                    |
| 總集數        | Total episode count                                                                        |
| 總觀看次數      | Total viewed count                                                                         |
| 平均觀看次數     | Total viewed count / Total episode count                                                   |
| 評分         | The score of anime                                                                         |
| 評分人數       | Total scored count                                                                         |
| 評分轉換率      | Total scored count / Total viewed count : the tendency of scoring after viewing the anime. |
| 原作者        | The author of original.                                                                    |
| 代理商        | The agency.                                                                                |
| 動畫公司       | The anime creating company.                                                                |
| 導演         | The director.                                                                              |
| 類型         | The types of anime.                                                                        |
| 簡介         | The introduction of anime.                                                                 |



### 2. Episode-level <a name="episodeLevel"></a>
For each episode of an anime, it also has its own metrics like `view count`, `danmu count`(彈幕數), `comment count`, ... etc.
![Episode metrics](plots/episode-metrics.png)
However, as the screenshot above shows, danmu count information is drop in a scroll drop element.
This time we have to use dynamic web scratch method like `selenium` to obtain those metrics and results are store in **Episode-Level Data** tab in [Google Sheet](https://docs.google.com/spreadsheets/d/1F94CV-TTa628TumABt3DOF_beqJxQTJ-Mjp1nHkWQDE/edit?usp=sharing). 
Below are also some simple explanation of columns:

| **Column** | **Explanation**                                                                   |
|------------|-----------------------------------------------------------------------------------|
| 動畫名稱       | The animation name                                                                |
| 集數         | The episod name.                                                                  |
| 上架時間       | The uploaded time of the episode                                                  |
| 觀看數        | The view count of episode                                                         |
| 評論數        | The comment count of episode                                                      |
| 評論轉換率      | Comment count / View count : the tendency of commenting after viewing the episode |
| 彈幕數        | The danmu count                                                                   |
| 彈幕轉換率      | Danmu count / View count : the tendency of sending danmu while watching episode   |


[Back to Contents](#contents)


---

## Review Analysis <a name="reviewAnalysis"></a>


[Back to Contents](#contents)

---

## Recommendation System <a name="recommendation"></a>


[Back to Contents](#contents)

---

## APIs <a name="apis"></a>


[Back to Contents](#contents)

---

## Google Sheet Development <a name="googleSheet"></a>



[Back to Contents](#contents)