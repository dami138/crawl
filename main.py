
from crawl.external import *
from crawl.internal import *
from crawl.general import *
from utils.similarity import keywordExAndSave



print("\n\n----교외 게시물 가져오기----")

# python main.py -D -J -T -A -K -E -M

def dropDB():
    # db 비우기
    client = MongoClient("mongodb://localhost:27017")
    db = client.crawl
    db['external'].drop()

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

args = parser.parse_args()

if args.dropDB:
    dropDB()


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
    News('KBS', source_url, 20)

    #키워드 '건축'
    source_url2 = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&query=%EA%B1%B4%EC%B6%95&tqi=hElnLlprvTossMt%2BLpRssssstRG-468912&nso=so%3Add%2Cp%3A1w&de=2022.04.27&ds=2022.04.20&mynews=1&news_office_checked=1056&office_section_code=2&office_type=1&pd=1&photo=0&sort=1'
    News('KBS', source_url2, 10)
    #키워드 '토목'
    source_url3 = 'https://search.naver.com/search.naver?sm=tab_hty.top&where=news&query=%ED%86%A0%EB%AA%A9&oquery=%EA%B1%B4%EC%B6%95&tqi=hElnRdprvTossMTchJRssssstG8-132324&nso=so%3Add%2Cp%3A1w&de=2022.04.27&ds=2022.04.20&mynews=1&news_office_checked=1056&office_section_code=2&office_type=1&pd=1&photo=0&sort=1'
    News('KBS', source_url3, 5)

if args.etnews:
    source_url = 'https://search.naver.com/search.naver?where=news&query=%EC%A0%84%EC%9E%90%EC%8B%A0%EB%AC%B8&sm=tab_opt&sort=1&photo=0&field=0&pd=1&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3A1w&is_sug_officeid=1'
    News('ETNews', source_url, 200)

print("\n\n----교내 게시물 가져오기----")
internal_f()

print("\n\n----general 테이블 갱신----")
uploadGeneraltoDB()

print("\n\n----document Keyword Extract ----")
keywordExAndSave()
