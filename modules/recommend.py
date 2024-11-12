from google.oauth2.service_account import Credentials
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pandas as pd
import numpy as np
import gspread
import ast
import modules.settings as settings


class AnimeRecommend:
    def __init__(self):
        # Authenticate with Google
        self.creds = Credentials.from_service_account_file(settings.service_account_file,
                                                           scopes=settings.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open(settings.sheetname)
        self.worksheet = self.spreadsheet.worksheet(settings.tabnames[3])
        self.df_anime = self.read_anime_data()
        self.similarity_df = self.compute_similarity_score()

    def read_anime_data(self):
        df_anime = pd.read_csv('data/all_anime.csv')

        # Convert to list type
        df_anime['types'] = df_anime['types'].apply(ast.literal_eval)

        # Convert launch date into int
        df_anime['first_launched_date'] = pd.to_datetime(df_anime['first_launched_date'])
        df_anime['first_launched_date'] = df_anime['first_launched_date'].astype(int)

        # Fill missing view and score value to their min values
        df_anime['total_view'] = df_anime['total_view'].fillna(df_anime['total_view'].min())
        df_anime['score'] = df_anime['score'].fillna(df_anime['score'].min())

        # Standardize launch date and score
        scaler = StandardScaler()
        df_anime[['scaled_launch', 'scaled_score']] = scaler.fit_transform(
            df_anime[['first_launched_date', 'score']])

        # Launch date and score are both left-skewed distribution --> apply Exp transformation
        df_anime['scaled_launch'] = np.exp(df_anime['scaled_launch'])
        df_anime['scaled_score'] = np.exp(df_anime['scaled_score'])
        # Total view is right-skewed distribution --> apply Log transformation
        df_anime['scaled_view'] = np.log(df_anime['total_view'])

        # Map to [0, 1]
        scaler = MinMaxScaler()
        df_anime[['scaled_launch', 'scaled_view', 'scaled_score']] = scaler.fit_transform(
            df_anime[['scaled_launch', 'scaled_view', 'scaled_score']])

        return df_anime.copy()

    def jaccard_similarity(self, set1, set2):
        # Function to compute Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def compute_similarity_score(self):
        df_anime = self.df_anime.copy()

        # Create an empty list to store the results
        similarity_matrix = np.zeros((len(df_anime), len(df_anime)))

        # Compute Jaccard similarity score between each pair of anime
        for r in range(len(df_anime)):
            for c in range(r + 1):
                if r == c:
                    similarity_matrix[r, c] = float('-inf')
                else:
                    similarity = self.jaccard_similarity(set(df_anime.iloc[r]['types']),
                                                         set(df_anime.iloc[c]['types']))
                    similarity_matrix[r, c] = similarity
                    similarity_matrix[c, r] = similarity

        similarity_df = pd.DataFrame(similarity_matrix, index=df_anime['name'], columns=df_anime['name'])
        return similarity_df.copy()

    def anime_recommend(self, target_anime, parameters):
        similarity_df = self.similarity_df.copy()
        df_anime = self.df_anime.copy()

        # Get the row corresponding to the target anime
        target_similarities = similarity_df.loc[:, target_anime]

        scaled_metrics = df_anime.loc[:, ['name', 'scaled_launch', 'scaled_view', 'scaled_score', 'link']]
        scaled_metrics = scaled_metrics.set_index('name')

        target_similarities.loc[:, ['scaled_launch', 'scaled_view', 'scaled_score', 'link']] = scaled_metrics

        target_similarities['main_metric'] = target_similarities[target_anime + parameters].mean(axis=1)

        # Sort the similarities in descending order and get the top 5 most similar anime
        top_recommend_anime = target_similarities.sort_values('main_metric', ascending=False).head(12)
        top_recommend_anime = top_recommend_anime.reset_index()

        return top_recommend_anime.apply(lambda row: f'=HYPERLINK("{row['link']}", "{row['name']}")', axis=1)
