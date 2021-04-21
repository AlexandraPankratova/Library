import argparse
import os
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathvalidate import sanitize_filename


def parse_file_ext(url):
    unquoted_url = unquote(url)
    parsed_url = urlsplit(unquoted_url)
    return os.path.splitext(parsed_url.path)[1]


def download_image(image_response, image_name):
    with open(image_name, "wb") as file:
        file.write(image_response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(book_response, book_title, directory):
    sanitized_book_title = sanitize_filename(book_title)
    book_path = os.path.join(directory, sanitized_book_title)
    with open(book_path, "w") as file:
        file.write(book_response.text)


def parse_book_page(book_response):

    soup = BeautifulSoup(
        book_response.text,
        "lxml",
    )

    title_tag = soup.find("h1")
    title_text = title_tag.text

    book_title, book_author = title_text.split("::")

    book_image_url = urljoin(
        "http://tululu.org",
        soup.find(class_="bookimage").find("img")["src"],
    )

    comments = soup.find_all(class_="texts")
    list_of_comments = [comment.find(class_="black").text
                        for comment in comments]

    book_soup = soup.find_all(class_="d_book")
    for string in book_soup:
        if string.find("b"):
            book_genre = string.find("a").text

    book_info = {
        "title": book_title.strip(),
        "author": book_author.strip(),
        "comments": list_of_comments,
        "image_url": book_image_url,
        "genre": book_genre,
    }
    return book_info


def parse_arguments(parser, arg_name, arg_help, arg_type):
    parser.add_argument(
        arg_name,
        help=arg_help,
        type=arg_type,
    )


def main():
    load_dotenv()
    images_directory = os.getenv("DIRECTORY_FOR_IMAGES")
    books_directory = os.getenv("DIRECTORY_FOR_BOOKS")

    parser = argparse.ArgumentParser(
        description="Программа скачивает книги с сайта tululu.py")
    parse_arguments(
        parser,
        "start_id",
        "ID книги, с которой начинается скачивание.",
        int,
    )
    parse_arguments(
        parser,
        "end_id",
        "ID книги, которым заканчивается скачивание.",
        int,
    )
    books_ids = parser.parse_args()

    os.makedirs(images_directory, exist_ok=True)
    os.makedirs(books_directory, exist_ok=True)

    for book_id in range(books_ids.start_id, books_ids.end_id):

        download_book_params = {"id": book_id}

        download_book_url = "https://tululu.org/txt.php"
        book_info_response = requests.get(
            f"https://tululu.org/b{book_id}/",
            verify=False,
        )

        download_book_response = requests.get(
            download_book_url,
            params=download_book_params,
            verify=False,
        )

        try:
            download_book_response.raise_for_status()
            check_for_redirect(download_book_response)

            book_information = parse_book_page(book_info_response)
            book_name = f"{book_id}. {book_information['title']}"

            book_image_response = requests.get(
                book_information["image_url"],
                verify=False,
            )
            book_image_response.raise_for_status()
            image_ext = parse_file_ext(book_information["image_url"])

            download_image(
                book_image_response,
                f"{images_directory}{book_name}{image_ext}",
            )

            download_txt(
                download_book_response,
                f"{book_name}.txt",
                books_directory,
            )
        except requests.HTTPError:
            print(f"Book {book_id} does not have txt format.")
            pass


if __name__ == "__main__":
    main()
