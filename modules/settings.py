"""
Global settings are managed here.
"""
service_account_file = 'conf/anime-analysis-440305-14c680a5f000.json'   # credential key from google console
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

sheetname = '巴哈動畫瘋分析 / Animation Crazy Analysis'    # Google spreadsheet name
tabnames = ['Anime-Level Data',                          # Google sheet tab names
            'Episode-Level Data',
            'Episode Trend Analysis',
            'Anime Recommendation']


# mapping to column names displayed in google sheet
column_names = {
    'anime_level': {
        'name': '動畫名稱',
        'thumbnail': '縮圖',
        # 'link': '連結',
        'first_launched_date': '首播日期',

        'total_episode': '總集數',
        'total_view': '總觀看次數',
        'avg_view': '平均觀看次數',
        'score': '評分',
        'score_count': '評分人數',
        'score_rate': '評分轉換率',

        'author': '原作者',
        'agent': '代理商',
        'animator': '動畫公司',
        'director': '導演',
        'types': '類型',
        'intro': '簡介'
    },
    'episode_level': {
        'anime_name': '動畫名稱',
        'episode_name': '集數',
        'episode_order': 'Episode Order',
        'uploaded_time': '上架時間',

        'view': '觀看數',
        'comment_count': '評論數',
        'comment_rate': '評論轉換率',
        'danmu_count': '彈幕數',
        'danmu_rate': '彈幕轉換率'
    }
}

parameter_map = {
    '新作優先': 'scaled_launch',
    '高分優先': 'scaled_score',
    '人氣優先': 'scaled_view'
}