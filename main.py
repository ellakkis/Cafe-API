from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()
db.create_all()


# CREATE TABLE
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


# http://127.0.0.1:5000/search?loc=Peckham
@app.route("/search")
def search():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_cafe = Cafe(
            name=request.args.get("name"),
            map_url=request.args.get("map_url"),
            img_url=request.args.get("img_url"),
            location=request.args.get("location"),
            seats=request.args.get("seats"),
            has_toilet=bool(request.args.get("has_toilet")),
            has_wifi=bool(request.args.get("has_wifi")),
            has_sockets=bool(request.args.get("has_sockets")),
            can_take_calls=bool(request.args.get("can_take_calls")),
            coffee_price=request.args.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})


# http://127.0.0.1:5000/update-price/22?new_price=5
@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    if request.method == 'PATCH':
        cafe_to_update = db.session.query(Cafe).get(cafe_id)
        if cafe_to_update:
            cafe_to_update.coffee_price = request.args.get("new_price")
            db.session.add(cafe_to_update)
            db.session.commit()
            return jsonify(response={"success": "Successfully updated coffee price."}), 200
        else:
            return jsonify(response={"Not Found": "Sorry, a cafe with that id was not found in the database"}), 404


@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    if request.method == 'DELETE':
        if request.args.get('api-key') == "TopSecretAPIKey":
            cafe_to_delete = db.session.query(Cafe).get(cafe_id)
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify(response={"success": "Successfully updated coffee price."}), 200
            else:
                return jsonify(response={"Not Found": "Sorry, a cafe with that id was not found in the database"}), 404
        else:
            return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
