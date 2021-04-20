import os

import requests


def ensure_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)


def download_image(image_url, image_name):
    response = requests.get(image_url)
    response.raise_for_status()

    with open(image_name, "wb") as file:
        file.write(response.content)


def download_book(book_url, book_title):
    response = requests.get(book_url, verify=False)

    with open(book_title, "wb") as file:
        file.write(response.content)


def main():
    ensure_dir("./images")
    ensure_dir("./books")
    download_image(
        "https://dvmn.org/filer/canonical/1542890876/16/",
        "./images/dvmn.svg",
    )

    for book_id in range(32159, 32169):
        download_book(
            f"https://tululu.org/txt.php?id={book_id}",
            f"./books/book_{book_id}.txt",
        )


if __name__ == '__main__':
    main()
