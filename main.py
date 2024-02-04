from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    #so now let's learn how to construct our own json for users
    #inside of database instance 
    def to_dict(self):
        #Method 1
        dictionary = {}
        for column in self.__table__.columns:
             dictionary[column.name] = getattr(self, column.name)
        return dictionary
    #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
    #    return {column.name: getattr(self, column.name) for column in self.__table__.columns}
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/route')
def route():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    print(random_cafe.name)
    return jsonify(cafe=random_cafe.to_dict())
@app.route('/all')
def all():
    reslut = db.session.execute(db.select(Cafe))
    all_cafes  = reslut.scalars().all()
    all_cafes_json = []
    for cafe in all_cafes:
        all_cafes_json.append(cafe.to_dict())
    return jsonify( {
        'cafes' : all_cafes_json})
    #OR short form return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
@app.route('/search')
def search():
    query_location = request.args.get("loc")
    cafe_all = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars().all()
    if cafe_all:
        return jsonify(cafes = [cafe.to_dict() for cafe in cafe_all])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404
# HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(
        name = request.form.get('name'),
        map_url = request.form.get('map_url'),
        img_url = request.form.get('img_url'),
        location = request.form.get('location'),
        seats = request.form.get('seats'),
        has_toilet = request.form.get('has_toilet'),
        has_wifi = request.form.get('has_wifi'),
        has_sockets = request.form.get('has_sockets'), 
        can_take_calls = request.form.get('can_take_calls'),
        coffee_price = request.form.get('coffee_price')
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={'success':'Successfuly added new cafe'})

# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    
    new_prce = request.args.get('new_price')
    cafe = db.get_or_404(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = new_prce 
        db.session.commit()
        return jsonify(response={'success':'Successfully price has been updated'}),200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}),404
# HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>',methods=['DELETE'])
def delete(cafe_id):
    api_key = request.args.get('api_key')
    if api_key == "TopSecretAPIKey":
        try:
            cafe = db.get_or_404(Cafe, cafe_id)
        except Exception as e:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}),404
        else:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={'success':'Successfully has been deleted'}),200
    else:
        return jsonify(error={"Method Not Allowed":"Sorry, you have wrong api-key"}),405

if __name__ == '__main__':
    app.run(debug=True)
