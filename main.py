from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

from forms import UpdateMovieForm, AddMovieForm

MOVIE_DB_API_KEY = "646681ac2df80bca84d09de6cbfb4267"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMG_URL = "https://image.tmdb.org/t/p/original/"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_DATABASE_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()
app.app_context().push()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = UpdateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)

    if form.validate_on_submit():
        rating = form.rating.data
        review = form.review.data
        movie.rating = rating
        movie.review = review
        db.session.commit()
        print(f"MOVIE, '{movie.title}', HAS BEEN UPDATED!!!")
        return redirect(url_for('home'))
    return render_template("update_movie.html", movie=movie, form=form)


@app.route('/delete_movie', methods=["GET"])
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/add', methods=["GET", "POST"])
def add_movie():
    form = AddMovieForm()

    if form.validate_on_submit():
        movie_name = form.name.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_name})
        movie_data = response.json()["results"]
        print(movie_name)
        print(movie_data)
        return render_template("select.html", movie_data=movie_data, )

    return render_template("add.html", form=form)


@app.route('/find_movie')
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            description = data["overview"],
            img_url=f"{MOVIE_DB_IMG_URL}{data['poster_path']}",
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
