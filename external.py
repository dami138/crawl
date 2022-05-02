import argparse
import sys, os
import urllib
import re
from pandas import DataFrame
from pymongo import MongoClient
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from tqdm import tqdm


# todo 각 소스별로 가져올 개수를 정해야함.. todo로 검색하기

def get_last_page(url):
    html_text = requests.get(url)
    htmls = BeautifulSoup(html_text.text, "html.parser")
    pagination = htmls.find("div", {"class": "tplPagination"})
    results = pagination.find_all("li")
    pages = []
    for result in results[1:5]:  # 페이지수 설정
        pages.append(int(result.find("a").string))

    return pages[-1]


def extract_job(item):
    # title
    post_list_info = item.find("div", {"class": "post-list-info"})
    title = ""
    try:
        title = post_list_info.find("a")["title"]

    except:
        return {}
    # company
    company = item.find("div", {"class": "post-list-corp"}).find("a")["title"]

    # location
    option = post_list_info.find("p", {"class": "option"})

    try:
        location = option.find("span", {"class": "loc long"}).string
    except:
        return {}

    # qualification
    qualification = ""
    all_span = option.find_all("span")
    for span_html in all_span[0:2]:
        qualification += span_html.string + " "

    # position
    position = all_span[2].string
    # tag
    tag = post_list_info.find("p", {"class": "etc"}).string

    # link
    data_gno = item["data-gno"]
    link = f"http://www.jobkorea.co.kr/Recruit/GI_Read/{data_gno}"

    # text2
    text2 = "· 회사:\t" + company + \
            "\n· 위치:\t" + location + \
            "\n· 자격:\t" + qualification + \
            "\n· 고용형태:\t" + position + \
            "\n· 태그:\t" + tag

    return {"source": 'JobKorea', "title": title, "date": '', "url": link, "text": "", "text2": text2, "img": '',
            "subtitle": ''}


def extract_jobs(last_page, url):
    # 1페이지 부터 ~ last_page까지
    jobs = []
    for page in range(last_page):
        print(f"{page + 1}페이지 출력합니다.")
        html_text = requests.get(f"{url}&Page_No={page + 1}")
        htmls = BeautifulSoup(html_text.text, "html.parser")
        items = htmls.find_all("li", {"class": "list-post"})
        # items는 한 페이지에 올라온 모든 직업공고 htmls가 담겨짐

        for item in items:
            job = extract_job(item)

            if not job == {}:
                jobs.append(job)
                # DB삽입
                client = MongoClient("mongodb://localhost:27017")
                db = client.crawl
                db['external'].insert_one(job)

    return jobs


def JobKorea():
    url = "https://www.jobkorea.co.kr/Search/?local=D000%2CI000%2CB000%2CG000%2CO000%2CE000%2CM000%2CJ000%2CA000%2CC000%2CH000%2CF000%2CL000%2CP000%2C1000%2CK000%2CQ000%2CN000"
    # last_page = get_last_page(url)
    last_page = 5  # todo 개수설정 (마지막 페이지 정하기 한페이지당 20개)
    jobs = extract_jobs(last_page, url)
    #### 데이터 처리 ######################################################
    # date = date_f()

    # print('데이터프레임 변환\n')
    # news_df = DataFrame(jobs).transpose().T

    # xlsx_file_name = '{}_{}개_{}.xlsx'.format('jobkorea', last_page * 20, date)
    # news_df.to_excel(xlsx_file_name)

    # print('엑셀 저장 완료')


def extract_thinkText(url):
    req = requests.get(url)
    req.encoding = None
    soup2 = BeautifulSoup(req.text, 'html.parser')

    img = ''

    text = BeautifulSoup(str(soup2.find('div', {'class': 'info-cont'}))).text.replace("●", "\n●").strip()

    poster = soup2.find('img', {'id': 'poster'})

    if poster:
        img = 'https://www.thinkcontest.com' + str(poster["src"])

    return text, img


