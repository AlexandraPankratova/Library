import requests


def download_image(image_url, image_name):
    response = requests.get(image_url)
    response.raise_for_status()

    with open(image_name, "wb") as file:
        file.write(response.content)


def main():
    download_image(
        "https://dvmn.org/filer/canonical/1542890876/16/",
        "./images/dvmn.svg",
    )


if __name__ == '__main__':
    main()
