APP_HOST = '0.0.0.0'
APP_PORT = 5000

# External API
CV_PARSER_API = 'http://127.0.0.1:60000/parser'
SKILL_EXTRACTOR_API = 'http://127.0.0.1:5000/skill'

# Uploaded resumes
UPLOADED_RESUMES_PATH = 'app/static/upload_resumes'

# SQLite DB
DB_PATH = 'db/job_rec.db'

# Preprocess
CV_DIR_PATH = 'data/cvs'
PROFILE_JSON_PATH = 'data/profiles/profiles.json'
JD_EXCEL_PATH = 'data/jds/vi_jd_6k.xlsx'

CV_PKL_PATH = 'saved_files/preprocessed_data/cv_dict.pkl'
PROFILE_PKL_PATH = 'saved_files/preprocessed_data/profile_dict.pkl'
JD_PKL_PATH = 'saved_files/preprocessed_data/jd_dict.pkl'
EMP_INFO_PKL_PATH = 'saved_files/preprocessed_data/emp_info_dict.pkl'
TRAIN_EMP_INFO_PKL_PATH = 'saved_files/preprocessed_data/train_emp_info_dict.pkl'
TEST_EMP_INFO_PKL_PATH = 'saved_files/preprocessed_data/test_emp_info_dict.pkl'

# Skill Normalization
SKILL_LEXICON_PATH = 'data/skill_lexicon/skill_vietnamwork.txt'
SKILL_NORM_DICT_PKL_PATH = 'saved_files/preprocessed_data/skill_norm_dict.pkl'

# Embedding
SKILL_TFIDF_PIPELINE_PKL_PATH = 'saved_files/model/skill_tfidf_pipeline.pkl'
SKILL_LSA_PIPELINE_PKL_PATH = 'saved_files/model/skill_lsa_pipeline.pkl'
SKILL_NBOW_PIPELINE_PKL_PATH = 'saved_files/model/skill_nbow_pipeline.pkl'
SKILL_DISTANCES_PKL_PATH = 'saved_files/model/skill_distances.pkl'
EXP_YEAR_PIPELINE_PKL_PATH = 'saved_files/model/exp_year_pipeline.pkl'
JOB_LV_ID_PIPELINE_PKL_PATH = 'saved_files/model/job_lv_id_pipeline.pkl'
LOCATION_PIPELINE_PKL_PATH = 'saved_files/model/location_pipeline.pkl'

TRAIN_EMP_INFO_VECTOR_DICT_PKL_PATH = 'saved_files/db/train_emp_info_vector_dict.pkl'
TEST_EMP_INFO_VECTOR_DICT_PKL_PATH = 'saved_files/db/test_emp_info_vector_dict.pkl'
JD_VECTOR_DICT_PKL_PATH = 'saved_files/db/jd_vector_dict.pkl'

TFIDF_RESULT_PKL_PATH = 'saved_files/result/tfidf_result.pkl'
LSA_RESULT_PKL_PATH = 'saved_files/result/lsa_result.pkl'
WMD_RESULT_PKL_PATH = 'saved_files/result/wmd_result.pkl'

# Lexicons
job_lv_to_id = {
    # All web
    'Nhân viên':2, 
    'Quản lý':4, 
    'Trưởng nhóm / Giám sát':3,
    'Sinh viên/ Thực tập sinh':1,
    'Giám đốc':5,
    'Mới tốt nghiệp':1,
    'Phó Giám đốc':5,
    'Cao đẳng':1,
    'Đại học':1,
    'Trung cấp':0,
    'Không yêu cầu':0,
    'Trung học':0,
    'Cử nhân':1,
    'PTCS':0,
    'Kỹ sư':2,
    'Chứng chỉ':1,
    'Thạc sĩ':2,
    'Khác':2,
    'Trên đại học':1,
    'Mới tốt nghiệp / Thực tập sinh':1,
    'Trưởng phòng':4,
    'Trưởng nhóm':3,
    # vietnameworks
    'Mới tốt nghiệp/Thực tập sinh':1,
    # 'Nhân viên':2,
    'Trưởng nhóm/Giám sát':3,
    # 'Trưởng phòng':4,
    # 'Giám đốc':5,
    # More
    'Sinh viên':1,
    'Thực tập':1,
}

month_to_num = {
    'jan':'1',
    'january':'1',
    'february':'2',
    'feb':'2',
    'march':'3',
    'mar':'3',
    'april':'4',
    'apr':'4',
    'may':'5',
    'june':'6',
    'jun':'6',
    'july':'7',
    'jul':'7',
    'august':'8',
    'aug':'8',
    'september':'9',
    'sep':'9',
    'october':'10',
    'oct':'10',
    'november':'11',
    'nov':'11',
    'december':'12',
    'dec':'12'
}

vi_locations = [
    'An Giang',
    'Bà Rịa - Vũng Tàu',
    'Bắc Giang',
    'Bắc Kạn',
    'Bạc Liêu',
    'Bắc Ninh',
    'Bến Tre',
    'Bình Định',
    'Bình Dương',
    'Bình Phước',
    'Bình Thuận',
    'Cà Mau',
    'Cao Bằng',
    'Đắk Lắk',
    'Đắk Nông',
    'Điện Biên',
    'Đồng Nai',
    'Đồng Tháp',
    'Gia Lai',
    'Hà Giang',
    'Hà Nam',
    'Hà Tĩnh',
    'Hải Dương',
    'Hậu Giang',
    'Hòa Bình',
    'Hưng Yên',
    'Khánh Hòa',
    'Kiên Giang',
    'Kon Tum',
    'Lai Châu',
    'Lâm Đồng',
    'Lạng Sơn',
    'Lào Cai',
    'Long An',
    'Nam Định',
    'Nghệ An',
    'Ninh Bình',
    'Ninh Thuận',
    'Phú Thọ',
    'Quảng Bình',
    'Quảng Nam',
    'Quảng Ngãi',
    'Quảng Ninh',
    'Quảng Trị',
    'Sóc Trăng',
    'Sơn La',
    'Tây Ninh',
    'Thái Bình',
    'Thái Nguyên',
    'Thanh Hóa',
    'Thừa Thiên Huế',
    'Tiền Giang',
    'Trà Vinh',
    'Tuyên Quang',
    'Vĩnh Long',
    'Vĩnh Phúc',
    'Yên Bái',
    'Phú Yên',
    'Cần Thơ',
    'Đà Nẵng',
    'Hải Phòng',
    'Hà Nội',
    # 'TP HCM',
    # 'Thành phố Hồ Chí Minh',
    'Hồ Chí Minh'
]