def ThinkGood():
    print('씽굿 크롤링 시작')
    print('\n' + '=' * 100 + '\n')

    res = {}
    maxPage = 4  # todo 개수설정 (한페이지 10개)

    pbar = tqdm(total=maxPage, leave=True)
    for page in range(1, maxPage + 1):
        title = ""
        period = ""
        n_url = ""
        category = ""
        host = ""

        url = 'https://www.thinkcontest.com/Contest/CateField.html?page=' + str(page)
        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find('table', attrs='type-2 mg-t-5 contest-table')
        table_rows = table.find_all('tr')

        for tr in range(1, len(table_rows)):
            td = table_rows[tr].find_all('td')
            for i in range(len(td)):
                if i == 0:
                    divs = td[i].find_all('div')
                    title = divs[0].find('a').text  # 제목
                    n_url = 'https://www.thinkcontest.com' + divs[0].find('a').get('href')  # url

                    text, img = extract_thinkText(n_url)

                    labelingTmp = divs[0].find('span')
                    if labelingTmp: labeling = labelingTmp.text
                    fieldListTmp = divs[1].find_all('span', attrs='cate-name')
                    category = []  # 카테고리
                    for tmp in fieldListTmp:
                        category.append(tmp.text)

                elif i == 1:
                    host = td[i].text

                elif i == 3:
                    period = td[i].text.strip()
                    # tmp = period.replace('\t', '').split('~')
                    # start = tmp[0] #시작일
                    # end = tmp[1] #마감일

                else:

                    pass

            res[(page - 1) * 10 + (tr - 1)] = {'source': 'ThinkGood',
                                               'title': title,
                                               'date': str(period),
                                               'url': n_url,
                                               'text': text,
                                               'text2': '',
                                               'img': img,
                                               'subtitle': ''
                                               }

            # print("{}: {}".format((page-1)*10+(tr-1),res[(page-1)*10+(tr-1)]))
            # DB삽입
            client = MongoClient("mongodb://localhost:27017")
            db = client.crawl
            db['external'].insert_one(res[(page - 1) * 10 + (tr - 1)])  # DB삽입
            pbar.update(1)

    print('finish')

    pbar.close()

    #### 데이터 처리 ######################################################

    # date = date_f()
    #
    # print('데이터프레임 변환\n')
    # df = pd.DataFrame(res).T
    # xlsx_file_name = '{}_{}개_{}.xlsx'.format('thinkGood', maxPage*10, date)
    # df.to_excel(xlsx_file_name)


def crawling_AI_text(url):
    req = requests.get(url)
    req.encoding = None
    soup2 = BeautifulSoup(req.text, 'html.parser')

    text = BeautifulSoup(str(soup2.find('article', {'id': 'article-view-content-div'})).replace("<br/>", "\n")) \
        .text.strip().replace('\r', '').replace('<br/>', '\n').replace('\t', '')

    matchObj = re.search('<!--', text)
    if matchObj:
        text2 = text[:matchObj.start()]
    else :
        text2 = text

    src = ''
    if soup2.select_one("article > div > figure > img"):
        src = soup2.select_one("article > div > figure > img")["src"]

    newsDate = soup2.find('ul', {'class': 'infomation'}).select("li")[1].text.replace(" 입력 ", "")

    subtitle = BeautifulSoup(str(soup2.find('h4', {'class': 'subheading'})).replace("<br/>", "\n")) \
        .text.strip().replace('\r', '').replace('<br/>', '\n').replace('\t', '').replace("\\n\\n", "   ")

    return (text2, src, subtitle, newsDate)



def AITimes():
    news_num =10  # todo 개수

    ################  크롤링 시작 ########################

    print('AITimes 크롤링 시작')
    print('\n' + '=' * 100 + '\n')
    # ####동적 제어로 페이지 넘어가며 크롤링
    news_dict = {}
    idx = 1
    pbar = tqdm(total=news_num, leave=True)

    page = 1

    while idx < news_num:

        target_url = 'http://www.aitimes.com/news/articleList.html?page={}&total=2234&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&box_idxno=30&sc_multi_code=&sc_is_image=&sc_is_movie=&sc_user_name=&sc_order_by=E'.format(
            page)
        html = urllib.request.urlopen(target_url).read()
        soup1 = BeautifulSoup(html, 'html.parser')

        time.sleep(0.5)

        table = soup1.find('ul', {'class': 'type1'})
        titles = table.select('li > h4 > a')

        for n in titles[:min(len(titles), news_num - idx + 1)]:
            n_url = 'http://www.aitimes.com/' + n['href']
            main_text, src, subtitle, newsDate = crawling_AI_text(n_url)
            if (main_text):
                news_dict[idx] = {'source': "AITimes",
                                  'title': n.text,
                                  'date': str(newsDate),
                                  'url': n_url,
                                  'text': main_text,
                                  'text2': '',
                                  'img': src,
                                  'subtitle': '' if (subtitle == 'None') else subtitle
                                  }
                # DB삽입
                client = MongoClient("mongodb://localhost:27017")
                db = client.crawl
                db['external'].insert_one(news_dict[idx])  # DB삽입
                idx += 1
                pbar.update(1)

        if idx < news_num:
            # 다음 페이지
            page += 1
            time.sleep(0.5)

        else:
            pbar.close()

            print('\n브라우저를 종료합니다.\n' + '=' * 100)
            time.sleep(0.7)
            break

    ### 데이터 처리 ######################################################
    # date = date_f()
    #
    # print('데이터프레임 변환\n')
    # news_df = DataFrame(news_dict).T
    #
    # folder_path = os.getcwd()
    # xlsx_file_name = 'AITimes_본문_{}개_{}.xlsx'.format(news_num, date)
    #
    # news_df.to_excel(xlsx_file_name)
    #
    # print('엑셀 저장 완료 | 경로 : {}\\{}\n'.format(folder_path, xlsx_file_name))



