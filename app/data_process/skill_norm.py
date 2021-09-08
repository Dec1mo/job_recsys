from app.parameters import TRAIN_EMP_INFO_PKL_PATH, JD_PKL_PATH, SKILL_NORM_DICT_PKL_PATH
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from dirty_cat import SimilarityEncoder
from sklearn.cluster import AffinityPropagation

def skill_clustering(df, min_df=5, max_df=0.9):
    skill_tfidf = TfidfVectorizer(min_df=min_df, max_df=max_df, token_pattern=r'\S+').fit(df)
    all_skills = skill_tfidf.get_feature_names()
    all_skills = np.array(all_skills)
    skill_ngram_embeddings = SimilarityEncoder(similarity='ngram').fit_transform(all_skills.reshape(-1, 1))
    skill_ngram_embeddings = np.array(skill_ngram_embeddings)

    affprop = AffinityPropagation(affinity="precomputed", random_state=0, verbose=True, max_iter=2000, damping=0.9)
    affprop.fit(skill_ngram_embeddings)
    skill_norm_dict = {}
    for cluster_id in np.unique(affprop.labels_):
        std_skill = all_skills[affprop.cluster_centers_indices_[cluster_id]]
        skill_norm_dict[std_skill] = std_skill
        cluster = np.unique(all_skills[np.nonzero(affprop.labels_==cluster_id)])
        for s in cluster:
            skill_norm_dict[s] = std_skill
    return skill_norm_dict

if __name__ == "__main__":
    with open(TRAIN_EMP_INFO_PKL_PATH, 'rb') as f:
        train_emp_info_dict = pickle.load(f)
    with open(JD_PKL_PATH, 'rb') as f:
        jd_dict = pickle.load(f)

    all_skills = []
    for k, v in train_emp_info_dict.items():
        all_skills.append(' '.join(v['skills']))
    for k, v in jd_dict.items():
        all_skills.append(' '.join(v['skills']))

    skill_norm_dict = skill_clustering(all_skills)
    with open(SKILL_NORM_DICT_PKL_PATH, 'wb') as f:
        pickle.dump(skill_norm_dict, f)
    print(len(skill_norm_dict.values()))
    print(len(set(skill_norm_dict.values())))

    