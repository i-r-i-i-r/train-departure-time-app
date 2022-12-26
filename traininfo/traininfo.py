import requests
import datetime as dt


_API_KEY = "xxxxxx" # API keyをここに記載してください




# 駅名(ある程度不正確でもよい)からの、正確な駅名と駅コードを取得
def _get_stationCode(name):
    url = "http://api.ekispert.jp/v1/json/station"
    querystring = {"name":name,
                   "key": _API_KEY}
    
    response = requests.request("GET", url, params=querystring)
    points = response.json()["ResultSet"]["Point"]
    if type(points) is list:
        code = [p["Station"]["code"] for p in points]
        name = [p["Station"]["Name"] for p in points]
    else:
        code = [points["Station"]["code"]]
        name = [points["Station"]["Name"]]
    return dict(zip(name,code))


# 駅コードから行先候補の名称とコードを取得
def _get_directionCode(stationCode, today):
    querystring = {"stationCode":stationCode,
                   "date":today,
                   "key": _API_KEY}
    
    url = "http://api.ekispert.jp/v1/json/operationLine/timetable"
    response = requests.request("GET", url, params=querystring)
    timetables = response.json()['ResultSet']['TimeTable']
    if type(timetables) is list:
        d = [t['Line']['Direction'] for t in timetables]
        c = [t['code']              for t in timetables]
    else:
        d = [timetables['Line']['Direction']]
        c = [timetables['code']]
    
    return dict(zip(d,c))


# 指定した駅、行先、日付における時刻表と列車種類を取得
def _get_timetable(station_code, direction_code, date_):
    querystring = {"stationCode":station_code,
                   "code":direction_code,
                   "date":date_,
                   "key": _API_KEY}
    
    url = "http://api.ekispert.jp/v1/json/operationLine/timetable"
    response  = requests.request("GET", url, params=querystring)
    timetable = response.json()['ResultSet']['TimeTable']
    linekind = timetable['LineKind']
    if type(linekind)is list:
        l_text = [l["text"] for l in linekind]
        l_code = [l["code"] for l in linekind]
    else:
        l_text = [linekind["text"]]
        l_code = [linekind["code"]]
    return (timetable['HourTable'], dict(zip(l_code,l_text)))


# m0分より後の電車の時刻を時刻表から求める
def _get_minutes_after_m0(timetable_hour, m0, hour, linekind):
    time_disp=[]
    #date_disp = date[:2]+"/"+date[4:6]+"/"date[7:]+" "
    if type(timetable_hour) is list:
        minutes = [int(t['Minute']) for t in timetable_hour]
        train_kind = [linekind[t['Stop']['kindCode']] for t in timetable_hour]
    else:
        minutes = [int(timetable_hour['Minute'])]
        train_kind = [linekind[timetable_hour['Stop']['kindCode']]]
    for i in range(len(minutes)):
        if minutes[i]>m0:
            #datetime_disp += [[date+str(hour).zfill(2)+":"+str(minutes[i]).zfill(2), train_kind[i]]]
            time_disp += [str(hour).zfill(2)+":"+str(minutes[i]).zfill(2) + "   " + train_kind[i]]
    return time_disp


# 表示すべき発車時刻の特定
def _detect_datetime_disp(date_now, hour_now, minute_now, station_code, direction_code, n_disp):
    date1      = date_now
    hour1      = hour_now
    minute1    = minute_now
    timetable1, linekind = _get_timetable(station_code, direction_code, date1)
    hours      = [int(t['Hour']) for t in timetable1]
    datetime_disp = []
    
    for i in range(20): # 20は適当
        bool1 = [hour1==h for h in hours]
        bool2 = [hour1< h for h in hours]
        if sum(bool1) and i==0:
            date2       = date1
            index_hour2 = bool1.index(True)
            minute2     = minute1
        elif sum(bool2)>0:
            date2       = date1
            index_hour2 = bool2.index(True)
            minute2     = -1
        else:
            date2       = (dt.datetime.today()+dt.timedelta(days=1)).strftime("%Y%m%d")
            timetable1,_= _get_timetable(station_code, direction_code, date1)
            hours       = [int(t['Hour']) for t in timetable1]
            index_hour2 = 0
            minute2     = -1
        
        timetable2 = timetable1[index_hour2]['MinuteTable']
        hour2 = hours[index_hour2]
        datetime_disp += _get_minutes_after_m0(timetable2, minute2, hour2, linekind)
        
        if len(datetime_disp)<n_disp:
            hour1 = hour2
            date1 = date2
        else:
            return datetime_disp[:n_disp]

def make_station_property(station_names):
    station_codes = {}
    for n in station_names:
        station_codes.update(_get_stationCode(n))
    
    station_names = list(station_codes)# 正確な駅名リストに更新する
    directions    = [_get_directionCode(c, dt.datetime.today().strftime("%Y%m%d")) for c in list(station_codes.values())]
    
    station_property = dict(zip(
                                   station_names,
                                   [
                                       dict(zip(
                                           ["code", "direction"],
                                           [list(station_codes.values())[i], directions[i]])) 
                                       for i in range(len(station_names))
                                   ]
                               ))
    
    return station_property

def make_disp_text(station_name, direction_name, station_property, n_disp):
    station_code   = station_property[station_name]["code"]
    direction_code = station_property[station_name]['direction'][direction_name]
    
    # 現在の日付と時刻を取得
    now = dt.datetime.today()
    date_now   = now.strftime("%Y%m%d") # str
    hour_now   = int(now.strftime("%H"))
    minute_now = int(now.strftime("%M"))
    
    # 深夜0~2時の場合は前日の24~26時として検索
    if hour_now<3:
        hour_now += 24
        date_now = (now-dt.timedelta(days=1)).strftime("%Y%m%d")
    
    # 表示すべき発車時刻の特定
    disp_text_list = _detect_datetime_disp(date_now, hour_now, minute_now, station_code, direction_code, n_disp)
    
    return disp_text_list