def MedicalTimes():
    news_num = 300  # todo 개수

    ################  크롤링 시작 ########################

    print('MedicalTimes 크롤링 시작')
    print('\n' + '=' * 100 + '\n')
    # ####동적 제어로 페이지 넘어가며 크롤링
    news_dict = {}
    idx = 1
    pbar = tqdm(total=news_num, leave=True)

    page = 0

    while idx < news_num:

        target_url = 'https://www.medicaltimes.com/Main/News/List.html?page={}&MainCate=&SubCate=&News_Level=&SectionTop=&ReporterID=&TargetDate=&keyword='.format(
            page)
        html = urllib.request.urlopen(target_url).read()
        soup1 = BeautifulSoup(html, 'html.parser')

        time.sleep(0.5)

        table = soup1.find('div', {'class': 'newsList_wrap'})
        articles = table.select('article')

        for n in articles[:min(len(articles), news_num - idx + 1)]:
            url = n.select_one('a')
            n_url = 'https://www.medicaltimes.com' + url['href']
            title = url.select_one('div > h4').text
            main_text = url.find('div', {'class': 'list_txt'}).text
            src = url.select_one('div > img')["src"]
            newsDate = url.find('span', {'class': 'newsList_cont_date'}).text
            if (main_text):
                news_dict[idx] = {'source': "MedicalTimes",
                                  'title': title,
                                  'date': str(newsDate)[:10],
                                  'url': n_url,
                                  'text': main_text,
                                  'text2': '',
                                  'img': src,
                                  'subtitle': ''
                                  }
                # DB삽입
                client = MongoClient("mongodb://localhost:27017")
                db = client.crawl
                db['external'].insert_one(news_dict[idx])  # DB삽입
                idx += 1
                pbar.update(1)

        if idx < news_num:
            # 다음 페이지
            page += 1
            time.sleep(0.5)

        else:
            pbar.close()


def crawling_KBS_text(url):
    req = requests.get(url)
    req.encoding = None
    soup = BeautifulSoup(req.text, 'html.parser')
    text = BeautifulSoup(str(soup.find('div', {'id': 'cont_newstext'})).replace("<br/>", "\n")).text.strip()

    src = ''
    # 자꾸 기본이미지만 줌.... 막아놓은 건가 싶음
    # img = soup.find_all('img', {'id': "imgVodThumbnail"})
    # print(img)
    # if img:
    #     src = img["src"]

    newsDate = soup.find('em', {'class': 'date'}).text.replace("입력 ", "")
    return (text.replace('\r', '').replace('<br/>', '\n').replace('\t', ''), src, newsDate)


def crawling_et_text(url):
    req = requests.get(url)
    req.encoding = None
    soup = BeautifulSoup(req.text, 'html.parser')
    text = BeautifulSoup(str(soup.find('div', {'class': 'article_txt'})).replace("<br/>", "\n")).text.strip()

    src = ''
    if soup.select_one("section > section > article > div > div > figure > a > img"):
        src = soup.select_one("section > section > article > div > div > figure > a > img")["src"]

    newsDate = soup.find('time', {'class': 'date'}).text.replace("발행일 : ", "")
    return (text.replace('\r', '').replace('<br/>', '\n').replace('\t', ''), src, newsDate)


