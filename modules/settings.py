service_account_file = 'conf/anime-analysis-440305-a2070891547c.json'
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

sheetname = 'Baha Anime Analysis'
tabnames = ['Anime-Level Data',
            'Episode-Level Data']


column_names = {
    'anime_level': {
        'name': '動畫名稱',
        'thumbnail': '縮圖',
        # 'link': '連結',

        'season': '播出季度',
        'first_launched_date': '首播日期',

        'total_view': '總觀看次數',
        'total_episode': '總集數',
        'score': '評分',
        'score_count': '評分人數',

        'author': '原作者',
        'agent': '代理商',
        'animator': '動畫公司',
        'director': '導演',
        'types': '類型'
    }
}
