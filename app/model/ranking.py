import pickle
import numpy as np
import pandas as pd
import random as rd
from app.parameters import *

# from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler, normalize
# from scipy.spatial import distance
from scipy.spatial.distance import cosine
from pyemd import emd

def it_to_id(a_dict):
    it_to_id_dict = {}
    for it, id in enumerate(a_dict.keys()):
        it_to_id_dict[it] = id
    return it_to_id_dict

def skill_tfidf_cos_sim(emp_infos, jds, weights={'skill':0.4, 'exp_year': 0.2, 'job_lv_id': 0.2, 'location':0.2}, k=10):
    jd_it_to_id = it_to_id(jds)

    res_dict = {}
    for emp_id, emp_vec_dict in emp_infos.items():
        # print(emp_id)
        dis = np.zeros(len(jds))
        for i, jd_vec_dict in enumerate(jds.values()):
            skill_dis = cosine(emp_vec_dict['skill_tfidf_vector'].toarray().ravel(),\
                jd_vec_dict['skill_tfidf_vector'].toarray().ravel())
            # print('skill_wmd = ', skill_wmd)

            exp_year_dis = max(jd_vec_dict['exp_year_vector'][0][0] - emp_vec_dict['exp_year_vector'][0][0], 0)
            # print('exp_year_dis = ', exp_year_dis)

            job_lv_id_dis = max(jd_vec_dict['job_lv_id_vector'][0][0] - emp_vec_dict['job_lv_id_vector'][0][0], 0)
            # print('job_lv_id_dis = ', job_lv_id_dis)

            # print("emp_vec_dict['location_vector'] = ", emp_vec_dict['location_vector'])
            # print(type(emp_vec_dict['location_vector']))
            emp_loc_indices = np.where(emp_vec_dict['location_vector'].toarray() == 1)
            jd_loc_indices = np.where(jd_vec_dict['location_vector'].toarray() == 1)
            intersect_loc = np.intersect1d(emp_loc_indices, jd_loc_indices)
            # print('intersect_loc = ', intersect_loc)
            if intersect_loc.size == 0:
                location_cos_dis = 1
            else:
                location_cos_dis = 0
            # print('location_cos_dis = ', location_cos_dis)

            dis[i] = skill_dis*weights['skill'] + exp_year_dis*weights['exp_year'] + \
                job_lv_id_dis*weights['job_lv_id'] + location_cos_dis*weights['location']

        idxes = np.argpartition(dis, k)[:k]
        min_dis = dis[idxes]
        pair_of_list = ([jd_it_to_id[idx] for idx in idxes], 1-min_dis)
        list_of_pair = [(pair_of_list[0][i], pair_of_list[1][i]) for i in range(k)]
        res_dict[emp_id] = sorted(list_of_pair, key=lambda tup: -tup[1])
    return res_dict

def skill_lsa_cos_sim(emp_infos, jds, weights={'skill':0.4, 'exp_year': 0.2, 'job_lv_id': 0.2, 'location':0.2}, k=10):
    jd_it_to_id = it_to_id(jds)

    res_dict = {}
    for emp_id, emp_vec_dict in emp_infos.items():
        # print(emp_id)
        dis = np.zeros(len(jds))
        for i, jd_vec_dict in enumerate(jds.values()):
            skill_dis = cosine(emp_vec_dict['skill_lsa_vector'],\
                jd_vec_dict['skill_lsa_vector'])
            # print('skill_dis = ', skill_dis)
            if pd.isna(skill_dis):
                skill_dis = 1

            exp_year_dis = max(jd_vec_dict['exp_year_vector'][0][0] - emp_vec_dict['exp_year_vector'][0][0], 0)
            # print('exp_year_dis = ', exp_year_dis)

            job_lv_id_dis = max(jd_vec_dict['job_lv_id_vector'][0][0] - emp_vec_dict['job_lv_id_vector'][0][0], 0)
            # print('job_lv_id_dis = ', job_lv_id_dis)

            # print("emp_vec_dict['location_vector'] = ", emp_vec_dict['location_vector'])
            # print(type(emp_vec_dict['location_vector']))
            emp_loc_indices = np.where(emp_vec_dict['location_vector'].toarray() == 1)
            jd_loc_indices = np.where(jd_vec_dict['location_vector'].toarray() == 1)
            intersect_loc = np.intersect1d(emp_loc_indices, jd_loc_indices)
            # print('intersect_loc = ', intersect_loc)
            if intersect_loc.size == 0:
                location_cos_dis = 1
            else:
                location_cos_dis = 0
            # print('location_cos_dis = ', location_cos_dis)

            dis[i] = skill_dis*weights['skill'] + exp_year_dis*weights['exp_year'] + \
                job_lv_id_dis*weights['job_lv_id'] + location_cos_dis*weights['location']

        idxes = np.argpartition(dis, k)[:k]
        min_dis = dis[idxes]
        # res_dict[emp_id] = ([jd_it_to_id[idx] for idx in idxes], 1-min_dis)

        pair_of_list = ([jd_it_to_id[idx] for idx in idxes], 1-min_dis)
        list_of_pair = [(pair_of_list[0][i], pair_of_list[1][i]) for i in range(k)]
        res_dict[emp_id] = sorted(list_of_pair, key=lambda tup: -tup[1])
    return res_dict

