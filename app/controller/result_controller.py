from flask import render_template, request, Blueprint
from werkzeug.utils import secure_filename
import os

from app.parameters import *
from app.data_process.preprocess import *
from app.model.embedding import *
from app.model.ranking import *
from app.db_connector.sqlite_connector import get_db

# Load model
with open(SKILL_NORM_DICT_PKL_PATH, 'rb') as f:
    skill_norm_dict = pickle.load(f)
with open(SKILL_TFIDF_PIPELINE_PKL_PATH, 'rb') as f:
    skill_tfidf_pipeline = pickle.load(f)
with open(SKILL_LSA_PIPELINE_PKL_PATH, 'rb') as f:
    skill_lsa_pipeline = pickle.load(f)
with open(SKILL_NBOW_PIPELINE_PKL_PATH, 'rb') as f:
    skill_nbow_pipeline = pickle.load(f)
with open(EXP_YEAR_PIPELINE_PKL_PATH, 'rb') as f:
    exp_year_pipeline = pickle.load(f)
with open(JOB_LV_ID_PIPELINE_PKL_PATH, 'rb') as f:
    job_lv_id_pipeline = pickle.load(f)
with open(LOCATION_PIPELINE_PKL_PATH, 'rb') as f:
    location_pipeline = pickle.load(f)
with open(JD_VECTOR_DICT_PKL_PATH, 'rb') as f:
    jd_vector_dict = pickle.load(f)

# CV name -> CV Path
id_path_dict = build_path_dict(CV_DIR_PATH)

# Profile
with open(PROFILE_PKL_PATH, 'rb') as f:
    profile_dict = pickle.load(f)

def build_jd_res(jd_id_list, max_sims=None):
    if max_sims == None:
        max_sims = [0.8] * len(jd_id_list)
    conn = get_db(DB_PATH)
    jd_list = []
    for i, jd_id in enumerate(jd_id_list):
        cursor = conn.cursor()
        query = "SELECT * FROM jd WHERE id='{}'".format(jd_id)
        cursor.execute(query)
        result = cursor.fetchone()
        # pprint.pprint(result)
        a_dict = {}
        max_similarity = max_sims[i]
        a_dict['max_similarity'] = "{:.2f}".format(max_similarity * 100)
        a_dict['Company name'] = result[1]
        a_dict['Company Address'] = result[2]
        a_dict['Title'] = result[3]
        a_dict['Job Formality'] = result[4]
        a_dict['Salary'] = result[5]
        a_dict['Job Exp Years'] = result[6]
        a_dict['Job Descriptions'] = result[7]
        a_dict['Job Requirements'] = result[8]
        a_dict['Skills'] = result[9]
        # a_dict['Slots'] = this_jd['job_number_available']
        jd_list.append(a_dict)
    conn.close()
    return jd_list

result_controller = Blueprint('result_controller', __name__)

@result_controller.route('/result', methods=['POST'])
def get_result():
    # Resume part
    try:
        f = request.files['file']
        filepath = os.path.join(UPLOADED_RESUMES_PATH, secure_filename(f.filename))
        f.save(filepath)
        with open(filepath, 'rb') as file_object:
            resume = process_a_cv(file_object)
    except FileNotFoundError:
        resume = {'skills':set(), 'exp_year':0, 'job_lv_id':0, 'location':[]}

    # Profile part
    profile = {}

    skill_list = request.form.getlist('skills')
    skills = set()
    for skill in skill_list:
        skill = skill.replace('+', ' +').replace(' ', '_').lower()
        if skill in skill_norm_dict:
            skills.add(skill_norm_dict[skill])
    profile['skills'] = skills
    front_skills = ', '.join(skill_list)

    try:
        exp_year = int(request.form['experience'])
    except ValueError:
        exp_year = 0
    profile['exp_year'] = exp_year

    joblv = request.form['joblv'].strip().split(',')
    job_lv_id, job_lv_name = int(joblv[0]), joblv[1]
    profile['job_lv_id'] = job_lv_id

    standard_locations = []
    locations = []
    for l in request.form.getlist('location'):
        standard_locations.append(l.split(',')[0])
        locations.append(l.split(',')[1])
    profile['location'] = standard_locations
    front_location = ', '.join(locations)
    
    # combine resume and profile
    persona = {'new_emp_id':combine_cv_profile(resume, profile, min_exp_year=0, max_exp_year=10)}

    # embedding
    persona_vector_dict = build_vector_dict(persona, skill_norm_dict, \
            skill_tfidf_pipeline, skill_lsa_pipeline, \
            skill_nbow_pipeline, exp_year_pipeline, \
            job_lv_id_pipeline, location_pipeline)

    lsa_res_dict = skill_lsa_cos_sim(persona_vector_dict, jd_vector_dict, k=3)
    
    sim_lists  = lsa_res_dict.values()
    sim_list_iterator = iter(sim_lists)
    sim_list = next(sim_list_iterator)

    jd_id_list = [x[0] for x in sim_list]
    max_sims = [x[1] for x in sim_list]
    jd_list = build_jd_res(jd_id_list, max_sims)
    return render_template("result.html", filename=f.filename, skills=front_skills, exp_year=exp_year, \
        job_lv_name=job_lv_name, location=front_location, jd_list=jd_list)