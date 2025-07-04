# Импорт для графиков
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd
from datetime import timedelta
import matplotlib.dates as md
import matplotlib.cm as cm
import os
import matplotlib as mpl

from setting import CURRENT_DIR
# Установка шрифтов
import matplotlib.font_manager as font_manager

    font_files = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
