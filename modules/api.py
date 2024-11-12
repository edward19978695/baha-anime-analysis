from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.review_analysis import ReviewAnalysis


# Define a Pydantic model for the input
class LinkRequest(BaseModel):
    anime_name: str
    episode_name: str


app = FastAPI(title='Baha Anime Anlysis API',
              description='API to compute comment and danmu word frequency.')

ra = ReviewAnalysis()


# @app.get('/', description='Root endpoint for testing.')
# async def get_root():
#     return {}


@app.post('/word_freq',
          description='Count word frequency')
async def count_word_freq(request: LinkRequest):
    try:
        ra.worksheet.batch_clear(['B:E'])
        df = ra.df_episode.copy()
        anime_name = request.anime_name
        episode_name = request.episode_name
        print('Get episode link...')
        link = df.loc[(df['anime_name'] == anime_name) &
                      (df['episode_name'] == episode_name), 'episode_link'].iloc[0]

        ra.dynamic_web_page(link)
        danmus = ra.danmu_crawler()
        ra.word_freq(text_list=danmus, type='danmu')

        comments = ra.comment_crawler()
        ra.word_freq(text_list=comments, type='comment')


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
