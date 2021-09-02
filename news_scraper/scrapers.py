import requests
import bs4
import os
from datetime import date
import json
import xlsxwriter

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class BaseWebScraper:
    output_file_directory = '..\\output_files'

    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.categories_and_urls = dict()
        self.news_category_and_description = dict()
        self.page_categories()
        self.provider_dir_output = os.path.join(self.output_file_directory, self.name)

    def page_categories(self):
        raise NotImplementedError('Subclasses must implement this method')

    def news_and_article_description(self):
        raise NotImplementedError('Subclasses must implement this method')

    def print_content(self):
        print(f'\n\t\t\t\t\t\t{self.name}\n')
        for category_name, category_url in self.categories_and_urls.items():
            print('Category name : {0:20}  {1}_url :   {2}'.format(category_name, category_name, category_url))

        print("\n")
        for category, article_news in self.news_category_and_description.items():
            print(f'\n Category : {category}')
            for index, (article_header, article_description) in enumerate(article_news.items()):
                print(f"\n\t{index + 1} : {article_header}")
                for paragraph in article_description:
                    print(f"\t\t\t{paragraph}")

    @staticmethod
    def __remove_file(dir_path, file_extension):
        """
        Removes files with same file extension in existing directory, to update with new news article files
        """
        for output in os.listdir(dir_path):
            if output.endswith(file_extension):
                file_path = os.path.join(dir_path, output)
                print(f"Older {output} file, removed from directory\n")
                os.remove(file_path)

    def __make_dir(self):
        if not os.path.exists(self.provider_dir_output):
            os.mkdir(self.provider_dir_output)
            for category in self.news_category_and_description.keys():
                category_dir_path = os.path.join(self.provider_dir_output, category)
                os.mkdir(category_dir_path)

    def write_exel(self, file_extension=".xlsx"):
        self.__make_dir()
        for category, article_news in self.news_category_and_description.items():
            category_file_path = os.path.join(self.provider_dir_output, category)
            self.__remove_file(category_file_path, file_extension)
            file_name = f"{str(date.today())}_{category}"
            with xlsxwriter.Workbook(f'{category_file_path}/{file_name}.xlsx') as exel_file:
                worksheet = exel_file.add_worksheet()
                row = 0
                column = 0
                for index, (news_header, article_description) in enumerate(article_news.items()):
                    worksheet.write(row, column, f'{index + 1}: {news_header}')
                    row += 1
                    column += 1
                    for paragraph in article_description:
                        worksheet.write(row, column, paragraph)
                        row += 1
                    row += 2
                    column = 0
        print(f"{file_extension} files, for {self.name} provider created at {self.provider_dir_output}\n")

    def write_text(self, file_extension='.txt'):
        self.__make_dir()
        for category, article_news in self.news_category_and_description.items():
            category_file_path = os.path.join(self.provider_dir_output, category)
            self.__remove_file(category_file_path, file_extension)
            file_name = f"{str(date.today())}_{category}"
            with open(f'{category_file_path}/{file_name}.txt', 'w', encoding='utf-8') as text_file:
                for index, (news_header, article_description) in enumerate(article_news.items()):
                    text_file.write(f'{index + 1}: {news_header}\n')
                    for paragraph in article_description:
                        text_file.write(f'\t\t{paragraph}\n')
                    text_file.write('\n\n')
        print(f"{file_extension} files, for {self.name} provider created at {self.provider_dir_output}\n")

    def write_json(self, file_extension=".json"):
        self.__make_dir()
        for category, article_news in self.news_category_and_description.items():
            category_dir_path = os.path.join(self.provider_dir_output, category)
            self.__remove_file(category_dir_path, file_extension)
            file_name = f"{str(date.today())}_{category}"
            json_f = json.dumps(article_news, indent=2)
            with open(f'{category_dir_path}/{file_name}.json', "w", encoding='utf-8') as json_file:
                json_file.write(json_f)
        print(f"{file_extension} files, for {self.name} provider created at {self.provider_dir_output}\n")


