import json
import re
import pickle
import numpy as np
import pandas as pd
import random as rd

from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from scipy.spatial import distance

def average_vectors(X):
    res = np.zeros((len(X), vector_len))
    print(res.shape)
    for idx, i in enumerate(X.index):
        cv_vector = np.zeros(vector_len)
        c = 0
        for skill in X['skill_set'][i]:
            # print('cv shape = ', cv_vector.shape)
            emb_skill = similarity_encoder.transform(np.array(skill).reshape(1, -1))
            # print('emb skill = ', emb_skill.shape)
            cv_vector = cv_vector + emb_skill
            c += 1
        cv_vector /= c
        # print('res[idx] = ', res[idx,:].shape)
        # print('cv_vector = ', cv_vector.shape)
        res[idx] = cv_vector
    return pd.DataFrame(res)

def make_pipeline(transformers):
    pipeline = Pipeline([
        # Use ColumnTransformer to combine the features
        ('union', ColumnTransformer(
            transformers=transformers,
            remainder='drop'
            )),
        ('scaler', StandardScaler(with_mean=False)),
    ])
    return pipeline

if __name__ == "__main__":
    with open('job_recsys\pickle\emp_info_dict.pkl', 'rb') as f:
        emp_info_dict = pickle.load(f)
    with open('job_recsys\pickle\jd_dict.pkl', 'rb') as f:
        jd_dict = pickle.load(f)

    # Change job req to exp

    all_data = {}
    for k, v in emp_info_dict.items():
        all_data[k] = v
    for k, v in jd_dict.items():
        all_data[k] = v

    df = pd.DataFrame.from_dict(all_data, orient='index',
        columns=['skills', 'exp_year', 'job_lv_id', 'location'])

    new_df = df.copy()
    for i in df.index:
        new_df['skills'][i] = ' '.join(new_df['skills'][i])
        new_df['location'][i] = ' '.join(new_df['location'][i])

    transformers = [
        ('skills_tfidf', TfidfVectorizer(min_df=4), 'skills'),
        ('exp_year_numerical', FunctionTransformer(None), ['exp_year']),
        ('job_lv_id_numerical', FunctionTransformer(None), ['job_lv_id']),
        ('location', OneHotEncoder(), ['location'])
    ]

    pipeline = make_pipeline(transformers)
    emb_vectors = pipeline.fit_transform(new_df)
    emb_vectors = emb_vectors.toarray()

    emp_info_vecs = {}
    jd_vecs = {}
    for i, k in enumerate(all_data.keys()):
        if len(k) < 10:
            emp_info_vecs[k] = emb_vectors[i]
        else:
            jd_vecs[k] = emb_vectors[i]

    with open(r'job_recsys/pickle/emp_info_vecs.pkl', 'wb') as f:
        pickle.dump(emp_info_vecs, f)
    with open(r'job_recsys/pickle/jd_vecs.pkl', 'wb') as f:
        pickle.dump(jd_vecs, f)
    