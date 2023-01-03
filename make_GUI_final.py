import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import requests
from bs4 import BeautifulSoup
from newspaper import Article
from konlpy.tag import Okt
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


class CrawlingGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # select_site_group (크롤링할 사이트 선택)
        self.select_site_group = QGroupBox('Crawling Site')
        self.naver = QCheckBox('네이버')
        self.daum = QCheckBox('다음')
        self.donga = QCheckBox('동아')
        self.checkbox_list = [self.naver, self.daum, self.donga]
        self.checked_box = []

        # keyword_group (크롤링할 키워드 입력)
        self.keyword_group = QGroupBox('Keyword')
        self.keyword = QLineEdit()  # 키워드 넣는 박스
        self.keyword.setFixedWidth(100)

        # page_range_group (크롤링할 페이지 범위 입력)
        self.page_range_group = QGroupBox('Page Range')
        self.page_range = QLineEdit()
        self.page_range.setFixedWidth(100)

        # start_quit_group (크롤링 시작 버튼)
        self.start_quit_group = QGroupBox()
        self.start_quit_group.setFlat(True)
        self.start = QPushButton('Start')
        self.start.setShortcut('Ctrl+S')
        self.start.clicked.connect(self.start_crawling)
        self.quit = QPushButton('Quit')
        self.quit.setShortcut('Ctrl+Q')
        self.quit.clicked.connect(qApp.quit)

        # select_site_group LAYOUT
        self.site_box = QVBoxLayout()
        self.site_box.addWidget(self.naver)
        self.site_box.addWidget(self.daum)
        self.site_box.addWidget(self.donga)
        self.select_site_group.setLayout(self.site_box)

        # keyword_group LAYOUT
        self.keyword_box = QVBoxLayout()
        self.keyword_box.addWidget(self.keyword)
        self.keyword_group.setLayout(self.keyword_box)

        # page_range_group LAYOUT
        self.page_range_box = QVBoxLayout()
        self.page_range_box.addWidget(self.page_range)
        self.page_range_group.setLayout(self.page_range_box)

        # start_quit_group LAYOUT
        self.start_quit_box = QVBoxLayout()
        self.start_quit_box.addWidget(self.start)
        self.start_quit_box.addWidget(self.quit)
        self.start_quit_group.setLayout(self.start_quit_box)

        # LAYOUT & WINDOW
        grid = QGridLayout()
        grid.addWidget(self.select_site_group, 0, 0)
        grid.addWidget(self.keyword_group, 1, 0)
        grid.addWidget(self.page_range_group, 2, 0)
        grid.addWidget(self.start_quit_group, 3, 1)
        self.setLayout(grid)

        self.setWindowTitle('Crawling GUI')
        self.setWindowIcon(QIcon('crawling.png'))
        self.setGeometry(300, 300, 480, 320)
        self.show()

        # WARNING MESSAGE BOX
        self.warning = QMessageBox()
        self.warning.setIcon(QMessageBox.Warning)
        self.warning.setWindowIcon(QIcon('warning.png'))

        # INFORMATION MESSAGE BOX
        self.information = QMessageBox()
        self.information.setIcon(QMessageBox.Information)
        self.information.setWindowIcon(QIcon('information.png'))

    def start_crawling(self):

        global crawling_url_list, article_file, tag, graph_file
        for chkbox in self.checkbox_list:
            if chkbox.isChecked():
                self.checked_box.append(chkbox)

        self.keyword_text = self.keyword.text()
        self.page_range_text = self.page_range.text()

        if self.checked_box == [] or self.keyword_text == '' or self.page_range_text == '':
            self.warning.setWindowTitle('Error')
            self.warning.setText('모든 항목을 입력해 주세요.')
            self.warning.exec_()
            self.checked_box = []

        else:
            for checked in self.checked_box:
                link = []

                for page in range(int(self.page_range_text)):

                    if checked == self.naver:
                        article_file = '네이버 뉴스 기사.txt'
                        graph_file = '네이버 TOP 10.png'
                        URL_BEFORE_KEYWORD = "https://search.naver.com/search.naver?&where=news&query="
                        URL_BEFORE_PAGE_NUM = '&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=0&ds=&de=&docid=&nso=so:r,p:all,a:all&mynews=0&start='
                        URL_REST = '&refresh_start=0'
                        tag = 'div.news_wrap.api_ani_send > div > a'
                        current_page = 1 + page * 10
                        crawling_url_list = URL_BEFORE_KEYWORD + self.keyword_text + URL_BEFORE_PAGE_NUM + str(
                            current_page) + URL_REST

                    if checked == self.daum:
                        article_file = '다음 뉴스 기사.txt'
                        graph_file = '다음 TOP 10.png'
                        URL_BEFORE_KEYWORD = 'https://search.daum.net/search?w=news&DA=PGD&enc=utf8&cluster=y&cluster_page=1&q='
                        URL_BEFORE_PAGE_NUM = '&p='
                        URL_REST = ''
                        tag = '#clusterResultUL > li > div > div > div > a'
                        current_page = 1 + page
                        crawling_url_list = URL_BEFORE_KEYWORD + self.keyword_text + URL_BEFORE_PAGE_NUM + str(
                            current_page) + URL_REST

                    if checked == self.donga:
                        article_file = '동아 뉴스 기사.txt'
                        graph_file = '동아 TOP 10.png'
                        URL_BEFORE_PAGE_NUM = 'http://www.donga.com/news/search?p='
                        URL_BEFORE_KEYWORD = '&query='
                        URL_REST = '&check_news=1&more=1&sorting=3&search_date=1&v1=&v2=&range=3'
                        tag = 'p.txt > a'
                        current_page = 1 + page * 15
                        crawling_url_list = URL_BEFORE_PAGE_NUM + str(
                            current_page) + URL_BEFORE_KEYWORD + self.keyword_text + URL_REST

                    response = requests.get(crawling_url_list)
                    soup = BeautifulSoup(response.text, 'lxml')
                    url_tag = soup.select(tag)

                    for url in url_tag:
                        link.append(url['href'])

                f = open(article_file, 'w', encoding='utf8')
                i = 1
                for url2 in link:
                    article = Article(url2, language='ko')

                    try:
                        article.download()
                        article.parse()
                    except:
                        self.information.setWindowTitle('Article Saving Error')
                        self.information.setText('- %d번째 URL을 크롤링할 수 없습니다.' % i)
                        self.information.exec()
                        continue

                    news_title = article.title
                    news_content = article.text

                    f.write(news_title)
                    f.write(news_content)

                    i += 1
                f.close()

                self.information.setWindowTitle('Article Saved')
                self.information.setText('%s 관련 뉴스기사 %s 페이지 (기사 %d개)가 저장되었습니다.\n(%s)' %
                                         (self.keyword_text, self.page_range_text, i - 1, article_file))
                self.information.exec()

                font_location = 'NanumGothic.ttf'
                font_name = fm.FontProperties(fname=font_location).get_name()

                g = open(article_file, 'r', encoding='utf8')
                engine = Okt()  # Open Korea Text
                data = g.read()
                all_nouns = engine.nouns(data)
                nouns = [n for n in all_nouns if len(n) > 1]

                count = Counter(nouns)
                rank = count.most_common(10)
                top = dict(rank)

                fig = plt.gcf()  # get reference to the current figure
                fig.set_size_inches(15, 10)
                matplotlib.rc('font', family=font_name, size=20)
                plt.title('기사에 많이 나온 단어 Top 10', fontsize=35)
                plt.xlabel('기사에 나온 단어', fontsize=30)
                plt.ylabel('기사에 나온 단어의 개수', fontsize=30)
                plt.bar(top.keys(), top.values(), color='#FFA7A7')
                plt.savefig(graph_file)
                plt.clf()  # clear figure

                self.information.setWindowTitle('Graph Saved')
                self.information.setText('%s 관련 뉴스기사에서의 상위 10개의 단어가 저장되었습니다.\n(%s)' %
                                         (self.keyword_text, graph_file))
                self.information.exec()

                g.close()
            self.checked_box = []


if __name__ == '__main__':
    app = QApplication(sys.argv)
    crawler = CrawlingGUI()
    sys.exit(app.exec())  # 메인 이벤트 루프에 진입하여 본격적으로 코드 실행, 프로그램이 종료될 때까지 무한 루프 상태로 돌아감