def News(source, source_url, news_num=20):
    print(source + '뉴스 크롤링 시작')
    print('\n' + '=' * 100 + '\n')

    print('브라우저를 실행시킵니다(자동 제어)\n')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_path = './chromedriver'
    browser = webdriver.Chrome(chrome_path, chrome_options=chrome_options)

    news_url = source_url

    browser.get(news_url)
    time.sleep(0.5)

    ################ 뉴스 크롤링 ########################

    print('\n크롤링을 시작합니다.')
    # ####동적 제어로 페이지 넘어가며 크롤링
    news_dict = {}
    idx = 1
    cur_page = 1

    pbar = tqdm(total=news_num, leave=True)

    while idx < news_num:

        table = browser.find_element_by_xpath('//ul[@class="list_news"]')
        li_list = table.find_elements_by_xpath('./li[contains(@id, "sp_nws")]')
        area_list = [li.find_element_by_xpath('.//div[@class="news_area"]') for li in li_list]
        a_list = [area.find_element_by_xpath('.//a[@class="news_tit"]') for area in area_list]

        for n in a_list[:min(len(a_list), news_num - idx + 1)]:
            n_url = n.get_attribute('href')
            main_text = ''

            if source == "KBS":
                main_text, src, newsDate = crawling_KBS_text(n_url)
            elif source == "ETNews":

                main_text, src, newsDate = crawling_et_text(n_url)

            if (main_text):
                news_dict[idx] = {'source': source,
                                  'title': n.get_attribute('title'),
                                  'date': str(newsDate),
                                  'url': n_url,
                                  'text': main_text,
                                  'text2': '',
                                  'img': src,
                                  'subtitle': ''
                                  }
                # DB삽입
                client = MongoClient("mongodb://localhost:27017")
                db = client.crawl
                db['external'].insert_one(news_dict[idx])
                idx += 1
                pbar.update(1)

        if idx < news_num:
            cur_page += 1

            pages = browser.find_element_by_xpath('//div[@class="sc_page_inner"]')
            next_page_url = [p for p in pages.find_elements_by_xpath('.//a') if p.text == str(cur_page)][
                0].get_attribute(
                'href')

            browser.get(next_page_url)
            time.sleep(0.5)
        else:
            pbar.close()

            print('\n브라우저를 종료합니다.\n' + '=' * 100)
            time.sleep(0.7)
            browser.close()
            break

    #### 데이터 처리 ######################################################
    # date = date_f()
    # print('데이터프레임 변환\n')
    # news_df = DataFrame(news_dict).T
    #
    # folder_path = os.getcwd()
    # xlsx_file_name = '{}_본문_{}개_{}.xlsx'.format(source, news_num, date)
    #
    # news_df.to_excel(xlsx_file_name)
    #
    # print('엑셀 저장 완료 | 경로 : {}\\{}\n'.format(folder_path, xlsx_file_name))



def date_f():
    ###### 날짜 저장 ##########
    date = str(datetime.now())
    date = date[:date.rfind(':')].replace(' ', '_')
    date = date.replace(':', '시') + '분'
    return date


def dropDB():
    # db 비우기
    client = MongoClient("mongodb://localhost:27017")
    db = client.crawl
    db['external'].drop()


if __name__ == '__main__':
    # python external.py -K AI 하면 kbs에서 검색어 AI로 최근 1주 글 n개씩 뽑아옴

    # python external.py -J -T -A -K -E

    parser = argparse.ArgumentParser()

    parser.add_argument('--dropDB', '-D', action='store_true',
                        help='dropDB for new crawling')

    parser.add_argument('--jobkorea', '-J', action='store_true',
                        help='jobkorea')
    parser.add_argument('--thinkgood', '-T', action='store_true',
                        help='thinkgood')
    parser.add_argument('--aitimes', '-A', action='store_true',
                        help='AI Times')
    parser.add_argument('--medicaltimes', '-M', action='store_true',
                        help='MedicalTimes')
    parser.add_argument('--kbs', '-K', action='store_true',
                        help='KBS')
    parser.add_argument('--etnews', '-E', action='store_true',
                        help='전자신문')
    # parser.add_argument('--ja', '-JA',action='store_true',
    #                     help='중앙일보')

    args = parser.parse_args()

    if args.thinkgood:
        ThinkGood()

    if args.jobkorea:
        JobKorea()

    if args.aitimes:
        AITimes()

    if args.medicaltimes:
        MedicalTimes()

    if args.kbs:
        source_url = 'https://search.naver.com/search.naver?where=news&query=kbs&sm=tab_clk.jou&sort=1&photo=0&field=0&pd=1&ds=2021.11.28&de=2021.12.05&docid=&related=0&mynews=0&office_type=&office_section_code=&news_office_checked=&nso=so%3Add%2Cp%3A1w&is_sug_officeid=1'
        News('KBS', source_url, 100)  # todo 개수

        # 키워드 '건축'
        source_url2 = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&query=%EA%B1%B4%EC%B6%95&tqi=hElnLlprvTossMt%2BLpRssssstRG-468912&nso=so%3Add%2Cp%3A1w&de=2022.04.27&ds=2022.04.20&mynews=1&news_office_checked=1056&office_section_code=2&office_type=1&pd=1&photo=0&sort=1'
        News('KBS', source_url2, 10)  # todo 개수
        # 키워드 '토목'
        source_url3 = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&query=%ED%86%A0%EB%AA%A9&oquery=%EA%B1%B4%EC%B6%95&tqi=hElnRdprvTossMTchJRssssstG8-132324&nso=so%3Add%2Cp%3A1w&de=2022.04.27&ds=2022.04.20&mynews=1&news_office_checked=1056&office_section_code=2&office_type=1&pd=1&photo=0&sort=1'
        News('KBS', source_url3, 5)  # todo 개수

    if args.etnews:
        source_url = 'https://search.naver.com/search.naver?where=news&query=%EC%A0%84%EC%9E%90%EC%8B%A0%EB%AC%B8&sm=tab_opt&sort=1&photo=0&field=0&pd=1&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3A1w&is_sug_officeid=1'
        News('ETNews', source_url, 200)  # todo 개수





