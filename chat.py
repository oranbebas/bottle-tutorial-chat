# coding: utf-8

import json
import csv
import os
from datetime import datetime
from bottle import route, run, template, request, response, redirect

@route('/')
def index():
    return template('index')

@route('/enter', method=["POST"])
def enter():
    """
    入室処理を行う。
    フォームの情報をCookieに格納し、チャット時の名前として使用。
    """
    # POSTデータの確認
    username = request.POST.username
    print("POST username is ", username)

    # Cookieへの格納
    response.set_cookie('username', username)

    return redirect('/chat_room')

@route('/chat_room')
def chat_room():
    """
    チャットを行う画面
    """
    # Cookieからの取得はrequestから行う
    username = request.get_cookie('username')

    # Cookieにユーザー情報がない場合は入室画面へ戻す
    if not username:
        return redirect('/')

    # チャットデータの取得
    talk_list = get_talk()

    return template('chat_room', username=username, talk_list=talk_list)

@route('/talk', method=["POST"])
def talk():
    """
    発言を登録し、チャットルームへリダイレクト
    """
    chat_data = request.POST.getunicode('chat')
    username = request.get_cookie('username')
    talk_time = datetime.now()
    save_talk(talk_time, username, chat_data)

    return redirect('/chat_room')

@route('/api/talk', method=['GET', 'POST'])
def talk_api():
    """
    発言一覧を管理するAPI
    """
    if request.method == 'GET':
        talk_list = get_talk()
        return json.dumps(talk_list)
    elif request.method == 'POST':
        chat_data = request.POST.chat
        username = request.get_cookie('username')
        talk_time = datetime.now()

        save_talk(talk_time, username, chat_data)

        return json.dumps({
            "status": "success"
        })

@route('/api/last_talk')
def get_last_talk():
    """
    最終発言だけを戻すAPI
    """
    talk_list = get_talk()
    return json.dumps(talk_list[-1])


def save_talk(talk_time, username, chat_data):
    """
    チャットデータを永続化する関数
    CSVとしてチャットの内容を書き込む
    """
    with open('./chat_data.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow([talk_time, username, chat_data])

def get_talk():
    """
    永続化されたチャットデータを取得する関数
    CSVからリスト形式でデータを取得
    """
    talk_list = []

    # 履歴ファイル婦がない場合は空ファイルを作成する
    if not os.path.exists('./chat_data.csv'):
        open('./chat_data.csv', 'w').close()

    with open('./chat_data.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            talk_list.append({
                'talk_time': row[0],
                'username': row[1],
                'chat_data': row[2],
            })
    return talk_list

run(host='localhost', port=8080, debug=True, reloader=True)
