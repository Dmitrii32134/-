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

# Инициализация шрифтов (исправленная версия)
try:
    font_files = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
except Exception as e:
    print(f"Не удалось загрузить шрифты: {e}")
plt.switch_backend('agg')
# COLORS = cm.Set2.colors
COLORS = [cm.tab20c.colors[0], cm.tab20c.colors[1+4], cm.tab20c.colors[2+8], cm.tab20c.colors[5+12],
          cm.tab20c.colors[1], cm.tab20c.colors[2 + 4], cm.tab20c.colors[3 + 8], cm.tab20c.colors[6 + 12],]

# Функция построения графиков по каждой термопаре отдельно 

def plot_time_series(df_list, columns, legend_labels=None, title=None, param=None,
                   filename='temperature_plot.png',
                   figsize=(10, 65/18), dpi=200,
                   hour_interval=6, resample_interval=None):
    """
    Функция для построения графиков временных рядов с кастомными метками в легенде.

    Параметры:
    df_list - Список DataFrame'ов
    columns - Список столбцов для построения (по одному из каждого DataFrame)
    legend_labels - Список меток для легенды (должен соответствовать длине df_list)
    title - Заголовок графика
    param - Параметр (единицы измерения)
    filename - Имя файла для сохранения
    figsize - Размер графика
    dpi - Разрешение
    hour_interval - Интервал между метками времени (в часах)
    resample_interval - Интервал для усреднения
    """
    plt.switch_backend('agg')
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'

    if not isinstance(df_list, list):
        raise ValueError("df_list должен быть списком DataFrame'ов.")

    if legend_labels is None:
        legend_labels = [f"DataFrame {i+1}" for i in range(len(df_list))]
    elif len(legend_labels) != len(df_list):
        raise ValueError("Длина legend_labels должна совпадать с длиной df_list.")

    if len(columns) != len(df_list):
        raise ValueError("Длина columns должна совпадать с длиной df_list.")

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor='white')
    colors = plt.cm.tab10(np.linspace(0, 1, len(df_list)))  # Количество цветов = количество графиков

    for i, df_plot in enumerate(df_list):
        col = columns[i]  # Берем соответствующий столбец для этого DataFrame

        # Преобразование даты
        if not pd.api.types.is_datetime64_any_dtype(df_plot['Date']):
            df_plot['Date'] = pd.to_datetime(df_plot['Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')

        # Усреднение данных
        if resample_interval:
            try:
                df_plot = df_plot.set_index('Date').resample(resample_interval).mean().reset_index()
                print(f"Данные DataFrame {i+1} усреднены по интервалу {resample_interval}")
            except Exception as e:
                print(f"Ошибка при ресемплинге DataFrame {i+1}: {e}. Продолжаем без ресемплинга")
                df_plot = df_plot.copy()
        else:
            df_plot = df_plot.copy()
            print("Построение без усреднения - используются все точки данных")

        if col in df_plot.columns and len(df_plot[col].dropna()) > 2:
            ax.plot(df_plot['Date'], df_plot[col],
                    linewidth=1.2,
                    alpha=0.9,
                    label=legend_labels[i],  # Используем кастомную метку
                    color=colors[i])  # Берем соответствующий цвет

    # Настройка оси времени
    date_format = mdates.DateFormatter('%H:%M\n%Y-%m-%d')
    ax.xaxis.set_major_formatter(date_format)

    # Автоматическое создание меток с интервалом
    all_dates = pd.concat([df['Date'] for df in df_list if 'Date' in df.columns])
    if not all_dates.empty:
        start_date = all_dates.min()
        end_date = all_dates.max()
        ticks = []
        current_date = start_date
        while current_date <= end_date:
            ticks.append(current_date)
            current_date += timedelta(hours=hour_interval)
        if ticks[-1] != end_date:
            ticks.append(end_date)
        ax.set_xticks(ticks)

    # Настройка осей и заголовков
    ax.set_title(title, pad=15, fontsize=14)
    if param:
        ax.set_ylabel(param, rotation=0, fontsize=12, labelpad=10, x=1, y=1.02)

    # Сетка
    ax.grid(True, linestyle='--', alpha=0.4)

    # Легенда под графиком
    lines, labels = ax.get_legend_handles_labels()
    total_series = len(labels)

    # Позиционирование графика и легенды
    if total_series >= 8:
        ax.set_position([0.1, 0.4, 0.9, 0.5])
        ncol = 2
    elif total_series >= 4:
        ax.set_position([0.1, 0.35, 0.9, 0.55])
        ncol = 2
    else:
        ax.set_position([0.1, 0.25, 0.9, 0.65])
        ncol = 1

    ax.legend(lines, labels,
             loc='upper center',
             bbox_to_anchor=(0.5, -0.2),
             fancybox=True,
             ncol=ncol,
             framealpha=1)

    # Сохранение
    fig.savefig(filename, bbox_inches='tight', dpi=dpi, facecolor='white')
    plt.close()
    print(f"График сохранен в {filename} (наборов данных: {len(df_list)})")

def plot_time_series_one(df, columns, legend_labels=None, title=None, param=None,
                               filename='temperature_plot.png',
                               figsize=(10, 65/18), dpi=200,
                               hour_interval=6, resample_interval=None):
    """
    Функция для построения графиков временных рядов для одного DataFrame.

    Параметры:
    df - DataFrame
    columns - Список столбцов для построения
    legend_labels - Список меток для легенды (необязательный, должен соответствовать длине columns)
    title - Заголовок графика
    param - Параметр (единицы измерения)
    filename - Имя файла для сохранения
    figsize - Размер графика
    dpi - Разрешение
    hour_interval - Интервал между метками времени (в часах)
    resample_interval - Интервал для усреднения
    """
    plt.switch_backend('agg')
    plt.style.use('default')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df должен быть DataFrame.")

    if isinstance(columns, str):
        columns = [columns] 
    if legend_labels is None:
        legend_labels = columns  
    elif len(legend_labels) != len(columns):
        print("Длина legend_labels не совпадает с количеством столбцов.  Легенда будет построена по умолчанию.")
        legend_labels = columns


    fig, ax = plt.subplots(figsize=figsize, dpi=dpi, facecolor='white')

    colors = plt.cm.tab10(np.linspace(0, 1, len(columns)))  

    for i, col in enumerate(columns):
        # Преобразование даты
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y %H:%M:%S', errors='coerce')

        # Усреднение данных
        if resample_interval:
            try:
                df = df.set_index('Date').resample(resample_interval).mean().reset_index()
                print(f"Данные DataFrame усреднены по интервалу {resample_interval}")
            except Exception as e:
                print(f"Ошибка при ресемплинге DataFrame: {e}. Продолжаем без ресемплинга")
                df = df.copy()
        else:
            df = df.copy()
            print("Построение без усреднения - используются все точки данных")

        if col in df.columns and len(df[col].dropna()) > 2:
            ax.plot(df['Date'], df[col],
                    linewidth=1.2,
                    alpha=0.9,
                    label=legend_labels[i],  # Assign legend label
                    color=colors[i])

    # Настройка оси времени
    date_format = mdates.DateFormatter('%H:%M\n%Y-%m-%d')
    ax.xaxis.set_major_formatter(date_format)

    # Автоматическое создание меток с интервалом
    if not df['Date'].empty:
        start_date = df['Date'].min()
        end_date = df['Date'].max()
        ticks = []
        current_date = start_date
        while current_date <= end_date:
            ticks.append(current_date)
            current_date += timedelta(hours=hour_interval)
        if ticks[-1] != end_date:
            ticks.append(end_date)
        ax.set_xticks(ticks)

    # Настройка осей и заголовков
    ax.set_title(title, pad=15, fontsize=14)
    if param:
        ax.set_ylabel(param, rotation=0, fontsize=12, labelpad=10, x=1, y=1.02)

    # Сетка
    ax.grid(True, linestyle='--', alpha=0.4)

    # Легенда под графиком
   #  lines, labels = ax.get_legend_handles_labels()
   #  total_series = len(labels)

    # Позиционирование графика и легенды
 #    if total_series >= 8:
  #       ax.set_position([0.1, 0.4, 0.9, 0.5])
 #        ncol = 2
 #    elif total_series >= 4:
  #       ax.set_position([0.1, 0.35, 0.9, 0.55])
 #        ncol = 2
 #    else:
  #       ax.set_position([0.1, 0.25, 0.9, 0.65])
  #       ncol = 1

  #   ax.legend(lines, labels,
   #           loc='upper center',
  #            bbox_to_anchor=(0.5, -0.2),
  #            fancybox=True,
  #            ncol=ncol,
  #            framealpha=1)

    # Сохранение
    fig.savefig(filename, bbox_inches='tight', dpi=dpi, facecolor='white')
    plt.close()
    print(f"График сохранен в {filename}")