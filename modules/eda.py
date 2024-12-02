"""
Module that contains an EDA class.
"""
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt


class EDA:
    def __init__(self):
        self.scalar = StandardScaler()
        self.df_all_anime = pd.read_csv('data/all_anime.csv')
        self.df_all_episode = pd.read_csv('data/all_episode.csv')

    def score_rate_analysis(self):
        """
        1. Compute correlation between total episode and score rate
        2. Iterate 100 times:
            i. Sample 100 animations randomly
            ii. Build regression model with total_episode and score_rate
            iii. Record parameter, P-value, correlation coefficient
        3. Show experiment results as plot
        """
        df_all_anime = self.df_all_anime.copy()
        df = df_all_anime.dropna(subset='score', ignore_index=True)
        df.loc[:, 'weight'] = df.loc[:, 'total_episode'] / df.loc[:, 'total_episode'].sum()

        print(f'''Corr(total episode, scoring rate) = {df['total_episode'].corr(df['score_rate'])}.''')

        parameters = []
        pvalues = []
        corr_coeffs = []
        print('Start 100 iterations experiment...')
        for i in range(100):
            df_sample = df.sample(n=100, weights='weight', random_state=i)
            y = df_sample['score_rate']
            X = df_sample[['total_episode']]
            X = sm.add_constant(X)

            model = sm.OLS(y, X).fit()
            parameters.append(model.params.iloc[1])
            pvalues.append(model.pvalues.iloc[1])
            corr_coeffs.append(np.sqrt(model.rsquared) * np.sign(model.params.iloc[1]))

        df_plot = pd.DataFrame({'parameter': parameters,
                                'pvalue': pvalues,
                                'corr_coeff': corr_coeffs})

        # Create a figure with two subplots (1 row, 2 columns)
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot the p-values on the left
        axes[0].scatter(df_plot.index, df_plot['pvalue'], color='blue', alpha=0.7)
        axes[0].axhline(y=0.05, color='red', linestyle='--', label='Significance Threshold 0.05')
        axes[0].set_title('P-values')
        axes[0].set_xlabel('Index')
        # axes[0].set_ylabel('P-value')
        axes[0].legend()

        # Plot the correlation coefficients on the right
        axes[1].scatter(df_plot.index, df_plot['corr_coeff'], color='green', alpha=0.7)
        axes[1].axhline(y=0, color='red', linestyle='--', label='Zero Correlation')
        axes[1].set_ylim([-0.4, 0.4])
        axes[1].set_title('Correlation Coefficients')
        axes[1].set_xlabel('Index')
        # axes[1].set_ylabel('Correlation Coefficient')
        axes[1].legend()

        # Adjust layout to avoid overlap
        plt.tight_layout()

        # Save the figure as a .jpg file
        plt.savefig('plots/ep_count_to_score_rate_experiment.jpg', format='jpg', dpi=300, bbox_inches='tight')
        print('Finish storing the result plots!!!')

    def comment_rate_analysis(self):
        """
        1. Compute correlation between score and comment rate
        2. Iterate 100 times:
            i. Sample 100 animations randomly
            ii. Build regression model with score and comment_rate
            iii. Record parameter, P-value, correlation coefficient
        3. Show experiment results as plot
        """
        df_all_episode = self.df_all_episode.copy()
        df_all_anime = self.df_all_anime.copy()
        agg_anime = df_all_episode.groupby('anime_name')['comment_count'].sum().reset_index()
        df_all_anime = df_all_anime.merge(agg_anime, left_on='name', right_on='anime_name')
        df_all_anime = df_all_anime.dropna(subset=['total_view', 'score'], ignore_index=True)

        df_all_anime.loc[:, 'comment_rate'] = df_all_anime['comment_count'] / df_all_anime['total_view']
        print(f'''Corr(score, commenting rate) = {df_all_anime['score'].corr(df_all_anime['comment_rate'])}.''')

        parameters = []
        pvalues = []
        corr_coeffs = []
        print('Start 100 iterations experiment...')
        for i in range(100):
            df_sample = df_all_anime.sample(n=100, random_state=i)
            y = df_sample['comment_rate']
            X = df_sample[['score']]
            X = sm.add_constant(X)

            model = sm.OLS(y, X).fit()
            parameters.append(model.params.iloc[1])
            pvalues.append(model.pvalues.iloc[1])
            corr_coeffs.append(np.sqrt(model.rsquared) * np.sign(model.params.iloc[1]))

        df_plot = pd.DataFrame({'parameter': parameters,
                                'pvalue': pvalues,
                                'corr_coeff': corr_coeffs})

        # Create a figure with two subplots (1 row, 2 columns)
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Plot the p-values on the left
        axes[0].scatter(df_plot.index, df_plot['pvalue'], color='blue', alpha=0.7)
        axes[0].axhline(y=0.05, color='red', linestyle='--', label='Significance Threshold 0.05')
        axes[0].set_title('P-values')
        axes[0].set_xlabel('Index')
        # axes[0].set_ylabel('P-value')
        axes[0].legend()

        # Plot the correlation coefficients on the right
        axes[1].scatter(df_plot.index, df_plot['corr_coeff'], color='green', alpha=0.7)
        axes[1].axhline(y=0, color='red', linestyle='--', label='Zero Correlation')
        axes[1].set_ylim([-0.4, 0.4])
        axes[1].set_title('Correlation Coefficients')
        axes[1].set_xlabel('Index')
        # axes[1].set_ylabel('Correlation Coefficient')
        axes[1].legend()

        # Adjust layout to avoid overlap
        plt.tight_layout()

        # Save the figure as a .jpg file
        plt.savefig('plots/score_to_comment_rate_experiment.jpg', format='jpg', dpi=300, bbox_inches='tight')
        print('Finish storing the result plots!!!')

if __name__ == '__main__':
    eda = EDA()
    eda.score_rate_analysis()
    eda.comment_rate_analysis()
