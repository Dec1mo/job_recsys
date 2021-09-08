from flask import request, Blueprint, jsonify

from app.db_connector.sqlite_connector import get_db
from app.parameters import DB_PATH

skill_controller = Blueprint('skill_controller', __name__)

@skill_controller.route('/api/get_skills', methods = ['POST'])
def get_skills():
    searchbox = request.form.get("text")
    conn = get_db(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT * FROM skill WHERE name LIKE '{}%' ORDER BY name".format(searchbox)
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    std_res = [{'id':p[0], 'text':p[1]} for p in result]
    # pprint.pprint(std_res)
    return jsonify({"results": std_res})
