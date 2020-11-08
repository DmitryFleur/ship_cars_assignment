import csv
import validators


def populate_website_urls_from_file(file_path):
    websites = []

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        for row in csv_reader:
            url = f'https://{row[1]}/'
            if validators.url(url):
                websites.append(url)

    return websites
