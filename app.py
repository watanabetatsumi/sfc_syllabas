import requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import os
from dotenv import load_dotenv

result_data = []

# .env ファイルを読み込む
load_dotenv()
# 環境変数を取得する
login_name = os.getenv("LOGIN_NAME")
login_pass = os.getenv("LOGIN_PASS")

access_url = "https://syllabus.sfc.keio.ac.jp/users/sign_in?locale=ja&return_to=%2F"
#url = 'https://syllabus.sfc.keio.ac.jp/?locale=ja'
result_url = 'https://syllabus.sfc.keio.ac.jp/courses?locale=ja&search%5Byear%5D=2024&search%5Bsemester%5D=fall'
session = requests.Session()
login_info = {
    'user[cns_account]': login_name,
    'user[password]': login_pass
}

response = session.post(access_url,data=login_info)
if 'アカウントまたはパスワードが正しくありません。' in response.text:
    print('ログインに失敗しました。')
    # 何らかのエラーハンドリングを追加することができます
else:
    print('ログインに成功しました。')
#response = session.get(url)
for i in range(1,10):
    print("count :", i)
    params = {
        'page':i
    }
    html = session.get(result_url,params=params)
    soup = BeautifulSoup(html.content,"html.parser")
    chap2 = soup.find(attrs={'class':'result'})
    for elements in chap2.find_all("li"):
        element = elements.find("h2")
        if element is None:
            continue
        if "卒業" in element.text:
            continue
        elif "研究会" in element.text:
            continue
        elif "英語" in element.text:
            continue
        elif "ベーシック" in element.text:
            continue
        elif "インテンシブ" in element.text:
            continue
        elif "語スキル" in element.text:
            continue
        elif "体育" in element.text:
            continue
        elif "心身ウェルネス" in element.text:
            continue
        elif "情報基礎" in element.text:
            continue
        elif "GIGA" in element.text:
            continue
        teacher = elements.find("dt",string="授業教員名").find_next_sibling("dd").text
        detail = elements.find("a", class_="detail-btn")
        if detail is None:
            continue
        
        detail_url = urllib.parse.urljoin('https://syllabus.sfc.keio.ac.jp/courses',detail.get("href"))
        detail_html = session.get(detail_url)
        detail_soup = BeautifulSoup(detail_html.content,"html.parser")
        
        abstruct = detail_soup.find(attrs={'class':'subject'})
        where = abstruct.find("dt",string="学部・研究科").find_next_sibling("dd").text
        if "メディア" in where:
            continue
        field = abstruct.find("dt",string="分野").find_next_sibling("dd").text
        degree = abstruct.find("dt",string="単位").find_next_sibling("dd").text
        
        info = detail_soup.find(attrs={'class':'syllabus-info'})
        when = info.find("dt",string="曜日・時限").find_next_sibling("dd").text
        # basement = info.find("dt",string="履修条件").find_next_sibling("dd").text
        basement_element = info.find("dt",string="履修条件")
        if basement_element is not None:
            basement = basement_element.find_next_sibling("dd").text
        else:
            basement = "なし"
        style = info.find("dt",string="実施形態").find_next_sibling("dd").text
        # limit = info.find("dt",string="履修制限").find_next_sibling("dd").text
        limit_element = info.find("dt",string="履修制限")
        if limit_element is not None:
            limit = limit_element.find_next_sibling("dd").text
        if limit_element is None:
            limit = "なし"
        member = info.find("dt",string="受け入れ予定人数")
        if member is None:
            member = "未定"
        else:
            member = member.find_next_sibling("dd").text

        content = detail_soup.find(attrs={'class':'detail-info'})
        todo = content.find("dt",string="講義概要").find_next_sibling("dd").text
        # evaluation = content.find("dt",string="提出課題・試験・成績評価の方法など").find_next_sibling("dd").text
        evaluation_element = content.find("dt",string="提出課題・試験・成績評価の方法など")
        if evaluation_element is not None:
            evaluation = evaluation_element.find_next_sibling("dd").text
        else:
            evaluation = "未定"

        result_data.append([element.text, teacher, detail_url, when, basement, style, limit, member, todo, evaluation])

        # print(element.text)
        # print(teacher)
        # print(detail_url)
        # print(when)
        # print(basement)
        # print(style)
        # print(limit)
        # print(member)
        # print(todo)
        # print(evaluation)

df = pd.DataFrame(result_data, columns=["授業名", "授業教員名", "詳細リンク","時間","推奨科目","授業形態","履修制限","受け入れ予定人数" ,"講義概要","成績評価"])
df.to_excel("syllabus_output.xlsx", index=False)
