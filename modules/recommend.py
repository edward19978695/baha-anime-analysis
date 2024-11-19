from google.oauth2.service_account import Credentials
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
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
        self.anime_type_similarity = pd.read_csv('data/anime_type_similarity.csv')
        self.anime_intro_similarity = pd.read_csv('data/anime_intro_similarity.csv')
        # self.similarity_df = self.compute_similarity_score()

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

        print('Finish reading and transform anime data!!!')
        return df_anime.copy()

    def jaccard_similarity(self, set1, set2):
        # Function to compute Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def compute_type_similarity_score(self):
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
        print('Finish computing anime type similarity score!!!')
        similarity_df.to_csv('data/anime_type_similarity.csv')
        # return similarity_df.copy()

    def compute_intro_similarity_score(self):
        # Load the tokenizer and model
        tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
        model = BertModel.from_pretrained("hfl/chinese-roberta-wwm-ext")

        def intro_feature_extraction(intro):
            # helper function to extract anime intro to feature vector
            try:
                # Tokenize and encode the input text
                inputs = tokenizer(intro, return_tensors="pt", truncation=True, max_length=512)
                outputs = model(**inputs)

                # Get the hidden states
                hidden_states = outputs.last_hidden_state

                # Take the embedding of the [CLS] token (first token)
                cls_embedding = hidden_states[:, 0, :]  # Shape: (batch_size, hidden_dim)
                feature = cls_embedding.squeeze().detach().tolist()
                return feature
            except:
                return None

        df_anime = self.df_anime.copy()
        df_anime['intro'] = df_anime['intro'].fillna(df_anime['name'])
        df_anime['intro_feature'] = df_anime['intro'].apply(intro_feature_extraction)

        df_intro = df_anime[['name', 'intro_feature']].copy()

        features = np.vstack(df_intro['intro_feature'])

        # Calculate cosine similarity
        cosine_sim = cosine_similarity(features)
        cosine_sim = (cosine_sim - cosine_sim.min()) / (cosine_sim.max() - cosine_sim.min())

        np.fill_diagonal(cosine_sim, -np.inf)

        anime_names = df_intro['name']
        cosine_sim_df = pd.DataFrame(cosine_sim, index=anime_names, columns=anime_names)

        print('Finish computing anime intro similarity score!!')
        cosine_sim_df.to_csv('data/anime_intro_similarity.csv')

    def anime_recommend(self):
        print('Start deciding recommend anime...')
        anime_type_similarity = self.anime_type_similarity.copy()
        anime_type_similarity = anime_type_similarity.set_index('name')

        anime_intro_similarity = self.anime_intro_similarity.copy()
        anime_intro_similarity = anime_intro_similarity.set_index('name')

        df_anime = self.df_anime.copy()

        target_anime = self.worksheet.get_values('B1:D1')[0]
        target_anime = [t for t in target_anime if t != '']
        parameters = self.worksheet.get_values('A6')[0]
        parameters = [settings.parameter_map[p] for p in parameters if p != '']
        print('Obtained the target animes and metrics.')

        # Get the row corresponding to the target anime
        target_similarities = pd.concat([anime_type_similarity[target_anime],
                                         anime_intro_similarity[target_anime]], axis=1).mean(axis=1)
        target_similarities = target_similarities.reset_index().rename(columns={0: 'similarity_score'})
        print('Finish merging two types of similarity scores!')

        scaled_metrics = df_anime.loc[:, ['name', 'scaled_launch', 'scaled_view', 'scaled_score', 'link']]
        # scaled_metrics = scaled_metrics.set_index('name')

        target_similarities = target_similarities.merge(scaled_metrics, on='name', how='inner')
        # target_similarities[['scaled_launch', 'scaled_view', 'scaled_score', 'link']] = scaled_metrics
        print('Append other scaled metrics!')

        target_similarities['main_metric'] = target_similarities[['similarity_score'] + parameters].mean(axis=1)
        print('Finish computing main metric!')

        # Sort the similarities in descending order and get the top 5 most similar anime
        top_recommend_anime = target_similarities.sort_values('main_metric', ascending=False).head(12)
        # top_recommend_anime = top_recommend_anime.reset_index()
        print('Determine recommended anime!!!')

        return top_recommend_anime.apply(lambda row: f'=HYPERLINK("{row['link']}", "{row['name']}")', axis=1)


if __name__ == '__main__':
    ar = AnimeRecommend()
    ar.compute_type_similarity_score()
    ar.compute_intro_similarity_score()
