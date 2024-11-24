"""
Endpoints built by FastAPI.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.review_analysis import ReviewAnalysis
from modules.recommend import AnimeRecommend
from typing import List


# Define a Pydantic model for the input
class LinkRequest(BaseModel):
    anime_name: str  # The name of the anime
    episode_name: str  # The name of the specific episode


# Initialize FastAPI application
app = FastAPI(
    title='Animation Crazy Analysis API',
    description='API to analyze and recommend anime content, compute word frequency, and extract insights.',
)

# Initialize analysis and recommendation modules
ra = ReviewAnalysis()
ar = AnimeRecommend()


@app.get('/', description='Root endpoint for testing the API connection.')
async def get_root():
    """
    Test the API connection.
    Returns:
        An empty dictionary as a basic response.
    """
    return {}


@app.post('/anime/episode/review', description='Count word frequency in episode comments and danmu.')
async def count_word_freq(request: LinkRequest):
    """
    Analyze and compute word frequency for a given anime episode.

    Args:
        request (LinkRequest): Anime and episode names for analysis.

    Process:
        1. Clear columns B:E in the worksheet.
        2. Retrieve the episode link from the database.
        3. Scrape danmu and comments for the episode.
        4. Compute word frequency for both danmu and comments.

    Raises:
        HTTPException: If an error occurs during the process.
    """
    try:
        ra.worksheet.batch_clear(['B:E'])  # Clear existing data in the worksheet
        df = ra.df_episode.copy()

        # Extract anime and episode information
        anime_name = request.anime_name
        episode_name = request.episode_name
        print('Fetching episode link...')
        link = df.loc[(df['anime_name'] == anime_name) &
                      (df['episode_name'] == episode_name), 'episode_link'].iloc[0]

        # Perform danmu and comment analysis
        ra.dynamic_web_page(link)
        danmus = ra.danmu_crawler()
        ra.word_freq(text_list=danmus, type='danmu')

        comments = ra.comment_crawler()
        ra.word_freq(text_list=comments, type='comment')

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Define the input model for anime recommendation
class RecommendationInput(BaseModel):
    target_anime: List[str]  # List of target anime names for personalized recommendations
    parameters: List[str]  # List of parameters for filtering and prioritizing recommendations


@app.post('/anime/recommendation', description='Recommend animations based on similarity and custom parameters.')
async def recommend_anime(input_data: RecommendationInput):
    """
    Generate anime recommendations based on similarity scores and custom parameters.

    Args:
        input_data (RecommendationInput): Includes target anime and recommendation parameters.

    Process:
        1. Clear specific worksheet ranges for fresh data.
        2. Extract user-provided anime and parameters.
        3. Call the recommendation system to generate suggestions.
        4. Update the worksheet with the top 12 recommendations.

    Raises:
        HTTPException: If an error occurs during the process.
    """
    try:
        # Clear previous recommendations from the worksheet
        ar.worksheet.batch_clear(['B6:G6', 'B11:G11'])

        # Extract input data
        target_anime = input_data.target_anime
        parameters = input_data.parameters

        # Generate recommendations
        animes = ar.anime_recommend(target_anime, parameters)

        # Update worksheet with new recommendations
        ar.worksheet.update(range_name='B6:G6', values=[list(animes[:6])], raw=False)
        ar.worksheet.update(range_name='B11:G11', values=[list(animes[6:])], raw=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
