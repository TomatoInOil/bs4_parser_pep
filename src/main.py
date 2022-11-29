import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, MAIN_PEPS_URL
from outputs import control_output
from utils import (
    find_next_sibling_tag,
    find_tag,
    find_tag_by_string,
    get_response,
)


def whats_new(session):
    """Парсит ссылки на статьи о нововведениях в Python."""
    whats_new_url = urljoin(MAIN_DOC_URL, "whatsnew/")
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features="lxml")

    main_div = find_tag(soup, "section", attrs={"id": "what-s-new-in-python"})
    div_with_ul = find_tag(main_div, "div", attrs={"class": "toctree-wrapper"})
    sections_by_python = div_with_ul.find_all(
        "li", attrs={"class": "toctree-l1"}
    )

    results = [("Ссылка на статью", "Заголовок", "Редактор, Автор")]
    translate_table = str.maketrans("", "", "\n")
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, "a")
        version_link = urljoin(whats_new_url, version_a_tag["href"])
        response = get_response(session, version_link)
        if response is None:
            return
        soup = BeautifulSoup(response.text, features="lxml")
        h1 = find_tag(soup, "h1")
        dl = find_tag(soup, "dl")
        dl_text = dl.text.translate(translate_table)
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    """Парсит информацию о статусах версий Python."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, "lxml")

    sidebar = find_tag(soup, "div", attrs={"class": "sphinxsidebarwrapper"})
    ul_tags = sidebar.find_all("ul")

    for ul in ul_tags:
        if "All versions" in ul.text:
            a_tags = ul.find_all("a")
            break
    else:
        raise Exception("Ничего не нашлось")

    results = [("Ссылка на документацию", "Версия", "Статус")]
    pattern = r"Python (?P<version>\d\.\d+) \((?P<status>.*)\)"
    for a_tag in a_tags:
        link = a_tag["href"]
        match = re.search(pattern, a_tag.text)
        if match is None:
            version, status = a_tag.text, ""
        else:
            version, status = match.groups()
        results.append((link, version, status))

    return results


def download(session):
    """Скачивает архив с актуальной документацией."""
    downloads_url = urljoin(MAIN_DOC_URL, "download.html")
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, "lxml")

    main_div = find_tag(soup, "div", attrs={"role": "main"})
    table_tag = find_tag(main_div, "table", attrs={"class": "docutils"})

    pdf_a4_tag = find_tag(
        table_tag, "a", attrs={"href": re.compile(r".+pdf-a4\.zip$")}
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag["href"])
    filename = archive_url.split("/")[-1]
    downloads_dir = BASE_DIR / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, "wb") as file:
        file.write(response.content)
    logging.info(f"Архив был загружен и сохранён: {archive_path}")


def pep(session):
    """Парсит информацию о статусах PEP."""
    response = get_response(session, MAIN_PEPS_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, "lxml")

    section_num_index = find_tag(
        soup, "section", attrs={"id": "numerical-index"}
    )
    table = find_tag(section_num_index, "tbody")
    rows = table.find_all("tr")
    status_count = {}
    for row in tqdm(rows):
        status_abbr = find_tag(row, "abbr").text
        try:
            status_f_table = EXPECTED_STATUS[status_abbr[1:]]
        except KeyError:
            logging.exception(
                f"Аббревиатура {status_abbr} не соответствует"
                " ни одному из ожидаемых статусов.",
                stack_info=True,
            )
        link = urljoin(MAIN_PEPS_URL, find_tag(row, "a")["href"])

        card_response = get_response(session, link)
        if response is None:
            return
        card_soup = BeautifulSoup(card_response.text, "lxml")

        pep_content = find_tag(
            card_soup, "section", attrs={"id": "pep-content"}
        )
        dl = find_tag(pep_content, "dl")
        status_dt = find_tag_by_string(dl, string=re.compile(r"^Status$"))
        status_dd = find_next_sibling_tag(status_dt, "dd")
        status_f_card = status_dd.text
        if status_f_card not in status_f_table:
            logging.warning(
                f"Несовпадающий статус для {link}\n"
                f"Статус в карточке: {status_f_card}\n"
                f"Ожидаемые статусы: {status_f_table}"
            )
        if status_f_card in status_count:
            status_count[status_f_card] += 1
        else:
            status_count[status_f_card] = 1

    results = [("Статус", "Количество")]
    list_of_counted_statuses = sorted(
        status_count.items(), key=lambda x: -x[1]
    )
    results.extend(list_of_counted_statuses)
    results.append(("Total", len(rows)))
    return results


MODE_TO_FUNCTION = {
    "whats-new": whats_new,
    "latest-versions": latest_versions,
    "download": download,
    "pep": pep,
}


def main():
    configure_logging()
    logging.info("Парсер запущен!")

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f"Аргументы командной строки: {args}")

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info("Парсер завершил работу.")


if __name__ == "__main__":
    main()
