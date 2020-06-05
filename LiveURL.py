import requests
import re
import execjs
import time
import hashlib
import win32clipboard as w


def get_huya_url(room_id):
    try:
        room_url = 'https://m.huya.com/' + str(room_id)
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/75.0.3770.100 Mobile Safari/537.36 '
        }
        response = requests.get(url=room_url, headers=header).text
        liveLineUrl = re.findall(r'liveLineUrl = "([\s\S]*?)";', response)[0]
        if liveLineUrl:
            if 'replay' in liveLineUrl:
                return '直播录像：' + liveLineUrl
            else:
                real_url = "https:" + \
                    re.sub(r'_\d{4}.m3u8', '.m3u8', liveLineUrl)
        else:
            real_url = '未开播或直播间不存在'
    except:
        real_url = '未开播或直播间不存在'
    return real_url


def get_tt():
    tt1 = str(int(time.time()))
    tt2 = str(int((time.time() * 1000)))
    today = time.strftime('%Y%m%d', time.localtime())
    return tt1, tt2, today


def get_homejs(rid):
    room_url = 'https://m.douyu.com/' + rid
    response = requests.get(url=room_url)
    pattern_real_rid = r'"rid":(\d{1,7})'
    real_rid = re.findall(pattern_real_rid, response.text, re.I)[0]
    if real_rid != rid:
        room_url = 'https://m.douyu.com/' + real_rid
        response = requests.get(url=room_url)
    homejs = ''
    pattern = r'(function ub9.*)[\s\S](var.*)'
    result = re.findall(pattern, response.text, re.I)
    str1 = re.sub(r'eval.*;}', 'strc;}', result[0][0])
    homejs = str1 + result[0][1]
    return homejs, real_rid


def get_sign(rid, post_v, tt, ub9):
    docjs = execjs.compile(ub9)
    res2 = docjs.call('ub98484234')
    str3 = re.sub(r'\(function[\s\S]*toString\(\)', '\'', res2)
    md5rb = hashlib.md5((rid + '10000000000000000000000000001501' + tt + '2501' +
                         post_v).encode('utf-8')).hexdigest()
    str4 = 'function get_sign(){var rb=\'' + md5rb + str3
    str5 = re.sub(r'return rt;}[\s\S]*', 'return re;};', str4)
    str6 = re.sub(r'"v=.*&sign="\+', '', str5)
    docjs1 = execjs.compile(str6)
    sign = docjs1.call(
        'get_sign', rid, '10000000000000000000000000001501', tt)
    return sign


def mix_room(rid):
    result1 = 'PKing'
    return result1


def get_pre_url(rid, tt):
    request_url = 'https://playweb.douyucdn.cn/lapi/live/hlsH5Preview/' + rid
    post_data = {
        'rid': rid,
        'did': '10000000000000000000000000001501'
    }
    auth = hashlib.md5((rid + str(tt)).encode('utf-8')).hexdigest()
    header = {
        'content-type': 'application/x-www-form-urlencoded',
        'rid': rid,
        'time': tt,
        'auth': auth
    }
    response = requests.post(url=request_url, headers=header, data=post_data)
    response = response.json()
    pre_url = ''
    if response.get('error') == 0:
        real_url = (response.get('data')).get('rtmp_live')
        if 'mix=1' in real_url:
            pre_url = mix_room(rid)
        else:
            pattern1 = r'^[0-9a-zA-Z]*'
            pre_url = re.search(pattern1, real_url, re.I).group()
    return pre_url


def get_sign_url(post_v, rid, tt, ub9):
    sign = get_sign(rid, post_v, tt, ub9)
    request_url = 'https://m.douyu.com/api/room/ratestream'
    post_data = {
        'v': '2501' + post_v,
        'did': '10000000000000000000000000001501',
        'tt': tt,
        'sign': sign,
        'ver': '219032101',
        'rid': rid,
        'rate': '-1'
    }
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Mobile Safari/537.36'
    }
    response = requests.post(
        url=request_url, headers=header, data=post_data).json()
    if response.get('code') == 0:
        real_url = (response.get('data')).get('url')
        if 'mix=1' in real_url:
            result1 = mix_room(rid)
        else:
            pattern1 = r'live/(\d{1,8}[0-9a-zA-Z]+)_?[\d]{0,4}/playlist'
            result1 = re.findall(pattern1, real_url, re.I)[0]
    else:
        result1 = 0
    return result1


