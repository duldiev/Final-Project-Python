from flask import render_template, url_for, flash, redirect, jsonify, request, make_response
from flaskblog import app
from flaskblog.forms import CheckForm, RegistrationForm, LoginForm
from flaskblog.models import Articles, Users
from flaskblog import db
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from transformers import pipeline
import requests
import jwt
import datetime
from functools import wraps


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        new_user = Users(f'{form.username.data}', f'{form.email.data}', f'{form.password.data}', f'')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return '<h1>Hello, token is missing </h1>', 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return '<h1>Hello, Could not verify the token</h1>', 403

        return f(*args, **kwargs)

    return decorated


@app.route("/unprotected")
def unprotected():
    return '<h1>Hello, this page viewed by anyone</h1>'


@app.route("/protected")
@token_required
def protected():
    return '<h1>Hello, token which is provided is correct</h1>'


@app.route('/coin', methods=['GET', 'POST'])
@token_required
def coin():
    form = CheckForm()

    headerArr = []
    paragraphArr = []

    if form.validate_on_submit():
        # Scrapper

        cryptoName = (str(form.crypto_name.data)).lower()

        url = 'https://coinmarketcap.com/currencies/' + cryptoName + '/news/'

        driver = webdriver.Firefox()
        driver.get(url)

        page = driver.page_source
        page_soup = soup(page, 'html.parser')

        exists = check(cryptoName)

        headers = page_soup.findAll("h3", {"class": "sc-1q9q90x-0 gEZmSc"})
        paragraphs = []
        links = page_soup.findAll("a", {"class": "svowul-0 jMBbOf cmc-link"}, href=True)

        summarizer = pipeline("summarization")

        for url_row in links:
            coinmarket = False

            url_temp = "https://coinmarketcap.com"
            if url_row['href'][0] == '/':
                url_temp += url_row['href']
                coinmarket = True
            else:
                url_temp = url_row['href']

            r = requests.get(url_temp)
            soup1 = soup(r.text, 'html.parser')

            if coinmarket:
                results = soup1.find_all(['h2', 'p'])
            else:
                results = soup1.find_all(['h1', 'p'])
            
            text = [result.text for result in results]

            ARTICLE = ' '.join(text)
            max_chunk = 500

            ARTICLE = ARTICLE.replace('.', '.<eos>')
            ARTICLE = ARTICLE.replace('?', '?<eos>')
            ARTICLE = ARTICLE.replace('!', '!<eos>')

            sentences = ARTICLE.split('<eos>')
            current_chunk = 0
            chunks = []
            for sentence in sentences:
                if len(chunks) == current_chunk + 1:
                    if len(chunks[current_chunk]) + len(sentence.split(' ')) <= max_chunk:
                        chunks[current_chunk].extend(sentence.split(' '))
                    else:
                        current_chunk += 1
                        chunks.append(sentence.split(' '))
                else:
                    print(current_chunk)
                    chunks.append(sentence.split(' '))

            for chunk_id in range(len(chunks)):
                chunks[chunk_id] = ' '.join(chunks[chunk_id])

            res = summarizer(chunks, max_length=120, min_length=30, do_sample=False)

            text = ' '.join([summ['summary_text'] for summ in res])

            paragraphs.append(text)


        for i in range(0, min(len(headers), len(paragraphs))):
            header = headers[i].text.strip()
            paragraph = paragraphs[i].strip()

            if not exists and len(header) > 0 and len(paragraph) > 0:
                new_article = Articles(f'{cryptoName}', f'{header}', f'{paragraph}')
                db.session.add(new_article)
                db.session.commit()

        for row in db.session.query(Articles).filter_by(crypto_name=cryptoName):
            headerArr.append(row.header)
            paragraphArr.append(row.paragraph)

        if len(headerArr) != 0:
            flash(f'Successfully pulled {form.crypto_name.data}!', 'success')
        else:
            flash(f'Couldn\'t find {form.crypto_name.data}!', 'warning')

    return render_template('coin.html', title='Check', form=form, headerArr=headerArr, paragraphArr=paragraphArr)


def check(cryptoName):
    for row in db.session.query(Articles).filter_by(crypto_name=cryptoName):
        if row.crypto_name == cryptoName:
            return True
    return False


@app.route("/login")
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = Users.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if auth and auth.password == user.password:
        token = jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                           app.config['SECRET_KEY'])
        user = Users.query.filter_by(username=auth.username).first()
        user.token = token
        db.session.commit()
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login required'})