import os

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from dotenv import load_dotenv


def ensure_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)


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

    image_url = "https://dvmn.org/filer/canonical/1542890876/16/"
    image_response = requests.get(image_url)
    image_response.raise_for_status()

    download_image(
        image_response,
        f"{images_directory}dvmn.svg",
    )

    for book_id in range(1, 11):
        book_response = requests.get(
            f"https://tululu.org/txt.php?id={book_id}",
            verify=False,
        )
        book_response.raise_for_status()

        soup = BeautifulSoup(
            requests.get(
                f"https://tululu.org/b{book_id}/",
                verify=False,
            ).text,
            'lxml',
        )

        title_tag = soup.find('h1')
        title_text = title_tag.text
        book_title = f"{book_id}. "+title_text.split("::")[0].strip()

        try:
            check_for_redirect(book_response)
            download_txt(
                book_response,
                f"{book_title}.txt",
                books_directory,
            )
        except requests.HTTPError:
            pass


if __name__ == "__main__":
    main()
