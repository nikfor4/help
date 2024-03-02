import os
from flask import Flask, jsonify, request
import psycopg2
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


def connect_to_db():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DATABASE'),
        user=os.environ.get('POSTGRES_USERNAME'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST'),
        port=os.environ.get('POSTGRES_PORT')
    )
    return conn


@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'ok'})


@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM countries")
        countries = cur.fetchall()

        region = request.args.get('region')
        if region:
            filtered_countries = [country for country in countries if country[3] == region]
            return jsonify(filtered_countries)
        else:
            return jsonify(countries)

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()


@app.route('/api/countries/<alpha2>', methods=['GET'])
def get_country_by_alpha2(alpha2):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM countries WHERE alpha2 = %s", (alpha2,))
        country = cur.fetchone()

        if country:
            return jsonify(country)
        else:
            return jsonify({'error': 'Country not found'}), 404

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()


@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        region = request.args.get('region')

        if region:
            cur.execute("SELECT * FROM countries WHERE region = %s", (region,))
        else:
            cur.execute("SELECT * FROM countries")

        countries = cur.fetchall()

        return jsonify(countries)

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()


@app.route('/api/countries/<alpha2>', methods=['GET'])
def get_country_by_alpha2(alpha2):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM countries WHERE alpha2 = %s", (alpha2,))
        country = cur.fetchone()

        if country:
            return jsonify(country)
        else:
            return jsonify({'error': 'Country not found'}), 404

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()


@app.route('/api/countries', methods=['GET'])
def get_countries():
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        region = request.args.get('region')

        if region:
            cur.execute("SELECT * FROM countries WHERE region = %s", (region,))
        else:
            cur.execute("SELECT * FROM countries")

        countries = cur.fetchall()

        return jsonify(countries)

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()


@app.route('/api/profiles/<string:login>', methods=['GET'])
def get_profile_by_login(login):
    try:
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE login = %s", (login,))
        user = cur.fetchone()

        if user:
            profile = {
                'login': user[0],
                'email': user[1],
                'country_code': user[2],
                'is_public': user[3],
                'phone': user[4],
                'image': user[5]
            }
            return jsonify(profile)
        else:
            return jsonify({'error': 'User not found'}), 404

    except psycopg2.Error as e:
        return jsonify({'error': str(e)})

    finally:
        if conn:
            conn.close()


users = {
    "user1": {
        "password": "password123",
        "tokens": []
    }
}


@app.route("/me/updatePassword", methods=["POST"])
def update_password():
    data = request.json
    new_password = data.get("new_password")
    current_password = data.get("current_password")
    token = request.headers.get("Authorization")

    user_login = get_user_login_from_token(token)
    if not user_login:
        return jsonify({"message": "Unauthorized"}), 401

    if users.get(user_login, {}).get("password") != current_password:
        return jsonify({"message": "Current password is incorrect"}), 400

    users[user_login]["password"] = new_password
    users[user_login]["tokens"] = []

    return jsonify({"message": "Password updated successfully"})


def get_user_login_from_token(token: str) -> str:
    return "user1"


# Эндпоинт для добавления друга
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
db = SQLAlchemy(app)


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    friend_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, friend_id):
        self.user_id = user_id
        self.friend_id = friend_id


@app.route('/friends/add', methods=['POST'])
def add_friend():
    data = request.get_json()
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')

    if not user_id or not friend_id:
        return jsonify({"error": "User ID or Friend ID is missing"}), 400

    # Проверяем, не является ли пользователь уже другом
    if Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first():
        return jsonify({"error": "User is already a friend"}), 400

    # Добавляем друга в базу данных
    friend = Friend(user_id=user_id, friend_id=friend_id)
    db.session.add(friend)
    db.session.commit()

    return jsonify({"message": "Friend added successfully"})


@app.route('/friends/remove', methods=['POST'])
def remove_friend():
    data = request.get_json()
    user_id = data.get('user_id')
    friend_id = data.get('friend_id')

    if not user_id or not friend_id:
        return jsonify({"error": "User ID or Friend ID is missing"}), 400

    # Проверяем, является ли пользователь другом
    friend = Friend.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    if not friend:
        return jsonify({"error": "User is not a friend"}), 400

    # Удаляем друга из базы данных
    db.session.delete(friend)
    db.session.commit()

    return jsonify({"message": "Friend removed successfully"})


@app.route('/friends', methods=['GET'])
def get_friends():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is missing"}), 400

    # Получаем список друзей пользователя из базы данных
    friends = Friend.query.filter_by(user_id=user_id).all()

    # Преобразуем результат в формат JSON
    friends_list = [{"friend_id": friend.friend_id} for friend in friends]

    return jsonify({"friends": friends_list})



if __name__ == '__main__':
    app.run(debug=True)