def skill_nbow_wmd(emp_infos, jds, skill_distances, weights={'skill':0.4, 'exp_year': 0.2, 'job_lv_id': 0.2, 'location':0.2}, k=10):
    jd_it_to_id = it_to_id(jds)

    res_dict = {}
    for emp_id, emp_vec_dict in emp_infos.items():
        dis = np.zeros(len(jds))
        for i, jd_vec_dict in enumerate(jds.values()):
            skill_wmd = emd(emp_vec_dict['skill_nbow_vector'].toarray().ravel().astype(np.double),
                jd_vec_dict['skill_nbow_vector'].toarray().ravel().astype(np.double),
                skill_distances)
            # print('skill_wmd = ', skill_wmd)

            exp_year_dis = max(jd_vec_dict['exp_year_vector'][0][0] - emp_vec_dict['exp_year_vector'][0][0], 0)
            # print('exp_year_dis = ', exp_year_dis)

            job_lv_id_dis = max(jd_vec_dict['job_lv_id_vector'][0][0] - emp_vec_dict['job_lv_id_vector'][0][0], 0)
            # print('job_lv_id_dis = ', job_lv_id_dis)

            # print("emp_vec_dict['location_vector'] = ", emp_vec_dict['location_vector'])
            # print(type(emp_vec_dict['location_vector']))
            emp_loc_indices = np.where(emp_vec_dict['location_vector'].toarray() == 1)
            jd_loc_indices = np.where(jd_vec_dict['location_vector'].toarray() == 1)
            intersect_loc = np.intersect1d(emp_loc_indices, jd_loc_indices)
            # print('intersect_loc = ', intersect_loc)
            if intersect_loc.size == 0:
                location_cos_dis = 1
            else:
                location_cos_dis = 0
            # print('location_cos_dis = ', location_cos_dis)

            dis[i] = skill_wmd*weights['skill'] + exp_year_dis*weights['exp_year'] + \
                job_lv_id_dis*weights['job_lv_id'] + location_cos_dis*weights['location']
        idxes = np.argpartition(dis, k)[:k]
        min_dis = dis[idxes]
        # res_dict[emp_id] = ([jd_it_to_id[idx] for idx in idxes], 1-min_dis)
        pair_of_list = ([jd_it_to_id[idx] for idx in idxes], 1-min_dis)
        list_of_pair = [(pair_of_list[0][i], pair_of_list[1][i]) for i in range(k)]
        res_dict[emp_id] = sorted(list_of_pair, key=lambda tup: -tup[1])
    return res_dict

if __name__ == "__main__":
    with open(TEST_EMP_INFO_VECTOR_DICT_PKL_PATH, 'rb') as f:
        test_emp_info_vector_dict = pickle.load(f)
    with open(JD_VECTOR_DICT_PKL_PATH, 'rb') as f:
        jd_vector_dict = pickle.load(f)
    with open(SKILL_DISTANCES_PKL_PATH, 'rb') as f:
        skill_distances = pickle.load(f)
    #######################

    # Skill TFIDF Cosine Similarity
    # tfidf_res_dict = skill_tfidf_cos_sim(test_emp_info_vector_dict, jd_vector_dict, k=10)
    # with open(TFIDF_RESULT_PKL_PATH, 'wb') as f:
    #     pickle.dump(tfidf_res_dict, f)

    # with open(TFIDF_RESULT_PKL_PATH, 'rb') as f:
    #     tfidf_res_dict = pickle.load(f)
    # for k, v in tfidf_res_dict.items():
    #     print(k)
    #     for pair in v:
    #         print(pair[0], pair[1])
    #     print('-'* 20)
    # print("=======================================")

    # # Skill LSA Cosine Similarity
    lsa_res_dict = skill_lsa_cos_sim(test_emp_info_vector_dict, jd_vector_dict, k=10)
    with open(LSA_RESULT_PKL_PATH, 'wb') as f:
        pickle.dump(lsa_res_dict, f)
    for k, v in lsa_res_dict.items():
        print(k)
        for pair in v:
            print(pair[0], pair[1])
        print('-'* 20)
    print("=======================================")

    # # Skill nBOW WMD
    # wmd_result = skill_nbow_wmd(test_emp_info_vector_dict, jd_vector_dict, skill_distances)
    # # wmd_result = skill_nbow_wmd(test_emp_info_vector_dict, jd_vector_dict, skill_distances)
    # with open(WMD_RESULT_PKL_PATH+'2', 'wb') as f:
    #     pickle.dump(wmd_result, f)

