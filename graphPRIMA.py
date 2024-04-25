"""Преобразует файл снятых характеристик(PRIMA) в html страницу

версия 0_2:
    - Олег добавил новую информационную строку в начало, пропуск строк изменен с 5 на 6
Версия 0_3:
    - Миграция на 4-тую версию Plotly
    - Убрана функция получения имени файла (замена на метод .split())
    - Добавлено чтение имен столбцов из файла
    - Убрана тема по-умолчанию из графиков
    - Изменен рендер по-умолчанию на браузер (pio.renderers)
Версия 0_4:
    - pio.renderers убран
    - мелкие правки, улучшения кода(PEP8)
    - добавлен вывод таблицей(полезная информация о графике)
Версия 0_5:
    - изменен принцип чтения колонок из файла и пропуск строк (теперь функция).
    - фазовый шум читается правильно и весь.
    - из КП теперь читаются все данные
    - переработан принцип построения таблицы вспомогательных данных
Версия 0_6:
    - какого-то хрена на новом компе не открывается из plotly по .write_html(Auto_Open=True)
Версия 0_7:
    - добавлена пауза по окончанию выполнения программы, чтобы консоль с таблицей не исчезала
    - после паузы удаляется файл html
Версия 1_0:
    - удалена функция create_columns_name ее функционал передан parsing_file.
    - добавлена возможность чтения нескольких файлов.
Версия 1_0_1
    - добавлено циклический перебор цветов для мультиграфиков

    TODO перейти вместо Plotly_html на Plotly Dash
    TODO В конце концов решить проблему с шапкой файла с Олегом, стандартизировать шапку.
"""
from art import tprint
import plotly.graph_objs as go
import pandas as pd
import re
import sys
import tabulate
import webbrowser
import os
from itertools import cycle


def suffix_ru(number):
    if (number % 100) // 10 != 1 and number % 10 == 1:
        return 'файл'
    elif (number % 100) // 10 != 1 and number % 10 in [2, 3, 4]:
        return "файла"
    else:
        return 'файлов'


def parsing_file(file):
    """
    Функция читает переданный файл(с полным путем), преобразует данные из ПО PRIMA в Pandas DataFrame,
    возвращает DataFrame.
    Args:
        file (str): Полный путь к файлу.

    Returns:
        (pd.DataFrame): DataFrame с характеристиками
    """

    # Прочитаем файл и найдем строку со столбцами и выясним сколько строк надо пропустить
    with open(file, 'r') as f:
        for idx, line in enumerate(f.readlines()):
            if 'Freq' in line:
                columns_names = line
                # Ну тут понятно индекс с 0 начинается поэтому кол. +1.
                skiprows = idx + 1
                break
    # Форматируем строку и создаем список.
    columns_names = columns_names.replace("a (", "a(").split()
    # Читаем файл пропустив первые skiprows строк и создаем DataFrame, с имена столбцов columns_names.
    df_temp = pd.read_csv(file, sep='\t', skiprows=skiprows, names=columns_names, header=None, engine='python',
                          encoding='cp1251')
    print('[+] Парсинг успешен')
    return df_temp


def add_table(df: pd.DataFrame, name: str):
    """
    Функция создает ДатаФрейм с исследовательскими данными.

    Args:
        name (str): имя файла
        df (pd.DataFrame): ДатаФрейм.

    Returns:
        (pd.DataFrame): ДатаФрейм с характеристиками
    """
    table = pd.DataFrame()
    table['Наименование'] = ['Максимальное значение', 'Минимальное значение', 'Среднее значение', 'Медианное значение',
                             'Стандартное отклонение']
    for column in df.columns:
        if 'Freq' in column or 'Fmea' in column:
            continue
        table[column] = [df[column].max(), df[column].min(), df[column].mean(),
                         df[column].median(), df[column].std()]
    return table