class RtsWebScraper(BaseWebScraper):

    def __init__(self, url, name):
        super().__init__(url, name)

    def page_categories(self):
        page_response = requests.get(self.url)
        page_response.raise_for_status()
        rts_html = bs4.BeautifulSoup(page_response.text, "lxml")
        rts_menu = rts_html.findAll("li", class_=['level1', ''])
        for category in rts_menu:
            if len(category.find('a')) > 1:
                continue
            category_name = category.find('a').getText().strip()
            category_url = category.find('a')["href"]
            if "https://" not in category_url:
                category_url = self.url + category_url
            self.categories_and_urls[category_name] = category_url

    def news_and_article_description(self):
        for category, category_url in self.categories_and_urls.items():
            category_news = dict()
            page_response = requests.get(category_url)
            page_article_html = bs4.BeautifulSoup(page_response.text, 'lxml')
            news_articles = page_article_html.findAll('div', class_=['strip', 'info'])
            if not news_articles:
                continue
            # through site articles
            for article in news_articles:
                article_description = []
                article_header = article.find('a').getText()
                article_description.append(article.find('div',
                                                        class_=['newsTextNew newsTitle',
                                                                "newsTextNew"]).getText().strip())
                news_description_url = self.url + article.find('a')['href']

                # sub_article of article
                sub_article_response = requests.get(news_description_url)
                sub_article_response.raise_for_status()
                sub_article_description_html = bs4.BeautifulSoup(sub_article_response.text, 'lxml')
                lead_story = sub_article_description_html.find('p', class_='lead storyMainLead').getText()
                article_description.append(lead_story)
                story_text = sub_article_description_html.select('#story-text > p')

                # story in sub_article
                for story in story_text:
                    article_description.append(story.getText())

                # address of sub_article
                article_description.append(news_description_url)
                category_news[article_header] = article_description
            self.news_category_and_description[category] = category_news


class BlicWebScraper(BaseWebScraper):

    def __init__(self, url, name):
        super().__init__(url, name)

    def page_categories(self):
        page_response = requests.get(self.url)
        page_response.raise_for_status()
        blic_html = bs4.BeautifulSoup(page_response.text, "lxml")
        blic_menu = blic_html.select('.menu__main li')
        for category in blic_menu:
            if len(category.find('a')) > 1:
                continue
            category_name = category.find('a').getText().strip()
            category_url = category.find('a')["href"]
            if 'sport' in category_url:
                category_url = "https:" + category_url
            if "https://" not in category_url:
                category_url = self.url + category_url
            self.categories_and_urls[category_name] = category_url

    def news_and_article_description(self):
        for category, category_url in self.categories_and_urls.items():
            category_news = dict()
            page_response = requests.get(category_url)
            page_response.raise_for_status()
            page_article_html = bs4.BeautifulSoup(page_response.text, 'lxml')
            news_articles = page_article_html.findAll('div', class_='content-wrapper')
            if not news_articles:
                continue
            # through site articles
            for article in news_articles:
                article_description = []
                article_header = article.find('p')
                if article_header is None:
                    article_header = article.find('a').getText()
                else:
                    article_header = article.find('p').text
                news_description_url = article.find('a')['href']
                if "https://" not in news_description_url:
                    news_description_url = self.url + article.find('a')['href']

                # sub_article of article
                sub_article_response = requests.get(news_description_url)
                sub_article_response.raise_for_status()
                sub_article_description_html = bs4.BeautifulSoup(sub_article_response.text, 'lxml')
                lead_story = sub_article_description_html.find('h1').getText()
                article_description.append(lead_story)
                story_text = sub_article_description_html.select('.article-body > p')

                # story in sub_article
                for story in story_text:
                    article_description.append(story.getText())

                # address of sub_article
                article_description.append(news_description_url)
                category_news[article_header] = article_description
            self.news_category_and_description[category] = category_news
