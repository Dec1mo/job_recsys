import pickle
import numpy as np
import pandas as pd
import random as rd
from app.parameters import *

from sklearn.preprocessing import FunctionTransformer, StandardScaler, MinMaxScaler, Normalizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD
from dirty_cat import SimilarityEncoder

from sklearn.metrics import euclidean_distances
from sklearn.metrics.pairwise import cosine_distances

# After Skill Normalization

# 3 models:
# - skills_tfidf + cos_sim :)
# - skills_lsa + cos_sim :)
# - skills_sim_encoder + wmd :(
# - exp_lsa + skills_lsa + cos_sim + cos_sim :(

def skill_tfidf_pipeline(skills, min_df=5):
    pipeline = Pipeline([
        ('tfidf_embedding', TfidfVectorizer(min_df=min_df)),
        ('scaler', StandardScaler(with_mean=False))
    ])
    return pipeline.fit(skills)

def skill_lsa_pipeline(skills, min_df=5, ndim=50):
    pipeline = Pipeline([
        ('tfidf_embedding', TfidfVectorizer(min_df=min_df)),
        ('lsa_embedding', TruncatedSVD(n_components=ndim)),
        ('scaler', StandardScaler(with_mean=False))
    ])
    return pipeline.fit(skills)

def skill_nbow_pipeline(skills, min_df=5):
    pipeline = Pipeline([
        ('count_embedding', CountVectorizer(min_df=min_df)),
        ('normalizer', Normalizer(norm='l1'))
    ])
    return pipeline.fit(skills)

def build_skill_distances(vectorizer):
    all_skills = vectorizer.get_feature_names()
    all_skills = np.array(all_skills).reshape(-1, 1)
    similarity_encoder = SimilarityEncoder(similarity='ngram').fit(all_skills)
    skill_embeddings = similarity_encoder.transform(all_skills)
    # skill_distances = euclidean_distances(skill_embeddings)
    # skill_distances = cosine_distances(skill_embeddings)
    return cosine_distances(np.array(skill_embeddings))#, dtype=np.float32))

def exp_year_pipeline(exp_years):
    pipeline = Pipeline([
        # ('exp_year_numerical', FunctionTransformer(None)),
        ('scaler', MinMaxScaler())
    ])
    return pipeline.fit(exp_years)

def job_lv_id_pipeline(job_lv_ids):
    pipeline = Pipeline([
        # ('job_lv_id_numerical', FunctionTransformer(None)),
        ('scaler', MinMaxScaler())
    ])
    return pipeline.fit(job_lv_ids)

def location_pipeline(locations):
    pipeline = Pipeline([
        ('location', CountVectorizer()),
        # ('scaler', StandardScaler(with_mean=False))
    ])
    return pipeline.fit(locations)

def build_vector_dict(a_dict, skill_norm_dict, skill_tfidf_pipeline, skill_lsa_pipeline, \
    skill_nbow_pipeline, exp_year_pipeline, job_lv_id_pipeline, location_pipeline):
    vector_dict = {}
    for k, v in a_dict.items():
        skills = set()
        print("Employee's skills before skill norm: ", v['skills'])
        for s in v['skills']:
            if s in skill_norm_dict:
                skills.add(skill_norm_dict[s])
        v['skills'] = ' '.join([s for s in skills])
        print("Employee's skills after skill norm: ", set(v['skills'].split()))

        v['location'] = ' '.join([s.replace(' ', '_') for s in v['location']])

        skill_tfidf_vector = skill_tfidf_pipeline.transform([v['skills']])

        skill_lsa_vector = skill_lsa_pipeline.transform([v['skills']])

        skill_nbow_vector = skill_nbow_pipeline.transform([v['skills']])

        exp_year_vector = exp_year_pipeline.transform([[v['exp_year']]])
        job_lv_id_vector = job_lv_id_pipeline.transform([[v['job_lv_id']]])
        location_vector = location_pipeline.transform([v['location']])

        a_emb_dict = {
            'skill_tfidf_vector': skill_tfidf_vector,
            'skill_lsa_vector': skill_lsa_vector,
            'skill_nbow_vector': skill_nbow_vector,
            'exp_year_vector': exp_year_vector,
            'job_lv_id_vector': job_lv_id_vector,
            'location_vector': location_vector,
        }
        vector_dict[k] = a_emb_dict
    return vector_dict

