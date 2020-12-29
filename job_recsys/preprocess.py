# This includes CVParser and SkillExtractor
# Input: CV+Profile or JD
# Output: a json {skills, exp_year, location, job_lv,}

import json
import copy
import pandas as pd
import unicodedata as ud
import numpy as np
import pickle
from gensim.parsing.preprocessing import *
import re
import ast
import os
from pyvi import ViTokenizer
import requests
import pprint
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fuzzywuzzy import fuzz

CV_PARSER_API = 'http://127.0.0.1:60000/parser'
SKILL_EXTRACTOR_API = 'http://127.0.0.1:5000/skill'
FUZZY_THRESHOLD = 90
CV_DIR_PATH = 'job_recsys/data/cvs'
PROFILE_JSON_PATH = 'job_recsys/data/profiles/profiles.json'
JD_EXCEL_PATH = 'job_recsys/data/jds/vi_jd_6k.xlsx'

job_lv_to_id = {
    # All web
    'Nhân viên':2, 
    'Quản lý':4, 
    'Trưởng nhóm / Giám sát':3,
    'Sinh viên/ Thực tập sinh':1,
    'Giám đốc':5,
    'Mới tốt nghiệp':1,
    'Phó Giám đốc':5,
    'Cao đẳng':1,
    'Đại học':1,
    'Trung cấp':0,
    'Không yêu cầu':0,
    'Trung học':0,
    'Cử nhân':1,
    'PTCS':0,
    'Kỹ sư':2,
    'Chứng chỉ':1,
    'Thạc sĩ':2,
    'Khác':2,
    'Trên đại học':1,
    'Mới tốt nghiệp / Thực tập sinh':1,
    'Trưởng phòng':4,
    'Trưởng nhóm':3,
    # vietnameworks
    'Mới tốt nghiệp/Thực tập sinh':1,
    # 'Nhân viên':2,
    'Trưởng nhóm/Giám sát':3,
    # 'Trưởng phòng':4,
    # 'Giám đốc':5,
    # More
    'Sinh viên':1,
    'Thực tập':1,
}

month_to_num = {
    'jan':'1',
    'january':'1',
    'february':'2',
    'feb':'2',
    'march':'3',
    'mar':'3',
    'april':'4',
    'apr':'4',
    'may':'5',
    'june':'6',
    'jun':'6',
    'july':'7',
    'jul':'7',
    'august':'8',
    'aug':'8',
    'september':'9',
    'sep':'9',
    'october':'10',
    'oct':'10',
    'november':'11',
    'nov':'11',
    'december':'12',
    'dec':'12'
}

vi_locations = [
    'An Giang',
    'Bà Rịa - Vũng Tàu',
    'Bắc Giang',
    'Bắc Kạn',
    'Bạc Liêu',
    'Bắc Ninh',
    'Bến Tre',
    'Bình Định',
    'Bình Dương',
    'Bình Phước',
    'Bình Thuận',
    'Cà Mau',
    'Cao Bằng',
    'Đắk Lắk',
    'Đắk Nông',
    'Điện Biên',
    'Đồng Nai',
    'Đồng Tháp',
    'Gia Lai',
    'Hà Giang',
    'Hà Nam',
    'Hà Tĩnh',
    'Hải Dương',
    'Hậu Giang',
    'Hòa Bình',
    'Hưng Yên',
    'Khánh Hòa',
    'Kiên Giang',
    'Kon Tum',
    'Lai Châu',
    'Lâm Đồng',
    'Lạng Sơn',
    'Lào Cai',
    'Long An',
    'Nam Định',
    'Nghệ An',
    'Ninh Bình',
    'Ninh Thuận',
    'Phú Thọ',
    'Quảng Bình',
    'Quảng Nam',
    'Quảng Ngãi',
    'Quảng Ninh',
    'Quảng Trị',
    'Sóc Trăng',
    'Sơn La',
    'Tây Ninh',
    'Thái Bình',
    'Thái Nguyên',
    'Thanh Hóa',
    'Thừa Thiên Huế',
    'Tiền Giang',
    'Trà Vinh',
    'Tuyên Quang',
    'Vĩnh Long',
    'Vĩnh Phúc',
    'Yên Bái',
    'Phú Yên',
    'Cần Thơ',
    'Đà Nẵng',
    'Hải Phòng',
    'Hà Nội',
    'TP HCM',
    'Thành phố Hồ Chí Minh',
    'Hồ Chí Minh'
]