def unique_color():
    list_colors = cycle([
        'black', 'red', 'green', 'blue', 'purple', 'brown', 'magenta', 'orange', 'gray',
        'coral',
        'cadetblue', 'chocolate',  'cornflowerblue',
        'crimson',  'firebrick', 'forestgreen', 'fuchsia', 'blueviolet',
        'goldenrod',   'hotpink', 'indianred', 'indigo',   'maroon',
        'navy', 'olive', 'olivedrab',  'orangered', 'orchid', 'palevioletred', 'peru',
        'rosybrown', 'royalblue', 'rebeccapurple', 'saddlebrown', 'salmon',
        'sandybrown', 'seagreen', 'slateblue', 'slategray', 'steelblue', 'tan', 'teal', 'tomato',
        'turquoise', 'violet', 'dodgerblue', 'lightseagreen', 'lightslategray', 'limegreen', 'mediumblue',
        'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumturquoise',
        'mediumvioletred', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgreen', 'darkmagenta',
        'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
        'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue'
    ])
    return cycle(list_colors)


def add_graph(df, name):
    """
    Функция добавления графика из DataFrame.
    """
    global graph
    global color

    # добавляем график и его имя
    for column in df.columns:
        if 'Freq' in column or 'Fmea' in column:
            continue
        graph.add_trace(
            go.Scatter(
                x=df[df.columns[0]],
                y=df[column],
                name=f'{name} {column}',
                line=dict(
                    color=(next(color)),
                    width=1
                )
            )
        )
    # Далее основные настройки отображения
    graph.update_layout(
        template="plotly_white",
        # title={
        #     'text': 'file_name',
        #     'y': 0.96,
        #     'x': 0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top'
        # },
        # height = 800,
        margin=dict(
            pad=5
        ),
        xaxis=dict(
            title='Частота, МГц',
            ticksuffix=' МГц',
            exponentformat='none',
            nticks=50,
            zeroline=False,
            automargin=True
        ),
        yaxis=dict(
            title='Уровень, дБ',
            ticksuffix=' дБ',
            nticks=20,
            automargin=True
        )
    )
    # Коррекция всплывающей подсказки чтобы имя было целиком.
    graph.update_layout(hoverlabel_namelength=-1)

    buttons = [
        dict(
            label='Линейная шкала',
            method='relayout',
            args=[{'xaxis.type': 'linear'}]
        ),
        dict(
            label='Логарифмическая шкала',
            method='relayout',
            args=[{'xaxis.type': 'log'}]
        ),
    ]
    graph.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=buttons,
                pad={"l": 10, "t": 10},
                showactive=True,
                x=0,
                xanchor="left",
                y=1.1,
                yanchor="top"
            )
        ]
    )
    print('[+] График создан')


def main(files):
    global graph
    tprint('PRIMA - GRAPH', font='medium')
    files_KP = []
    files_KP.extend(files)
    print(f'[+] Обнаружено: {len(files_KP)} {suffix_ru(len(files_KP))} данных')

    graph_config = {
        'toImageButtonOptions': {'format': 'png', 'filename': 'result', 'height': 1080, 'width': 1920, 'scale': 2}}

    for file_KP in files_KP:
        filename = file_KP.split(sep="\\")[-1]
        print(f'[+] Обработка файла: {filename}')
        data_df = parsing_file(file_KP)
        add_graph(data_df, filename[:-4])
        print(f'[+] Таблица создана\n\n{filename}')
        print(tabulate.tabulate(add_table(data_df, filename), headers=list(add_table(data_df, filename).columns),
                                showindex=False, tablefmt="grid", stralign='left', numalign="left"), end='\n\n')

    graph.write_html('result' + ".html", auto_open=False, config=graph_config)
    print('[+] Файл с графиками создан')
    webbrowser.open('result' + ".html")
    os.system('pause')
    os.remove('result' + ".html")


if __name__ == '__main__':
    graph = go.Figure()
    color = unique_color()
    # KP = [
    #     'C:\\Users\\truhachevda\\Dropbox\\Python\\АРК-НК4_№36АРК0-29-593_вибрация_20-400_кп.txt',
    #     'C:\\Users\\truhachevda\\Dropbox\\Python\\АРК-НК4_№36АРК0-29-593_вибрация_20-400_кш.txt',
    # ]
    # KP = 'C:\\Users\\di_da\\Dropbox\\Python\\ПС9_№0003_вибрация_17,7-26,5.txt')  # Тестовый файл дома
    KP = sys.argv[1:]
    main(KP)
