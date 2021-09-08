# This includes CVParser and SkillExtractor
# Input: CV+Profile or JD
# Output: a json {skills, exp_year, location, job_lv}

import json
import pandas as pd
import random as rd
import pickle
import re
import ast
import os
import requests
from datetime import datetime
from gensim.parsing.preprocessing import *
from pyvi import ViTokenizer
from fuzzywuzzy import fuzz

from app.parameters import *

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

with open(SKILL_LEXICON_PATH, 'r', encoding='utf-8') as f:
    vi_skills = []
    for skill in f:
        skill = skill.rstrip('\n').lower()
        if len(skill) < 4:
            skill = skill.replace('+', ' +')
        vi_skills.append(skill)

def build_path_dict(dir):
    id_path_dict = {}
    for path, _, files in os.walk(dir):
        for name in files:
            id_path_dict[name.split('_')[0]] = os.path.join(path, name)
    return id_path_dict

def fuzzy_search(substr_list, str, fuzzy_threshold=90):
    max_ratio = 0
    max_sub_str = ''
    for substr in substr_list:
        ratio = fuzz.partial_ratio(substr.lower(), str.lower())
        if ratio > max_ratio:
            max_ratio = ratio
            max_sub_str = substr
    if max_ratio > fuzzy_threshold:
        return max_sub_str
    return ''

def extract_skill_from_text(text, skill_lexicon):
    skills = set()
    texts = text.replace('_',' ').splitlines()
    # Using Skill Extractor
    for t in texts:
        if len(t) > 3:
            try:
                payload = {"text":t, "raw": True}
                extracted_skills = requests.post(url=SKILL_EXTRACTOR_API, json=payload).json()['data']
                skills = skills.union(set([s.lower().strip(' ,_').replace(' ','_')\
                    .replace('/_','').replace('-_','').replace('_.','.').replace('._','.') for s in extracted_skills]))
            except:
                print('skill parser error: ', t)
    # Using Lexicon
    text = ' '.join(text.split()).replace('_',' ').replace('. ','.').lower()
    for skill in skill_lexicon:
        if ' {} '.format(skill).lower() in text:
            skills.add(skill.strip(' ,_').replace(' ','_').replace('/_','').replace('-_','').replace('_.','.').replace('._','.'))
    return skills

def process_a_cv(a_cv):
    # a_cv is a pdf file
    def diff_month(d1, d2):
        return (d1.year - d2.year) + (d1.month - d2.month)/12

    response = requests.post(url=CV_PARSER_API, files={'file': a_cv})
    try:
        a_cv_json = json.loads(response.text)
    except:
        print('Error a_cv_json = ', response.text)
        return None
    if len(a_cv_json) == 0:
        return None

    exp_year = 0
    # max_exp_year = 0
    job_lv_id = 0
    location = ''

    is_first_4digit_year = True
    last_4digit_year = 0
    for box in a_cv_json[0]['boxes']:
        year_diff = 0
        if box['type'] == 'company_time':
            # '15 / 8 / 2018 - 30 / 2 / 2019'
            date_str = box['text'].lower()
            for month_name, month_number in month_to_num.items():
                date_str = date_str.replace(month_name, ' {} '.format(month_number))
            # if '-' in date_str or '–' in date_str:
            time_list =  re.findall(r'\d+', date_str)

            if len(time_list) == 1: 
                # year
                if len(time_list[0]) == 4:
                    if is_first_4digit_year:
                        year_diff = datetime.now().year - int(time_list[0])

                        is_first_4digit_year = False
                        last_4digit_year = int(time_list[0])
                    else:
                        year_diff = max(0, last_4digit_year - int(time_list[0]))
                else:
                    # Exception
                    print(time_list)
            elif len(time_list) == 2: 
                # year - year or month/year or year/month
                if len(time_list[0]) == 4 and len(time_list[1]) == 4:
                    year_diff = int(time_list[1]) - int(time_list[0])
                elif len(time_list[0]) == 4 or len(time_list[1]) == 4:
                    if len(time_list[1]) == 4:
                        month = int(time_list[0])
                        year = int(time_list[1])
                    else:
                        month = int(time_list[1])
                        year = int(time_list[0])
                    try:
                        start_time = datetime(year, month, 1)
                    except ValueError:
                        start_time = datetime(year, 1, 1)

                    if is_first_4digit_year:
                        year_diff = diff_month(datetime.now(), start_time)
                        is_first_4digit_year = False
                        last_4digit_year = start_time
                    else:
                        year_diff = max(0, diff_month(last_4digit_year, start_time))
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
                    # max_year_diff = relativedelta(datetime.now(), start_time).months / 12
                    # max_exp_year = max(max_exp_year, max_year_diff)
                    year_diff = diff_month(datetime.now(), start_time)
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
                    year_diff = diff_month(end_time, start_time)
                elif len(time_list[1]) == 4 and len(time_list[3]) == 4:
                    try:
                        start_time = datetime(int(time_list[1]), int(time_list[0]), 1)
                        end_time = datetime(int(time_list[3]), int(time_list[2]), 1)
                    except ValueError:
                        start_time = datetime(int(time_list[1]), 1, 1)
                        end_time = datetime(int(time_list[3]), 1, 1)
                    year_diff = diff_month(end_time, start_time)
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
                    year_diff = diff_month(end_time, start_time)
                else:
                    # Exception
                    print(time_list)
            else:
                # Exception
                print(time_list)

            exp_year += year_diff
        elif box['type'] == 'position':
            # Becarefullllll
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

    # Skills
    skills = extract_skill_from_text(exp, vi_skills)

    # Exp year
    # if exp_year == 0 or max_exp_year == 0:
    #     exp_year = exp_year + max_exp_year

    # Location
    if location == '':
        location = []
    else:
        if location == 'tp hcm' or location == 'thanh pho ho chi minh':
            location = 'ho chi minh'
        location = [location]
    location = [l.replace(' ', '_') for l in location]

    return {'skills':skills, 'exp_year':exp_year, 'location':location, 'job_lv_id':job_lv_id, 'exp':exp}
     
