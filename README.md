# Animation Crazy Analysis

Animation Crazy ([巴哈姆特動畫瘋](https://ani.gamer.com.tw/)) is one of the most popular Japanese animation streaming platforms in Taiwan.  
As a frequent user, I built this project to crawl anime viewing data and utilize this information to develop functionalities like review analysis and anime recommendations.  
The results can be viewed in this [Google Sheet](https://docs.google.com/spreadsheets/d/1F94CV-TTa628TumABt3DOF_beqJxQTJ-Mjp1nHkWQDE/edit?usp=sharing).

**Disclaimer:**  
This project is developed purely out of personal interest and is not intended for commercial use.

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
Details of the implementation can be found in the `data.py` script in the `modules` folder.

### 1. Anime-level <a name="animeLevel"></a>

All authorized animations can be found on the "All Anime List" ([所有動畫](https://ani.gamer.com.tw/animeList.php)) tab of the Animation Crazy website.  
![All Anime](plots/all_anime_list.png)  
As shown in the screenshot, we can extract information such as `total views`, `total episodes`, etc. Additionally, by clicking on an individual anime, more detailed metrics like `launch date`, `score`, and more can be retrieved.  
![Anime Details](plots/anime_detail.png)  

This information is collected using static web scraping techniques (`requests` and `BeautifulSoup`) and stored in the **Anime-Level Data** tab of the [Google Sheet](https://docs.google.com/spreadsheets/d/1F94CV-TTa628TumABt3DOF_beqJxQTJ-Mjp1nHkWQDE/edit?usp=sharing). Below is a brief explanation of each column:

| **Column**   | **Explanation**                                                                                   |
|--------------|---------------------------------------------------------------------------------------------------|
| 動畫名稱       | The name of the animation.                                                                         |
| 縮圖         | The thumbnail of the animation.                                                                     |
| 首播日期       | The premiere date of the animation.                                                               |
| 總集數        | The total number of episodes.                                                                      |
| 總觀看次數      | The total view count.                                                                             |
| 平均觀看次數     | The average view count per episode (`total views / total episodes`).                              |
| 評分         | The overall rating of the animation.                                                               |
| 評分人數       | The total number of ratings.                                                                      |
| 評分轉換率      | Rating conversion rate (`total ratings / total views`): measures the tendency to rate after watching. |
| 原作者        | The author of the original work.                                                                   |
| 代理商        | The licensing agency.                                                                              |
| 動畫公司       | The production company of the animation.                                                          |
| 導演         | The director of the animation.                                                                     |
| 類型         | The genres of the animation.                                                                       |
| 簡介         | A brief description of the animation.                                                              |

[Back to Contents](#contents)

---


### 2. Episode-level <a name="episodeLevel"></a>
Each episode of an anime also includes metrics such as `view count`, `danmu count` (彈幕數), `comment count`, and more.  
![Episode Metrics](plots/episode-metrics.png)  

As shown above, the `danmu count` is located within a scrolldown element. To retrieve this information, dynamic web scraping techniques using `selenium` are required.  
The results are stored in the **Episode-Level Data** tab of the [Google Sheet](https://docs.google.com/spreadsheets/d/1F94CV-TTa628TumABt3DOF_beqJxQTJ-Mjp1nHkWQDE/edit?usp=sharing). Below is a brief explanation of each column:

| **Column**   | **Explanation**                                                                 |
|--------------|---------------------------------------------------------------------------------|
| 動畫名稱       | The name of the animation.                                                     |
| 集數         | The episode name.                                                              |
| 上架時間       | The upload time of the episode.                                               |
| 觀看數        | The view count of the episode.                                                |
| 評論數        | The comment count of the episode.                                             |
| 評論轉換率      | Comment conversion rate (`comments / views`): measures the tendency to comment after watching. |
| 彈幕數        | The number of danmu (user-generated subtitles/comments overlaid on the video). |
| 彈幕轉換率      | Danmu conversion rate (`danmu / views`): measures the tendency to send danmu while watching. |

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