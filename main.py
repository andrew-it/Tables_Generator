"""
Module for creating tables data-set using LaTeX.
Every table.pdf in data-set has an appropriate table.csv with the same data.
You need to install some LaTeX builder for using this script.
"""
import os
import time
import csv
from typing import List

import lorem

# Row and columns ranges
from latex import build_pdf

ROW_COUNT_MIN = 2
ROW_COUNT_MAX = 10
COLUMNS_COUNT_MIN = 2
COLUMNS_COUNT_MAX = 8

# Constants for table forming
COLUMN_DELIMITER = '|'
COLUMN_SEPARATOR = '&'
NEW_ROW_SYMBOL = r'\\'
TEXT_IN_CELL_ORIENTATION = 'l'  # Left: l, Right: r, Center: c, In cm: p{Ncm}
TABLE_HORIZONTAL_LINE = '\hline'  # Used as for horizontal lines, as for a vertical once.

# Constants for replacing
TEXT_BEFORE_TABLE = '_TEXT_BEFORE_TABLE'
TEXT_AFTER_TABLE = '_TEXT_AFTER_TABLE'
TABLE = '_THE_TABLE_'
TABLE_SCHEMA = '_TABLE_SCHEMA'
TABLE_ROWS_LIST = '_TABLE_ROWS_LIST'
TABLE_TITLE = '_TABLE_TITLE'

DIRECTORY_NAME = 'tables'

TEX_DOCUMENT_PATTERN = r'\documentclass{article}' \
                       '\n' \
                       r'\usepackage[a4paper, portrait, margin=1in]{geometry}' \
                       '\n' \
                       r'\usepackage[utf8x]{inputenc}' \
                       '\n' \
                       r'\usepackage{tabularx}' \
                       '\n' \
                       r'\begin{document}' \
                       '\n' \
                       rf'{TEXT_BEFORE_TABLE}' \
                       '\n' \
                       '\n' \
                       rf'{TABLE}' \
                       '\n' \
                       rf'{TEXT_AFTER_TABLE}' \
                       '\n' \
                       r'\end{document}'

TEX_TABLE_PATTERN = r'\begin{tabular}{' \
                    rf'{TABLE_SCHEMA}' \
                    r'}' \
                    '\n' \
                    r'\hline' \
                    f'\n{TABLE_TITLE}' \
                    r'\\ \hline' \
                    f'\n' \
                    rf'{TABLE_ROWS_LIST} \\ \hline' \
                    '\n' \
                    r'\end{tabular}' \
                    '\n'


# Table example:
# \begin{center}
#   \begin{tabular}{ | l | l | l | }
#     \hline
#     1 & 2 & 3 \\ \hline
#     4 & 5 & 6 \\ \hline
#     7 & 8 & 9 \\
#     \hline
#   \end{tabular}
# \end{center}
# https://en.wikibooks.org/wiki/LaTeX/Tables --- Documentation for tables in LaTeX

def get_schema(number_of_columns: int, text_position: str = 'l') -> str:
    """
    Returns schema for a table in format: '|text_position|text_position|etc|...|'
    :param number_of_columns: Number of columns in a table
    :param text_position: Position of a text in a cell: Left (l), Right (r), center (c)
    :return:
    """
    return ('|' + text_position) * number_of_columns + '|'


def get_text(number_of_sentences: int = 1) -> str:
    return lorem.sentence() * number_of_sentences


def get_table_title(number_of_columns: int, title_generic_name: str = 'title') -> List[str]:
    return [title_generic_name + str(i) for i in range(number_of_columns)]


def generate_data(number_of_rows: int, number_of_columns: int,
                  filling_is_sentences: bool) -> List[List[str]]:
    table = []
    for r in range(number_of_rows):
        cells_in_row = []
        for c in range(number_of_columns):
            if filling_is_sentences:
                cell_filling = lorem.sentence()
            else:
                cell_filling = str(int(time.time()))
            cells_in_row.append(cell_filling)
        table.append(cells_in_row)
    return table


def generate_tex_code(table_data: List[List[str]], table_title_data: List[str]) -> str:
    text_before = lorem.paragraph()
    text_after = lorem.paragraph()

    number_of_columns = len(table_title_data)

    tex_table_title = f' {COLUMN_SEPARATOR} '.join(table_title_data)

    # List[str] -- list of rows
    table = []
    for row in table_data:
        table.append(f' {COLUMN_SEPARATOR} '.join(row))

    # list of rows -> .tex format
    tex_rows = f' {NEW_ROW_SYMBOL} {TABLE_HORIZONTAL_LINE}\n'.join(table)

    # fit columns size according to page size (assume, the table width is 15 cm)
    table_width_cm = 15
    cell_schema = 'p{' + str(int(table_width_cm / number_of_columns)) + 'cm}'
    schema = get_schema(number_of_columns, cell_schema)

    tex_table = TEX_TABLE_PATTERN \
        .replace(TABLE_ROWS_LIST, tex_rows) \
        .replace(TABLE_SCHEMA, schema) \
        .replace(TABLE_TITLE, tex_table_title)

    tex_document = TEX_DOCUMENT_PATTERN \
        .replace(TEXT_BEFORE_TABLE, text_before) \
        .replace(TABLE, tex_table) \
        .replace(TEXT_AFTER_TABLE, text_after)

    return tex_document


if __name__ == "__main__":
    for r_c in range(ROW_COUNT_MIN, ROW_COUNT_MAX):
        for c_c in range(COLUMNS_COUNT_MIN, COLUMNS_COUNT_MAX):
            for filling in [True, False]:
                # Generate table data and title
                table_data = generate_data(r_c, c_c, filling_is_sentences=filling)
                table_title = get_table_title(c_c)

                # Create dir if not exists
                if not os.path.exists(DIRECTORY_NAME):
                    os.makedirs(DIRECTORY_NAME)
                # Generate file path
                file_path = f'./{DIRECTORY_NAME}/{r_c}_{c_c}_{filling}'

                # Generate .tex code
                tex_code = generate_tex_code(table_data, table_title)

                # Create and write .pdf file
                pdf = build_pdf(tex_code)
                pdf.save_to(f'{file_path}.pdf')

                # Create and write .csv file
                with open(f'{file_path}.csv', 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file, quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow(table_title)
                    for row in table_data:
                        csv_writer.writerow(row)
