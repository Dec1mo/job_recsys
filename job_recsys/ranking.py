
def cosine_sim():
    pass

def wmd_sim():
    pass

if __name__ == "__main__":
    r = rd.Random()
    r.seed(16)
    random_emp_ids = r.sample(list(emp_info_vecs), k=50)
    # print('random_emp_ids = ', random_emp_ids)
    random_emp_info_vecs = {}
    for i in random_emp_ids:
        random_emp_info_vecs[i] = emp_info_vecs[i]
        # print('i = ', i)
        # print('vec = ', emp_info_vecs[i])

    emp_info_iter_to_id = {}
    for i, k in enumerate(random_emp_info_vecs.keys()):
        emp_info_iter_to_id[i] = k

    jd_iter_to_id = {}
    for i, k in enumerate(jd_vecs.keys()):
        jd_iter_to_id[i] = k

    distances = distance.cdist(list(random_emp_info_vecs.values()), list(jd_vecs.values()), "cosine")
    for i, dis in enumerate(distances):
        dis = np.nan_to_num(dis,nan=1)  
        min_index = np.argmin(dis)
        min_distance = dis[min_index]
        max_similarity = 1 - min_distance
        print('max_similarity = ', max_similarity)
        print('emp id = ', emp_info_iter_to_id[i])
        print(all_data[emp_info_iter_to_id[i]])
        print('-' * 80)
        print('jd id = ', jd_iter_to_id[i])
        print(all_data[jd_iter_to_id[min_index]])
        print('#' * 80)