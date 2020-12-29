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

SKILL_EXTRACTOR_API = 'http://127.0.0.1:5000/skill'

# locations = [
#     'An Giang',
#     'Bà Rịa - Vũng Tàu',
#     'Bắc Giang',
#     'Bắc Kạn',
#     'Bạc Liêu',
#     'Bắc Ninh',
#     'Bến Tre',
#     'Bình Định',
#     'Bình Dương',
#     'Bình Phước',
#     'Bình Thuận',
#     'Cà Mau',
#     'Cao Bằng',
#     'Đắk Lắk',
#     'Đắk Nông',
#     'Điện Biên',
#     'Đồng Nai',
#     'Đồng Tháp',
#     'Gia Lai',
#     'Hà Giang',
#     'Hà Nam',
#     'Hà Tĩnh',
#     'Hải Dương',
#     'Hậu Giang',
#     'Hòa Bình',
#     'Hưng Yên',
#     'Khánh Hòa',
#     'Kiên Giang',
#     'Kon Tum',
#     'Lai Châu',
#     'Lâm Đồng',
#     'Lạng Sơn',
#     'Lào Cai',
#     'Long An',
#     'Nam Định',
#     'Nghệ An',
#     'Ninh Bình',
#     'Ninh Thuận',
#     'Phú Thọ',
#     'Quảng Bình',
#     'Quảng Nam',
#     'Quảng Ngãi',
#     'Quảng Ninh',
#     'Quảng Trị',
#     'Sóc Trăng',
#     'Sơn La',
#     'Tây Ninh',
#     'Thái Bình',
#     'Thái Nguyên',
#     'Thanh Hóa',
#     'Thừa Thiên Huế',
#     'Tiền Giang',
#     'Trà Vinh',
#     'Tuyên Quang',
#     'Vĩnh Long',
#     'Vĩnh Phúc',
#     'Yên Bái',
#     'Phú Yên',
#     'Cần Thơ',
#     'Đà Nẵng',
#     'Hải Phòng',
#     'Hà Nội',
#     # 'TP HCM',
#     # 'Thành phố Hồ Chí Minh',
#     'Hồ Chí Minh'
# ]

# def no_accent_vietnamese(s):
#     s = re.sub('[áàảãạăắằẳẵặâấầẩẫậ]', 'a', s)
#     s = re.sub('[ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ]', 'A', s)
#     s = re.sub('[éèẻẽẹêếềểễệ]', 'e', s)
#     s = re.sub('[ÉÈẺẼẸÊẾỀỂỄỆ]', 'E', s)
#     s = re.sub('[óòỏõọôốồổỗộơớờởỡợ]', 'o', s)
#     s = re.sub('[ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ]', 'O', s)
#     s = re.sub('[íìỉĩị]', 'i', s)
#     s = re.sub('[ÍÌỈĨỊ]', 'I', s)
#     s = re.sub('[úùủũụưứừửữự]', 'u', s)
#     s = re.sub('[ÚÙỦŨỤƯỨỪỬỮỰ]', 'U', s)
#     s = re.sub('[ýỳỷỹỵ]', 'y', s)
#     s = re.sub('[ÝỲỶỸỴ]', 'Y', s)
#     s = re.sub('đ', 'd', s)
#     s = re.sub('Đ', 'D', s)
#     return s

# no_accent_locations = [no_accent_vietnamese(x) for x in locations]

# def fuzzy_search(substr_list, str):
#     max_ratio = 0
#     max_sub_str = ''
#     for substr in substr_list:
#         ratio = fuzz.partial_ratio(substr.lower(), str.lower())
#         if ratio > max_ratio:
#             max_ratio = ratio
#             max_sub_str = substr
#     if max_ratio > FUZZY_THRESHOLD:
#         return max_sub_str
#     return ''
    
# def build_path_dict(dir):
#     id_path_dict = {}
#     for path, subdirs, files in os.walk(dir):
#         for name in files:
#             id_path_dict[name.split('_')[0]] = os.path.join(path, name)
#     return id_path_dict

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

new_cv_dict = {}
c = 0
for i in range(8, 13):
    with open(r'job_recsys\pickle\backup2\cv_dict_pack{}.pkl'.format(i), 'rb') as f:
        small_cv_dict = pickle.load(f)
    # pprint.pprint(small_cv_dict)
    for id, a_cv in small_cv_dict.items():
        c += 1
        print(c)
        if a_cv != None:
            exp = '\n'.join(a_cv['exp'])
            exp = exp.lower()
            a_cv['skills'] = extract_skill_from_text(exp.lower())
        new_cv_dict[id] = a_cv
    with open(r'job_recsys\pickle\backup2\new_cv_dict_{}.pkl'.format(i), 'wb') as f:
        pickle.dump(new_cv_dict, f)

# with open(r'job_recsys\pickle\backup\cv_dict_pack{}.pkl'.format(0), 'rb') as f:
#     small_cv_dict = pickle.load(f)
# pprint.pprint(small_cv_dict)

# with open(r'job_recsys/pickle/cv_dict.pkl', 'rb') as f:
#     new_cv_dict = pickle.load(f)
# print(len(new_cv_dict))
# print(new_cv_dict.keys())
# pprint.pprint(new_cv_dict['2447977'])

# with open(r'job_recsys/pickle/cv_dict.pkl', 'rb') as f:
#     cv_dict = pickle.load(f)

# c = 0
# for k, v in cv_dict.items():
#     if v != None:
#         if v['location'] != '':
#             city = no_accent_vietnamese(v['location']).lower()
#             if city == 'thanh pho ho chi minh' or city == 'tp hcm':
#                 city = 'ho chi minh'
#             cv_dict[k]['location'] = [city]
#             print(v['location'])
#             c += 1
#         else:
#             cv_dict[k]['location'] = []

# for k, v in cv_dict.items():
#     if v != None and v['job_lv_id'] == '':
#         cv_dict[k]['job_lv_id'] = 0

# with open(r'job_recsys/pickle/cv_dict.pkl', 'wb') as f:
#     pickle.dump(cv_dict, f)
# # pprint.pprint(cv_dict)

# with open(r'job_recsys/pickle/jd_dict.pkl', 'rb') as f:
#     jd_dict = pickle.load(f)

# # pprint.pprint(jd_dict)
# print(len(jd_dict))
# c = 0
# for k, v in jd_dict.items():
#     if len(v['skills']) != 0:
#         # print(v['skills'])
#         c += 1
# print(c)

# with open(r'job_recsys/pickle/cv_dict.pkl', 'rb') as f:
#     cv_dict = pickle.load(f)
# c = 0
# for k, v in cv_dict.items():
#     if v != None and len(v['skills']) != 0:
#         print(v['skills'])
#         c += 1
# print(c)

# for k, v in jd_dict.items():
#     new_locs = []
#     for l in v['location']:
#         if l == 'tp hcm' or l == 'thanh pho ho chi minh':
#             l = 'ho chi minh'
#         new_locs.append(l)
#     jd_dict[k]['location'] = new_locs

# with open(r'job_recsys/pickle/jd_dict.pkl', 'wb') as f:
#     pickle.dump(jd_dict, f)