def process_a_profile(a_profile):
    # Skills
    skills = a_profile['skill_set']
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
    new_locations = [l.replace(' ', '_') for l in new_locations]
    return {'skills':skills, 'exp_year':exp_year, 'job_lv_id':job_lv_id, 'location':new_locations}

def process_a_jd(a_jd):
    # job description
    skills_extracted_from_des = set()
    try:
        job_description = a_jd['job_descriptions'].lower().replace('_x000d_', '\n').strip()
        skills_extracted_from_des = extract_skill_from_text(job_description, vi_skills)
        job_description = ViTokenizer.tokenize(job_description)
    except:
        job_description = ''

    # job requirement
    skills_extracted_from_req = set()
    try:
        job_requirement = a_jd['job_requirements'].lower().replace('_x000d_', '\n').strip()
        skills_extracted_from_req = extract_skill_from_text(job_requirement, vi_skills)
    except:
        job_requirement = ''

    # Skills
    skills = set()
    for i in range(5):
        skill = a_jd['skills/{}'.format(i)]
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
    new_locations = [l.replace(' ', '_') for l in new_locations]
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
    else:
        exp_year = min(cv_year, profile_year)

    # Job lv id
    job_lv_id = 0
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
        locations = list(set(a_cv['location'] + a_profile['location']))

    # Exp
    # exp = a_cv['exp']
    return {'skills':skills, 'exp_year':exp_year, 'job_lv_id':job_lv_id, 'location':locations}

if __name__ == "__main__":
    # # CV Processing
    # id_path_dict = build_path_dict('CV_DIR_PATH')
    # cv_dict = {}
    # for id, path in id_path_dict.items():
    #     with open(path, 'rb') as a_cv:
    #         cv_dict[id] = process_a_cv(a_cv)
    # with open(CV_PKL_PATH, 'wb') as f:
    #     pickle.dump(cv_dict, f)

    # # Profile Processing
    # profile_dict = {}
    # with open(PROFILE_JSON_PATH, 'r') as f:
    #     raw_profiles = json.load(f)
    # for id, a_profile in raw_profiles.items():
    #     profile_dict[id] = process_a_profile(a_profile)
    # with open(PROFILE_PKL_PATH, 'wb') as f:
    #     pickle.dump(profile_dict, f)

    # # JD Processing
    # jd_dict = {}
    # raw_jds = pd.read_excel(JD_EXCEL_PATH, sheet_name='Sheet1', engine='openpyxl').to_dict('index')
    # for a_jd in raw_jds.values():
    #     jd_dict[a_jd['_id/0']] = process_a_jd(a_jd)
    # with open(JD_PKL_PATH, 'wb') as f:
    #     pickle.dump(jd_dict, f)

    # # Emb_info Processing
    # # Emb_info = CV + Profile
    # with open(CV_PKL_PATH, 'rb') as f:
    #     cv_dict = pickle.load(f)
    # # print(len(cv_dict))
    # with open(PROFILE_JSON_PATH, 'rb') as f:
    #     profile_dict = pickle.load(f)
    # # print(len(profile_dict))

    # emp_info_dict = {}
    # for id in cv_dict.keys():
    #     if cv_dict[id] == None or id not in profile_dict:
    #         continue
    #     emp_info_dict[id] = combine_cv_profile(cv_dict[id], profile_dict[id])
    # with open(EMP_INFO_PKL_PATH, 'wb') as f:
    #     pickle.dump(emp_info_dict, f)

    # Train and Test set
    with open(EMP_INFO_PKL_PATH, 'rb') as f:
        emp_info_dict = pickle.load(f)
    r = rd.Random()
    r.seed(25)
    random_emp_ids = r.sample(list(emp_info_dict.keys()), k=75)
    train_emp_info_dict = emp_info_dict.copy()
    test_emp_info_dict = {}
    for emp_id in random_emp_ids:
        del train_emp_info_dict[emp_id]
        test_emp_info_dict[emp_id] = emp_info_dict[emp_id]
    with open(TRAIN_EMP_INFO_PKL_PATH, 'wb') as f:
        pickle.dump(train_emp_info_dict, f)
    with open(TEST_EMP_INFO_PKL_PATH, 'wb') as f:
        pickle.dump(test_emp_info_dict, f)
