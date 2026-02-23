# fonts/__init__.py
import os
from matplotlib import font_manager

# Mendapatkan path folder tempat file ini berada
current_dir = os.path.dirname(os.path.abspath(__file__))

# Naik satu level ke folder 'proyek', lalu masuk ke 'assets'
parent_dir = os.path.dirname(current_dir)
google_sans_path = os.path.join(parent_dir, 'fonts', 'GoogleSansCode-Regular.ttf')

# Membuat properti font
GOOGLE_SANS_FONT = font_manager.FontProperties(fname=google_sans_path)

