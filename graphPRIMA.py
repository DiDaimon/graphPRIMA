"""Преобразует файл снятых характеристик(PRIMA) в html страницу
"""
import os
import sys
import webbrowser
from itertools import cycle

import pandas as pd
import plotly.graph_objs as go
import tabulate
from art import tprint


def suffix_ru(number: int) -> str:
    """
    Функция возвращает строку с суффиксом (файл, файла, файлов) в зависимости от
    количества файлов

    Args:
        number (int): Количество файлов

    Returns:
        str: Суффикс
    """
    if (number % 100) // 10 != 1 and number % 10 == 1:
        return 'файл'
    elif (number % 100) // 10 != 1 and number % 10 in [2, 3, 4]:
        return "файла"
    else:
        return 'файлов'


def parsing_file(file):
    """
    Функция читает переданный файл(с полным путем), преобразует данные из ПО PRIMA в 
    Pandas DataFrame, возвращает DataFrame.
    Args:
        file (str): Полный путь к файлу.

    Returns:
        (pd.DataFrame): DataFrame с характеристиками
    """

    # Прочитаем файл и найдем строку со столбцами и выясним сколько строк надо пропустить
    with open(file, 'r', encoding='cp1251') as f:
        for idx, line in enumerate(f.readlines()):
            if 'Freq' in line:
                columns_names = line
                # Ну тут понятно индекс с 0 начинается поэтому кол. +1.
                skiprows = idx + 1
                break
    # Форматируем строку и создаем список.
    columns_names = columns_names.replace("a (", "a(").split()
    # Читаем файл пропустив первые skiprows строк и создаем DataFrame,
    #с имена столбцов columns_names.
    df_temp = pd.read_csv(file, sep='\t', skiprows=skiprows, names=columns_names, header=None,
                          engine='python', encoding='cp1251')
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
    table['Наименование'] = ['Максимальное значение', 'Минимальное значение', 'Среднее значение',
                             'Медианное значение', 'Стандартное отклонение']
    for column in df.columns:
        if 'Freq' in column or 'Fmea' in column:
            continue
        table[column] = [df[column].max(), df[column].min(), df[column].mean(),
                         df[column].median(), df[column].std()]
    return table


def unique_color():
    """
    Функция возвращает последовательность цветов для графиков.

    Цвета берутся из стандартного набора matplotlib.

    Returns:
        cycle: последовательность цветов
    """
    list_colors = cycle([
        'black', 'red', 'green', 'blue', 'purple', 'brown', 'magenta', 'orange', 'gray',
        'coral', 'cornflowerblue', 'crimson', 'firebrick', 'forestgreen', 'fuchsia',
        'blueviolet', 'goldenrod', 'hotpink', 'indianred', 'indigo', 'maroon', 'navy',
        'olive', 'olivedrab', 'orangered', 'orchid', 'palevioletred', 'peru', 'rosybrown',
        'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'slateblue',
        'slategray', 'steelblue', 'tan', 'teal', 'tomato', 'turquoise', 'violet',
        'dodgerblue', 'lightseagreen', 'lightslategray', 'limegreen', 'mediumblue',
        'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue',
        'mediumturquoise', 'mediumvioletred', 'darkblue', 'darkcyan', 'darkgoldenrod',
        'darkgreen', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid',
        'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray',
        'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue'
    ])
    return cycle(list_colors)


def add_graph(df, name):
    """
    Функция добавления графика из DataFrame.
    """
    # добавляем график и его имя
    for column in df.columns:
        if 'Freq' in column or 'Fmea' in column:
            continue
        GRAPH.add_trace(
            go.Scatter(
                x=df[df.columns[0]],
                y=df[column],
                name=f'{name} {column}',
                line=dict(
                    color=(next(COLOR)),
                    width=1
                )
            )
        )
    # Далее основные настройки отображения
    GRAPH.update_layout(
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
    GRAPH.update_layout(hoverlabel_namelength=-1)

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
    GRAPH.update_layout(
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
    """
    Основная функция
    """
    tprint('graphPRIMA', font='medium')
    upload_files = []
    upload_files.extend(files)
    print(f'[+] Обнаружено: {len(upload_files)} {suffix_ru(len(upload_files))} данных')

    graph_config = {
        'toImageButtonOptions': {
            'format': 'png', 
            'filename': 'result', 
            'height': 1080, 
            'width': 1920, 
            'scale': 2
            }
        }

    for file in upload_files:
        filename = file.split(sep="\\")[-1]
        print(f'[+] Обработка файла: {filename}')
        data_df = parsing_file(file)
        add_graph(data_df, filename[:-4])
        print(f'[+] Таблица создана\n\n Таблица файла: {filename}')
        print(
            tabulate.tabulate(
                add_table(data_df, filename),
                headers=list(add_table(data_df, filename).columns),
                showindex=False, tablefmt="grid", stralign='left', numalign="left"
            ),
            end='\n\n'
        )

    GRAPH.write_html('result' + ".html", auto_open=False, config=graph_config)
    print('[+] Файл с графиками создан')
    webbrowser.open('result' + ".html")
    os.system('pause')
    os.remove('result' + ".html")


GRAPH = go.Figure()
COLOR = unique_color()

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