def no_accent_vietnamese(s):
    s = re.sub('[áàảãạăắằẳẵặâấầẩẫậ]', 'a', s)
    s = re.sub('[ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]', 'A', s)
    s = re.sub('[éèẻẽẹêếềểễệ]', 'e', s)
    s = re.sub('[ÉÈẺẼẸÊẾỀỂỄỆ]', 'E', s)
    s = re.sub('[óòỏõọôốồổỗộơớờởỡợ]', 'o', s)
    s = re.sub('[ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ]', 'O', s)
    s = re.sub('[íìỉĩị]', 'i', s)
    s = re.sub('[ÍÌỈĨỊ]', 'I', s)
    s = re.sub('[úùủũụưứừửữự]', 'u', s)
    s = re.sub('[ÚÙỦŨỤƯỨỪỬỮỰ]', 'U', s)
    s = re.sub('[ýỳỷỹỵ]', 'y', s)
    s = re.sub('[ÝỲỶỸỴ]', 'Y', s)
    s = re.sub('đ', 'd', s)
    s = re.sub('Đ', 'D', s)
    return s

no_accent_locations = [no_accent_vietnamese(x) for x in vi_locations]

def fuzzy_search(substr_list, str):
    max_ratio = 0
    max_sub_str = ''
    for substr in substr_list:
        ratio = fuzz.partial_ratio(substr.lower(), str.lower())
        if ratio > max_ratio:
            max_ratio = ratio
            max_sub_str = substr
    if max_ratio > FUZZY_THRESHOLD:
        return max_sub_str
    return ''

def build_path_dict(dir):
    id_path_dict = {}
    for path, subdirs, files in os.walk(dir):
        for name in files:
            id_path_dict[name.split('_')[0]] = os.path.join(path, name)
    return id_path_dict

def extract_skill_from_text(text):
    skills = set()
    texts = text.replace('_',' ').splitlines()
    for text in texts:
        if len(text) > 3:
            try:
                payload = {"text":text,"raw": True}
                extracted_skills = requests.post(url=SKILL_EXTRACTOR_API, json=payload).json()['data']
                skills = skills.union(set([s.lower() for s in extracted_skills]))
            except:
                print('skill parser error: ', text)
    return skills

