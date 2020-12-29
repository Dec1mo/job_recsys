import pickle 
import pprint

with open (r"job_recsys\pickle\backup2\new_cv_dict_0.pkl", 'rb') as f:
    a = pickle.load(f)

pprint.pprint(a)