from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pricing')
def pricing():
    return render_template('pricing.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
@app.route('/register')
def signup():
    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/products')
def products():
    return render_template('products.html')


@app.route('/orders')
def orders():
    return render_template('orders.html')


@app.route('/import')
def import_page():
    return render_template('import.html')


@app.route('/scraper')
def scraper():
    return render_template('scraper.html')


@app.route('/settings')
def settings():
    return render_template('settings.html')


if __name__ == '__main__':
    app.run(debug=True)
