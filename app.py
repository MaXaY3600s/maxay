from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # Добавлено для проверки почты

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    project_link = db.Column(db.String(255))
    amount_paid = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")  # "approved", "rejected"

# Регистрация
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not email or not password or not confirm_password:
        return jsonify({"error": "Пожалуйста, укажите все обязательные поля."}), 400

    # Проверяем, существует ли уже пользователь с таким email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Этот email уже зарегистрирован."}), 400

    if password != confirm_password:
        return jsonify({"error": "Пароли не совпадают."}), 400

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Регистрация успешна! Пожалуйста, подтвердите ваш email."}), 201

# Вход
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Пожалуйста, укажите email и пароль."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Пользователь с таким email не найден."}), 400

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Неверный пароль."}), 400

    if not user.is_verified:
        return jsonify({"error": "Почта не подтверждена."}), 400

    token = create_access_token(identity=user.id)
    return jsonify(access_token=token)

@app.route('/add_review', methods=['POST'])
@jwt_required()
def add_review():
    data = request.json
    user_id = get_jwt_identity()  # Извлекаем user_id из JWT токена
    if 'service' not in data or 'amount_paid' not in data or 'rating' not in data or 'comment' not in data:
        return jsonify({"error": "Пожалуйста, укажите все обязательные поля."}), 400

    new_review = Review(
        user_id=user_id,
        service=data['service'],
        project_link=data.get('project_link', ''),
        amount_paid=data['amount_paid'],
        rating=data['rating'],
        comment=data['comment']
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({"message": "Отзыв отправлен на модерацию!"}), 201

@app.route('/reviews', methods=['GET'])
def get_reviews():
    reviews = Review.query.filter_by(status="approved").all()
    return jsonify([{
        "service": r.service,
        "project_link": r.project_link,
        "amount_paid": r.amount_paid,
        "rating": r.rating,
        "comment": r.comment
    } for r in reviews])

if __name__ == '__main__':
    with app.app_context():  # Добавляем контекст приложения
        db.create_all()  # Создаем таблицы
    app.run(debug=True)
