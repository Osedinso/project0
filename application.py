import os
from flask import Flask, session, request, render_template, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import json

app= Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "GET":
    		if session.get("user"):
    			return render_template("index.html",session=session["user"])
    		return render_template('index.html')
    else:
    	un=request.form.get("un")
    	pw=request.form.get("pw")
    	data=db.execute("SELECT * from users where username=:username and password=:password",
    		{"username":un, "password":pw}).fetchall()
    	if not data:
    		return render_template("index.html", msg="Username/Password does not match")
    	else:
    		print(data)
    		session["user"]=data[0][0]
    		return render_template("index.html")
@app.route("/signup", methods=["GET","POST"])
def signup():
	if request.method == "GET":
		return render_template("signup.html")
	else:
		un=request.form.get("un")
		pw=request.form.get("pw")
		data=[]
		data.db.content("SELECT * from users where username=:username",
			{"username":un}).fetchall()
		if not data:
			db.execute("INSERT INTO users (username,password) VALUES (:username,:password)",
				{"username": un, "password": pw })
			db.commit()
			data.db.execute("SELECT * from users where username=:username and password=:password",
				{"username":un , "password":pw}).fetchall()
			session["user"]=data[0][0]
			return render_template ("index.html",session=session['user'])
		else:
			return render_template("signup.html", msg="Username already taken")
@app.route("/search", methods = ['GET', 'POST'])
def search():
	if request.method == "GET":
		return render_template("search.html")
	else:
		title= request.form.get("title")
		data=[]
		if title:
		    ti=db.execute("SELECT * from books where title like :title",
		   		{"title":"%"+title+"%"}).fetchall()
		    data.append(ti)
		else:
		    return render_template("search.html", dat=data)	
		
		   	
@app.route("/review/<bid>", methods=['GET','POST'])
def review(bid):
	if request.method== 'GET':
		return render_template("review.html", bid=bid)
	else:
		rating =request.form.get('rating')
		review =request.form.get('review')
		uid=session["user"]

		revdata=db.execute("SELECT * from review where uid=:uid and bid=:bid",
			{"uid":uid, "bid":bid}).fetchall()
		if revdata:
			return render_template('review.html', msg="Review already submitted")
		else:
			db.execute("INSERT INTO review{uid, bid, rating, review} VALUES{:uid, :bid, :rating, :review}",
			{"uid":uid, "bid":bid, "rating":rating, "review":review} )
			db.commit()
			return render_template('review.html', msg= "Review submitted successfully")
@app.route("/booksinfo/<bid>")
def bookinfo(bid):
	book=db.execute("SELECT * from books where id=:bid",
		{"bid":bid}).fetchall()
	revs=db.execute("SELECT * from review where bid=:bid",
		{"bid":bid}).fetchall()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params= {"key": " x80noZgDU3grXWl0FYTgw", "isbns":""})
	if res.status_code == 200:
		receive=res.json()
		ar=receive["books"][0]["average_rating"]
		rc=receive["books"][0]["work_ratings_count"]
	if not revs:
		return render_template('bookinfo.html', book=book, msg="No review found",ar=ar, rc=rc)
		return render_template('bookinfo.html', ar=ar, rc=rc, book=book )
		
@app.route("/logout")
def logout():
	session.pop('user')
	return render_template('index.html', msg="Logged out successfully")

@app.route("/api/<isbn>")
def api(isbn):
	isb=db.execute("SELECT * from books where isbn like :isbn",
		{"isbn":"%"+isbn+"%"}).fetchall()
	data={}
	data['title']=isb[0][2]
	data['year']=isb[0][4]
	data['author']=isb[0][3]
	data['isbn']=isbn
	data['review_count']=len(isb)
	bid=db.execute("SELECT id from books where isbn=:isbn",
		{"isbn":isbn}).fetchall()
	val=db.execute("SELECT avg(rating) from review where bid=:bid",
		{"bid":bid[0][0]}).fetchall()
	data['average_score']=val[0][0]
	return render_template('response.html', dat=data)




