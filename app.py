from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from time import time

# Use a service account
cred = credentials.Certificate('abelblog-a9344-firebase-adminsdk-iigv9-316eac934e.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)

@app.route('/')
def index():
    posts_ref = db.collection(u'posts')
    query = posts_ref.order_by(u'epoch_time', direction=firestore.Query.DESCENDING).limit(15)
    posts_raw = posts_ref.stream()

    posts = []
    for post in posts_raw:
        temp = post.to_dict()
        temp['id'] = post.id
        posts.append(temp)

    print(posts)

    return render_template('index.html', login='userID' in request.cookies, posts=posts)

@app.route('/admin-login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if request.form['pwd'] == 'AbelDiress@secure.9928025668':
            resp = make_response(render_template('login.html', login=login))
            resp.set_cookie('userID', request.form['pwd'])
            
            return resp
        else:
            return jsonify({'error': 'Incorrect password, stupid'})
    
    return render_template('login.html', login='userID' in request.cookies)

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == "POST":
        db.collection(u'posts').add(
            {
                u'title': request.form['title'],
                u'body': request.form['body'],
                u'time': datetime.now().time().__str__(),
                u'date': datetime.now().date().__str__(),
                u'epoch_time': time()
            }
        )
        return redirect(url_for('index'))
    if 'userID' not in request.cookies:
        return redirect(url_for('login'))

    return render_template('post.html')

@app.route('/delete/<string:id>', methods=['POST'])
def delete(id):
    if 'userID' not in request.cookies:
        return jsonify({'error': 'Unauthorized to delete post.'})

    try:
        db.collection(u'posts').document(id).delete()
    except:
        return jsonify({'error': 'Unable to delete post, please try again later.'})
    
    return jsonify({'success': 'Post deleted.'})

if __name__ == '__main__':
    app.run(debug=False)