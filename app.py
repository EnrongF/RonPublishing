from flask import Flask, request, abort
from flask import jsonify
from flask import make_response
import json
import MySQLdb

app = Flask(__name__)


@app.route('/api/v1/info')
def home_index():
    conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='Chenglong1121',
        db='test'
    )
    print('open database successfully')
    api_list = []
    cur = conn.cursor()
    cur.execute('select buildtime, version, methods, links from apirelease')

    for row in cur.fetchall():
        api = {'version': row[0], 'buildtime': row[1], 'methods': row[2], 'linkds': row[3]}
        api_list.append(api)

    conn.close()
    return jsonify({'api_version': api_list}), 200


@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return list_users()


def list_users():
    conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='Chenglong1121',
        db='test'
    )
    print('open database successfully')
    api_list = []
    cur = conn.cursor()
    cur.execute('select username, full_name, emailid, password, id from users')

    for row in cur.fetchall():
        a_dict = {'username': row[0], 'name': row[1], 'emailid': row[2], 'password': row[3], 'id': row[4]}
        api_list.append(a_dict)
    conn.close()
    return jsonify({'user_list': api_list})


@app.route('/api/v1/users', methods=['POST'])
def create_user():
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)
    user = {
        'username': request.json['username'],
        'email': request.json['email'],
        'name': request.json['name'],
        'password': request.json['password']
    }
    return jsonify({'status': add_user(user)}), 201


@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def add_user(new_user):
    conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='Chenglong1121',
        db='test'
    )
    print('open database successfully')
    api_list = []
    cur = conn.cursor()
    cur.execute('select * from users where username = %s or emailid = %s', (new_user['username'], new_user['email']))
    data = cur.fetchall()
    if len(data) != 0:
        abort(409)
    else:
        cur.execute('insert into users (username, emailid, password, full_name) values (%s, %s, %s, %s)',
                    (new_user['username'], new_user['email'], new_user['password'], new_user['name']))
        conn.commit()
        return 'Success'
    conn.close()
    return jsonify(new_user)


@app.errorhandler(409)
def invalid_request(error):
    return make_response(jsonify({'error': 'User exist'}), 409)


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return list_user(user_id)


@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
    if not request.json or not 'username' in request.json:
        abort(400)
    user = request.json['username']
    return jsonify({'status': del_user(user)}), 200


def del_user(del_user):
    conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='Chenglong1121',
        db='test'
    )
    print('open database successfully')
    cur = conn.cursor()
    cur.execute('select * from users where username = %s', (del_user,))
    data = cur.fetchall()
    print('Data', data)
    if len(data) == 0:
        abort(400)
    else:
        cur.execute('delete from users where username = %s', (del_user,))
        conn.commit()
        return "Success"


@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = {}
    if not request.json:
        abort(400)
    user['id'] = user_id
    key_list = request.json.keys()
    for i in key_list:
        user[i] = request.json[i]
    print(user)
    return jsonify({'status': upd_user(user)}), 200


def upd_user(user):
    conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='Chenglong1121',
        db='test'
    )
    print('open database successfully')
    cur = conn.cursor()
    cur.execute('select * from users where id = %s', (user['id'],))
    data = cur.fetchall()
    print(data)
    if len(data) == 0:
        abort(404)
    else:
        key_list = user.keys()
        for i in key_list:
            if i != 'id':
                print(user, i)
                cur.execute('update users set {0} = %s where id = %s'.format(i), (user[i], user['id'],))
                conn.commit()
    return "Success"


def list_user(user_id):
    conn = MySQLdb.connect(
        host='localhost',
        port=3306,
        user='root',
        passwd='Chenglong1121',
        db='test'
    )
    print('open database successfully')
    api_list = []
    cur = conn.cursor()
    cur.execute('select username, full_name, emailid, password, id from users where id = %s', (user_id,))
    data = cur.fetchall()

    if len(data) != 0:
        user = {'id': data[0][0], 'username': data[0][1], 'email': data[0][2], 'password': data[0][3],
                'name': data[0][4]}
        return jsonify(user)
    else:
        abort(404)
    conn.close()


@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
