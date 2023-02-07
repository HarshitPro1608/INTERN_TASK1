from flask import Flask, request, jsonify,appcontext_popped
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)




class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_instance_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    works = db.relationship('Work', secondary='artist_work', backref='artists')

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(100), nullable=False)
    work_type = db.Column(db.String(20), nullable=False)

artist_work = db.Table('artist_work',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
    db.Column('work_id', db.Integer, db.ForeignKey('work.id'), primary_key=True)
)


@app.route("/")

@app.route('/works', methods=['GET'])
def get_works():
    work_type = request.args.get('work_type')
    artist_name = request.args.get('artist_name')
    if work_type:
        works = Work.query.filter_by(work_type=work_type).all()
    elif artist_name:
        artist = Artist.query.filter_by(name=artist_name).first()
        works = artist.works if artist else []
    else:
        works = Work.query.all()
    return {'works': [{'link': work.link, 'work_type': work.work_type} for work in works]}


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name=data.get('name')
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    client = Client(name=data['name'], user_instance_id=user.id)
    db.session.add(client)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