def process_a_cv(a_cv):
    # a_cv is a file
    response = requests.post(url=CV_PARSER_API, files={'file': a_cv})
    try:
        a_cv_json = json.loads(response.text)
    except:
        print('Error a_cv_json = ', a_cv_json)
        return None
    if len(a_cv_json) == 0:
        print('len a_cv_json = 0')
        return None

    # print('cv ok')
    exp_year = 0
    max_exp_year = 0
    job_lv_id = 0
    location = ''

    for box in a_cv_json[0]['boxes']:
        # print('box = ', box)
        year_diff = 0
        if box['type'] == 'company_time':
            # '15 / 8 / 2018 - 30 / 2 / 2019'
            date_str = box['text'].lower()
            for month_name, month_number in month_to_num.items():
                date_str = date_str.replace(month_name, ' {} '.format(month_number))
            # if '-' in date_str or '–' in date_str:
            time_list =  re.findall(r'\d+', date_str)
            # print(time_list)
            if len(time_list) == 1: 
                # year
                if len(time_list[0]) == 4:
                    max_year_diff = datetime.now().year - int(time_list[0])
                    max_exp_year = max(max_exp_year, max_year_diff)
                else:
                    # Exception
                    print(time_list)
            elif len(time_list) == 2: 
                # year - year or month/year or year/month
                if len(time_list[0]) == 4 and len(time_list[1]) == 4:
                    year_diff = int(time_list[1]) - int(time_list[0])
                elif len(time_list[0]) == 4 or len(time_list[1]) == 4:
                    if len(time_list[0]) != 4:
                        month = int(time_list[0])
                        year = int(time_list[1])
                    else:
                        month = int(time_list[1])
                        year = int(time_list[0])
                    try:
                        start_time = datetime(year, month, 1)
                    except ValueError:
                        start_time = datetime(year, 1, 1)
                    today = datetime.now()
                    max_year_diff = relativedelta(today, start_time).months / 12
                    max_exp_year = max(max_exp_year, max_year_diff)
                else:
                    # Exception
                    print(time_list)
            elif len(time_list) == 3:
                if len(time_list[2]) == 4:
                    try:
                        start_time = datetime(int(time_list[2]), int(time_list[1]), int(time_list[0]))
                    except ValueError:
                        try:
                            start_time = datetime(int(time_list[2]), int(time_list[0]), int(time_list[1]))
                        except ValueError:
                            start_time = datetime(int(time_list[2]), 1, 1)
                    max_year_diff = relativedelta(datetime.now(), start_time).months / 12
                    max_exp_year = max(max_exp_year, max_year_diff)
                else:
                    # Exception
                    print(time_list)
            elif len(time_list) == 4: 
                # month/year - month/year or year/month - year/month
                if len(time_list[0]) == 4 and len(time_list[2]) == 4:
                    try:
                        start_time = datetime(int(time_list[0]), int(time_list[1]), 1)
                        end_time = datetime(int(time_list[2]), int(time_list[3]), 1)
                    except ValueError:
                        start_time = datetime(int(time_list[0]), 1, 1)
                        end_time = datetime(int(time_list[2]), 1, 1)
                    year_diff = relativedelta(end_time, start_time).months / 12
                elif len(time_list[1]) == 4 and len(time_list[3]) == 4:
                    try:
                        start_time = datetime(int(time_list[1]), int(time_list[0]), 1)
                        end_time = datetime(int(time_list[3]), int(time_list[2]), 1)
                    except ValueError:
                        start_time = datetime(int(time_list[1]), 1, 1)
                        end_time = datetime(int(time_list[3]), 1, 1)
                    year_diff = relativedelta(end_time, start_time).months / 12
                else:
                    # Exception
                    print(time_list)
            elif len(time_list) == 6:
                # date/month/year - date/month/year
                # month/date/year - month/date/year
                if len(time_list[2]) == 4 and len(time_list[5]) == 4:
                    try:
                        start_time = datetime(int(time_list[2]),int(time_list[1]),int(time_list[0]))
                        end_time = datetime(int(time_list[5]),int(time_list[4]),int(time_list[3]))
                    except ValueError:
                        start_time = datetime(int(time_list[2]),1,1)
                        end_time = datetime(int(time_list[5]),1,1)
                    year_diff = relativedelta(end_time, start_time).months / 12
                else:
                    # Exception
                    print(time_list)
            else:
                # Exception
                print(time_list)
            exp_year += year_diff
        elif box['type'] == 'position':
            position = fuzzy_search(list(job_lv_to_id.keys()), box['text'].replace('_', ' '))
            if position != '':
                job_lv_id = job_lv_to_id[position]
        elif box['type'] == 'address':
            location = fuzzy_search(vi_locations, box['text'].replace('_', ' ').strip())
            location = no_accent_vietnamese(location).lower()

    exp_list = a_cv_json[-1]['exp']
    exp = ''
    for e in exp_list:
        if any(c.isalpha() for c in e):
            exp += ' ' + e

    # Exp - already tokenized
    exp = exp.strip().lower()
    # print('exp = ', exp)

    # Skills
    skills = extract_skill_from_text(exp)
    # print('skill ok')

    # Exp year
    if exp_year == 0 or max_exp_year == 0:
        exp_year = exp_year + max_exp_year

    # Location
    if location == '':
        location = []
    else:
        if location == 'tp hcm' or location == 'thanh pho ho chi minh':
            location = 'ho chi minh'
        location = [location]

    return {'skills':skills, 'exp_year':exp_year, 'location':location, 'job_lv_id':job_lv_id, 'exp':exp}
     
