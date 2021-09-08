import pandas as pd
import sqlite3
from app.parameters import SKILL_LEXICON_PATH, JD_EXCEL_PATH, DB_PATH

def get_db(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def insert_skills(conn, all_skills):
    try:
        cursor = conn.cursor()
        for skill in all_skills:
            # print(skill)
            sqlite_insert_query = 'INSERT OR REPLACE INTO skill (id, name) VALUES (?, ?)'
            data_tuple = (skill, skill)
            cursor.execute(sqlite_insert_query, data_tuple)
            conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)

def insert_jd(conn, raw_jds):
    try:
        cursor = conn.cursor()
        for jd in raw_jds.values():
            id = jd['_id/0']
            # print(id)
            company_name = jd['company_name']
            company_address = jd['company_address']
            title = jd['title'].replace('_x000D_','')
            job_formality = jd['job_formality']
            salary = jd['salary'].replace('_x000D_','')
            job_experience_years = jd['job_experience_years']
            if pd.isna(jd['job_descriptions']):
                job_descriptions = ''
            else:
                job_descriptions = jd['job_descriptions'].replace('_x000D_','')
            if pd.isna(jd['job_requirements']):
                job_requirements = ''
            else:
                job_requirements = jd['job_requirements'].replace('_x000D_','')
            skills = []
            for i in range(5):
                skill = jd['skills/{}'.format(i)]
                if not pd.isna(skill):
                    skills.append(skill)
            skills = ', '.join(skills)

            sqlite_insert_query = '''
            INSERT OR REPLACE INTO jd (id, company_name, company_address, title, job_formality, 
            salary, job_experience_years, job_descriptions, job_requirements, skills) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            '''
            data_tuple = (id, company_name, company_address, title, job_formality, 
            salary, job_experience_years, job_descriptions, job_requirements, skills)
            cursor.execute(sqlite_insert_query, data_tuple)
            conn.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)

if __name__ == "__main__":
    conn = get_db(DB_PATH)

    # Skills
    # First, in SQLite CLI, create table skills by this command: "create table skill (id text primary key, name text);" 
    all_skills = []
    with open(SKILL_LEXICON_PATH, 'r', encoding='utf-8') as f:
        for skill in f:
            all_skills.append(skill.rstrip('\n').replace(' +', '+'))
    insert_skills(conn, all_skills)

    # JD
    # First, in SQLite CLI, create table jd by this command: "create table jd 
    # (id text primary key, company_name text, company_address text, title text, job_formality text, salary text,
    # job_experience_years text, job_descriptions text, job_requirements text, skills text);" 
    raw_jds = pd.read_excel(JD_EXCEL_PATH, sheet_name='Sheet1', engine='openpyxl').to_dict('index')
    insert_jd(conn, raw_jds)
