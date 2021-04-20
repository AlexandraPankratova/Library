import os
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathvalidate import sanitize_filename


def ensure_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)


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
    with open(book_path, "wb") as file:
        file.write(book_response.content)


def main():

    load_dotenv()
    images_directory = os.getenv("DIRECTORY_FOR_IMAGES")
    books_directory = os.getenv("DIRECTORY_FOR_BOOKS")

    ensure_dir(images_directory)
    ensure_dir(books_directory)

    for book_id in range(1, 11):

        download_book_url = f"https://tululu.org/txt.php?id={book_id}"
        soup_url = f"https://tululu.org/b{book_id}/"

        book_response = requests.get(
            download_book_url,
            verify=False,
        )
        book_response.raise_for_status()

        try:
            check_for_redirect(book_response)

            soup = BeautifulSoup(
                requests.get(
                    soup_url,
                    verify=False,
                ).text,
                "lxml",
            )

            title_tag = soup.find("h1")
            title_text = title_tag.text

            book_title = title_text.split("::")[0].strip()
            book_name = f"{book_id}. " + book_title

            book_image_url = urljoin(
                "http://tululu.org",
                soup.find(class_="bookimage").find("img")["src"],
            )
            book_image_response = requests.get(book_image_url, verify=False)
            book_image_response.raise_for_status()

            image_ext = parse_file_ext(book_image_url)

            comments = soup.find_all(class_="texts")
            print(book_title)
            for comment in comments:
                print(comment.find(class_="black").text)

            book_soup = soup.find_all(class_="d_book")
            for string in book_soup:
                if string.find("b"):
                    book_genre = string.find("a").text
                    print(book_genre)

            download_image(
                book_image_response,
                f"{images_directory}{book_name}.{image_ext}",
            )

            download_txt(
                book_response,
                f"{book_name}.txt",
                books_directory,
            )
        except requests.HTTPError:
            pass


if __name__ == "__main__":
    main()