if __name__ == "__main__":
    with open(TRAIN_EMP_INFO_PKL_PATH, 'rb') as f:
        train_emp_info_dict = pickle.load(f)
    with open(JD_PKL_PATH, 'rb') as f:
        jd_dict = pickle.load(f)
    with open(SKILL_NORM_DICT_PKL_PATH, 'rb') as f:
        skill_norm_dict = pickle.load(f)

    all_skill_sets = []
    all_exp_years = []
    all_job_lv_ids = []
    all_locations = []

    all_data = list(train_emp_info_dict.values()) + list(jd_dict.values())
    for v in all_data:
        skills = set()
        for s in v['skills']:
            if s in skill_norm_dict:
                skills.add(skill_norm_dict[s])
        all_skill_sets.append(' '.join([s for s in skills]))

        all_exp_years.append(v['exp_year'])

        all_job_lv_ids.append(v['job_lv_id'])

        all_locations.append(' '.join([s.replace(' ', '_') for s in v['location']]))

    ############# OK so start training and dumping from here #############
    skill_tfidf_pipeline = skill_tfidf_pipeline(all_skill_sets, min_df=5)
    with open(SKILL_TFIDF_PIPELINE_PKL_PATH, 'wb') as f:
        pickle.dump(skill_tfidf_pipeline, f)

    skill_lsa_pipeline = skill_lsa_pipeline(all_skill_sets, min_df=5, ndim=50)
    with open(SKILL_LSA_PIPELINE_PKL_PATH, 'wb') as f:
        pickle.dump(skill_lsa_pipeline, f)

    skill_nbow_pipeline = skill_nbow_pipeline(all_skill_sets, min_df=5)
    with open(SKILL_NBOW_PIPELINE_PKL_PATH, 'wb') as f:
        pickle.dump(skill_nbow_pipeline, f)

    skill_distances = build_skill_distances(skill_tfidf_pipeline[0])
    with open(SKILL_DISTANCES_PKL_PATH, 'wb') as f:
        pickle.dump(skill_distances, f)

    exp_year_pipeline = exp_year_pipeline(np.array(all_exp_years).reshape(-1,1))
    with open(EXP_YEAR_PIPELINE_PKL_PATH, 'wb') as f:
        pickle.dump(exp_year_pipeline, f)

    job_lv_id_pipeline = job_lv_id_pipeline(np.array(all_job_lv_ids).reshape(-1,1))
    with open(JOB_LV_ID_PIPELINE_PKL_PATH, 'wb') as f:
        pickle.dump(job_lv_id_pipeline, f)

    location_pipeline = location_pipeline(all_locations)
    with open(LOCATION_PIPELINE_PKL_PATH, 'wb') as f:
        pickle.dump(location_pipeline, f)

    train_emp_info_vector_dict = build_vector_dict(train_emp_info_dict, skill_norm_dict, skill_tfidf_pipeline, \
        skill_lsa_pipeline, skill_nbow_pipeline, exp_year_pipeline, job_lv_id_pipeline, location_pipeline)
    with open(TRAIN_EMP_INFO_VECTOR_DICT_PKL_PATH, 'wb') as f:
        pickle.dump(train_emp_info_vector_dict, f)

    jd_vector_dict = build_vector_dict(jd_dict, skill_norm_dict, skill_tfidf_pipeline, skill_lsa_pipeline, \
        skill_nbow_pipeline, exp_year_pipeline, job_lv_id_pipeline, location_pipeline)
    with open(JD_VECTOR_DICT_PKL_PATH, 'wb') as f:
        pickle.dump(jd_vector_dict, f)

    # Make test_emp_info_vector_dict
    with open(TEST_EMP_INFO_PKL_PATH, 'rb') as f:
        test_emp_info_dict = pickle.load(f)

    test_emp_info_vector_dict = build_vector_dict(test_emp_info_dict, skill_norm_dict, skill_tfidf_pipeline, \
        skill_lsa_pipeline, skill_nbow_pipeline, exp_year_pipeline, job_lv_id_pipeline, location_pipeline)

    with open(TEST_EMP_INFO_VECTOR_DICT_PKL_PATH, 'wb') as f:
        pickle.dump(test_emp_info_vector_dict, f)

