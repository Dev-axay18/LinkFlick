from flask import Flask, request, jsonify, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import random
import string

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for storing URLs
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

# Helper function to generate a random short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Home route to render the frontend HTML
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint to create a shortened URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "No URL provided"}), 400

    # Generate a unique short URL code
    while True:
        short_code = generate_short_code()
        if not URL.query.filter_by(short_url=short_code).first():
            break

    # Save the original and short URLs to the database
    new_url = URL(original_url=original_url, short_url=short_code)
    db.session.add(new_url)
    db.session.commit()

    # Return the full shortened URL as JSON
    short_url = request.host_url + short_code
    return jsonify({"short_url": short_url})

# Endpoint to handle redirection using the short URL
@app.route('/<short_code>')
def redirect_to_url(short_code):
    url = URL.query.filter_by(short_url=short_code).first_or_404()
    return redirect(url.original_url)

# Initialize database and create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
