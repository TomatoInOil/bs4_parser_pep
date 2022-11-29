import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results, cli_args):
    """Выбор способа вывода в зависимости от наличия аргумента --pretty."""
    output = cli_args.output
    if output is not None:
        if output == "pretty":
            pretty_output(results)
        elif output == "file":
            file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    """Вывод данных построчно."""
    for row in results:
        print(*row)


def pretty_output(results):
    """Вывод данных в формате таблицы PrettyTable."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = "l"
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    """Вывод данных в файл."""
    results_dir = BASE_DIR / "results"
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f"{parser_mode}_{now_formatted}.csv"
    file_path = results_dir / file_name
    with open(file_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file, dialect="unix")
        writer.writerows(results)
    logging.info(f"Файл с результатами был сохранён: {file_path}")
