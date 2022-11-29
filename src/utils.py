import logging

from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    """Получение response с перехватом ошибки загрузки страницы."""
    try:
        response = session.get(url)
        response.encoding = "utf-8"
        return response
    except RequestException:
        logging.exception(
            f"Возникла ошибка при загрузке страницы {url}", stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    """Поиск тега в супе с перехватом ошибки его отсутствия."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    error_msg = f"Не найден тег {tag} {attrs}"
    _handle_search_error(searched_tag, error_msg)
    return searched_tag


def find_tag_by_string(soup, string):
    """Поиск тега по строке с перехватом ошибки его отсутствия."""
    searched_tag = soup.find(string=string)
    error_msg = f"Не найден тег со строкой {string}"
    _handle_search_error(searched_tag, error_msg)
    return searched_tag.parent


def find_next_sibling_tag(soup, tag, attrs=None):
    """Поиск следующего одноуровнего с soup тега."""
    searched_tag = soup.find_next_sibling(tag, attrs=(attrs or {}))
    error_msg = (
        f"Не найден тег {tag} {attrs}"
        f" среди одноуровневых следующих после {soup.name}"
    )
    _handle_search_error(searched_tag, error_msg)
    return searched_tag


def _handle_search_error(searched_tag, error_msg):
    """Вызов и логирование ошибки отсутствия нужного тега."""
    if searched_tag is None:
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