def process_a_profile(a_profile):
    # a_profile is a dict 
    # Skills
    skills = a_profile['skill_set']
    # print('skills = ', skills)
    # print('skills type = ', type(skills))
    if skills == None:
        skills = []
    skills = set([ViTokenizer.tokenize(s.lower()) for s in skills])

    # Exp year
    exp_year = a_profile['year_of_exp']
    if exp_year == None:
        exp_year = 0

    # job_lv_id
    job_lv = a_profile['expected_job_level_name_vi']
    if job_lv == None:
        job_lv_id = 0
    else:
        job_lv_id = job_lv_to_id[job_lv]

    # location
    locations = a_profile['city_names_vi']
    if locations == None:
        locations = []
    new_locations = []
    for l in locations:
        loc = fuzzy_search(no_accent_locations, no_accent_vietnamese(l).strip()).lower()
        if loc == 'tp hcm' or loc == 'thanh pho ho chi minh':
            loc = 'ho chi minh'
        new_locations.append(loc)

    return {'skills':skills, 'exp_year':exp_year, 'job_lv_id':job_lv_id, 'location':new_locations}

def process_a_jd(a_jd):
    # a_jd is a dict 
    # job description
    skills_extracted_from_des = set()
    try:
        job_description = a_jd['job_descriptions'].lower().replace('_x000d_', '\n').strip()
        skills_extracted_from_des = extract_skill_from_text(job_description)
        job_description = ViTokenizer.tokenize(job_description)
    except:
        job_description = ''

    # job requirement
    skills_extracted_from_req = set()
    try:
        job_requirement = a_jd['job_requirements'].lower().replace('_x000d_', '\n').strip()
        skills_extracted_from_req = extract_skill_from_text(job_requirement)
    except:
        job_requirement = ''

    # Skills
    skills = set()
    for i in range(5):
        skill = a_jd['skills/{}'.format(i)]
        # print(skill)
        if not pd.isna(skill):
            skills.add(ViTokenizer.tokenize(skill.lower()))
    skills = skills.union(skills_extracted_from_des).union(skills_extracted_from_req)

    # Exp year
    exp_years = re.findall(r'\d+', str(a_jd['job_experience_years']))
    if not exp_years:
        exp_year = 0
    else:
        exp_year = int(exp_years[0])

    # job_lv_id
    job_lv = a_jd['job_level']
    if pd.isna(job_lv):
        job_lv_id = 0
    else:
        job_lv_id = job_lv_to_id[job_lv]
    # location
    try:
        locations = ast.literal_eval(a_jd['working_location'])
    except:
        locations = a_jd['working_location'].splitlines()

    # locations = [fuzzy_search(no_accent_locations, no_accent_vietnamese(l).strip()).lower() for l in locations]
    new_locations = []
    for l in locations:
        loc = fuzzy_search(no_accent_locations, no_accent_vietnamese(l).strip()).lower()
        if loc == 'tp hcm' or loc == 'thanh pho ho chi minh':
            loc = 'ho chi minh'
        new_locations.append(loc)
    
    return {'skills':skills, 'exp_year':exp_year, 'job_lv_id':job_lv_id, 'location':new_locations, 'job_des':job_description}

