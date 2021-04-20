import os

import requests


def ensure_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)


def download_image(image_response, image_name):
    with open(image_name, "wb") as file:
        file.write(image_response.content)


def download_book(response, book_title):
    with open(book_title, "wb") as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def main():
    ensure_dir("./images")
    ensure_dir("./books")

    image_url = "https://dvmn.org/filer/canonical/1542890876/16/"
    image_response = requests.get(image_url)
    image_response.raise_for_status()

    download_image(
        image_response,
        "./images/dvmn.svg",
    )

    for book_id in range(32159, 32169):
        book_response = requests.get(
            f"https://tululu.org/txt.php?id={book_id}",
            verify=False,
        )
        book_response.raise_for_status()

        try:
            check_for_redirect(book_response)
            download_book(
                book_response,
                f"./books/book_{book_id}.txt",
            )
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
