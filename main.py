from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///favorite-movie-10.db' # 데이터베이스 이름
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

##CREATE TABLE 테이블 만들기
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'

db.create_all()


all_movies =[]

@app.route("/")
def home():
    # 처음을 위한 row commit
    # new_movie = Movie(title="Phone Booth", year=2002,
    #                   description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #                   rating=7.3, ranking=10, review="My favourite character was the caller.",
    #                   img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")  # 기본키 필드는 선택사항
    # db.session.add(new_movie)
    # db.session.commit()
    all_movies = db.session.query(Movie).order_by(Movie.rating.desc()).all()

    # 순위 업데이트
    for movie in all_movies:
        movie_ranking = all_movies[0::].index(movie) #현재 인덱스값
        print(movie_ranking)
        movie.ranking = movie_ranking + 1
    db.session.commit()
    return render_template("index.html",all_movies = all_movies)

class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

@app.route("/edit", methods=["GET","POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id") #get id 획득
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit(): # form에서 완료 버튼을 클릭시
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete", methods=["GET"])
def delete():
    movie_id = request.args.get("id") #get id 획득
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))  # hoem으로 redirect

class AddMovieForm(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add Movie")


@app.route("/add",methods=["GET","POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit(): # form에서 완료 버튼을 클릭시
        print(form.title.data)
        # db.session.add(new_movie)
        # db.session.commit()
        request_url = f"https://api.themoviedb.org/3/search/movie?api_key=331a34bc45846eebf207590ad05ecfef&language=en-US&query={form.title.data}&page=1&include_adult=false"
        r = requests.get(request_url)
        result = r.json()
        print(result)
        return render_template("select.html",result = result['results'])
    return render_template("add.html",form=form)  # hoem으로 redirect

@app.route("/getDetail",methods=["GET"])
def getDetail():
    movie_id = request.args.get("id")  # get id 획득
    req_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=331a34bc45846eebf207590ad05ecfef&language=en-US"
    r = requests.get(req_url).json()
    print(r)
    MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
    new_movie = Movie(title=r['title'], img_url=f"{MOVIE_DB_IMAGE_URL}{r['poster_path']}",
                    year=r['release_date'].split("-")[0],description=r['overview'])  # 기본키 필드는 선택사항
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('rate_movie',id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