def combine_cv_profile(a_cv, a_profile, min_exp_year=0, max_exp_year=10):
    # Skills
    skills = a_cv['skills'].union(a_profile['skills'])

    # Exp years
    exp_year = 0
    cv_year = a_cv['exp_year']
    profile_year = a_profile['exp_year']
    if cv_year < min_exp_year:
        cv_year = min_exp_year
    if cv_year > max_exp_year:
        cv_year = max_exp_year
    if profile_year < min_exp_year:
        profile_year = min_exp_year
    if profile_year > max_exp_year:
        profile_year = max_exp_year

    if cv_year == 0 or profile_year == 0:
        exp_year = cv_year + profile_year
    elif profile_year > cv_year:
        exp_year = cv_year
    elif profile_year <= cv_year:
        exp_year = profile_year

    # Job lv id
    job_lv_id = 0
    # print('cv: ', a_cv['job_lv_id'])
    # print('a_profile: ', a_profile['job_lv_id'])
    if a_cv['job_lv_id'] == 0 or a_profile['job_lv_id'] == 0:
        job_lv_id = a_cv['job_lv_id'] + a_profile['job_lv_id']
    # Becareful if profile lv > cv lv
    elif a_cv['job_lv_id'] > a_profile['job_lv_id']:
        job_lv_id = a_cv['job_lv_id']
    else:
        job_lv_id = a_profile['job_lv_id']

    # Location
    if a_cv['location'] == '':
        locations = a_profile['location']
    else:
        # print('cv: ', a_cv['location'])
        # print('pf: ', a_profile['location'])
        locations = list(set(a_cv['location'] + a_profile['location']))

    # Exp
    exp = a_cv['exp']
    return {'skills':skills, 'exp_year':exp_year, 'job_lv_id':job_lv_id, 'location':locations, 'exp':exp}

if __name__ == "__main__":
    # CV Processing
    # id_path_dict = build_path_dict('job_recsys\data\cvs')
    # cv_dict = {}
    # c = 0
    # for id, path in id_path_dict.items():
    #     print(c, path)
    #     with open(path, 'rb') as a_cv:
    #         cv_dict[id] = process_a_cv(a_cv)
    #     c += 1
    #     # pprint.pprint(cv_dict[id])

    # with open('job_recsys/pickle/cv_dict.pkl', 'wb') as f:
    #     pickle.dump(cv_dict, f)

    # with open(r'job_recsys\data\cvs\pack0\2508017_Tran_Anh_Hai.pdf', 'rb') as a_cv:
    #     data = process_a_cv(a_cv)
    # pprint.pprint(data)

    # Profile Processing
    # profile_dict = {}
    # with open(PROFILE_JSON_PATH, 'r') as f:
    #     raw_profiles = json.load(f)
    # # pprint.pprint(raw_profiles['9001654'])
    # for id, a_profile in raw_profiles.items():
    #     profile_dict[id] = process_a_profile(a_profile)
    # # print(profile_dict.keys())
    # # pprint.pprint(profile_dict['9001654'])
    # with open(r'job_recsys/pickle/profile_dict.pkl', 'wb') as f:
    #     pickle.dump(profile_dict, f)

    # JD Processing
    jd_dict = {}
    raw_jds = pd.read_excel(JD_EXCEL_PATH, sheet_name='Sheet1', engine='openpyxl').to_dict('index')
    for a_jd in raw_jds.values():
        print(a_jd['_id/0'])
        jd_dict[a_jd['_id/0']] = process_a_jd(a_jd)
    # print(jd_dict.keys())
    # pprint.pprint(jd_dict['5f5fb85c59eedecb4fc1b403'])
    with open(r'job_recsys/pickle/jd_dict.pkl', 'wb') as f:
        pickle.dump(jd_dict, f)

    # Emb_info Processing
    # Emb_info = CV + Profile
    # with open(r'job_recsys/pickle/cv_dict.pkl', 'rb') as f:
    #     cv_dict = pickle.load(f)
    # # print(len(cv_dict))
    # with open(r'job_recsys/pickle/profile_dict.pkl', 'rb') as f:
    #     profile_dict = pickle.load(f)
    # # print(len(profile_dict))

    # emp_info_dict = {}
    # for id in cv_dict.keys():
    #     if cv_dict[id] == None or id not in profile_dict:
    #         continue
    #     emp_info_dict[id] = combine_cv_profile(cv_dict[id], profile_dict[id])
    # with open(r'job_recsys/pickle/emp_info_dict.pkl', 'wb') as f:
    #     pickle.dump(emp_info_dict, f)

    # with open(r'job_recsys/pickle/emp_info_dict.pkl', 'rb') as f:
    #     emp_info_dict = pickle.load(f)
    # pprint.pprint(emp_info_dict)