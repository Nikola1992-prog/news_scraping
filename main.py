from news_scraper.scrapers import RtsWebScraper, BlicWebScraper
from news_scraper.utils.helper import user_input, user_method_input


def export_output(news_provider, output_methods):
    for method in output_methods:
        if method == 1:
            news_provider.print_content()
        if method == 2:
            print(f"\nPlease wait, writing .xlsx files...")
            news_provider.write_exel()
        if method == 3:
            print(f"\nPlease wait, writing .json files...")
            news_provider.write_json()
        if method == 4:
            print(f"\nPlease wait, writing .txt files...")
            news_provider.write_text()


def run_scrapers():
    rts = RtsWebScraper("https://www.rts.rs/", "RTS")
    blic = BlicWebScraper('https://www.blic.rs/', "Blic")
    providers = {1: rts, 2: blic}

    provider_to_scrape = user_input()
    output_request = user_method_input()
    for key, provider in providers.items():
        if key == provider_to_scrape:
            print(f"\nCollecting data from the {provider.name} news provider, please wait...")
            provider.news_and_article_description()
            export_output(provider, output_request)
        elif provider_to_scrape == 3:
            print(f"\nCollecting data from the {provider.name} news provider, please wait...")
            provider.news_and_article_description()
            export_output(provider, output_request)


if __name__ == "__main__":
    run_scrapers()