def get_douyu_url(rid):
    rid = str(rid)
    tt = get_tt()
    url = get_pre_url(rid, tt[1])
    if url:
        return "http://tx2play1.douyucdn.cn/live/" + url + ".flv?uuid="
    else:
        result = get_homejs(rid)
        real_rid = result[1]
        homejs = result[0]
        real_url = get_sign_url(tt[2], real_rid, tt[0], homejs)
        if real_url != 0:
            real_url = "http://tx2play1.douyucdn.cn/live/" + real_url + ".flv"
        else:
            real_url = '未开播'
        return real_url


def get_real_rid(rid):
    room_url = 'https://api.live.bilibili.com/room/v1/Room/room_init?id=' + \
        str(rid)
    response = requests.get(url=room_url).json()
    data = response.get('data', 0)
    if data:
        live_status = data.get('live_status', 0)
        room_id = data.get('room_id', 0)
    else:
        live_status = room_id = 0
    return live_status, room_id


def get_bilibili_url(rid):
    room = get_real_rid(rid)
    live_status = room[0]
    room_id = room[1]
    if live_status:
        try:
            room_url = 'https://api.live.bilibili.com/xlive/web-room/v1/index/getRoomPlayInfo?room_id={}&play_url=1&mask=1&qn=0&platform=web'.format(
                room_id)
            response = requests.get(url=room_url).json()
            durl = response.get('data').get('play_url').get('durl', 0)
            real_url = durl[-1].get('url')
        except:
            real_url = '疑似部分国外IP无法GET到正确数据，待验证'
    else:
        real_url = '未开播或直播间不存在'
    return real_url


def get_egame_url(rid):
    room_url = 'https://share.egame.qq.com/cgi-bin/pgg_async_fcgi'
    post_data = {
        'param': '''{"0":{"module":"pgg_live_read_svr","method":"get_live_and_profile_info","param":{"anchor_id":''' + str(rid) + ''',"layout_id":"hot","index":1,"other_uid":0}}}'''
    }
    try:
        response = requests.post(url=room_url, data=post_data).json()
        data = response.get('data', 0)
        if data:
            video_info = data.get('0').get(
                'retBody').get('data').get('video_info')
            pid = video_info.get('pid', 0)
            if pid:
                is_live = data.get('0').get(
                    'retBody').get('data').get('profile_info').get('is_live', 0)
                if is_live:
                    play_url = video_info.get('stream_infos')[
                        0].get('play_url')
                    real_url = re.findall(r'([\w\W]+?)&uid=', play_url)[0]
                else:
                    real_url = '直播间未开播'
            else:
                real_url = '直播间未启用'
        else:
            real_url = '直播间不存在'
    except:
        real_url = '数据请求错误'
    return real_url

platform = input("选择平台:\nHY:虎牙\tBL:哔哩哔哩\nDY:斗鱼\tQQ:企鹅电竞\n")
live_url = "平台不存在！"
if platform.upper() == "HY":
    rid = input("输入房间号:\n")
    live_url = get_huya_url(rid)
if platform.upper() == "DY":
    rid = input("输入房间号:\n")
    live_url = get_douyu_url(rid)
if platform.upper() == "BL":
    rid = input("输入房间号:\n")
    live_url = get_bilibili_url(rid)
if platform.upper() == "QQ":
    rid = input("输入房间号:\n")
    live_url = get_egame_url(rid)
print(live_url)
# 写入剪切板
w.OpenClipboard()
w.EmptyClipboard()
w.SetClipboardText(live_url)
w.CloseClipboard()
time.sleep(3)
