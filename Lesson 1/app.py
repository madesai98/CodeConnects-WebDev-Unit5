from flask import Flask

# Create a new Flask instance
app = Flask(__name__)

# Create the default route -> www.domain.com points to this route
@app.route('/')
def index():
    return "This is the homepage"

# Create test route -> www.domain.com/test points to this route
@app.route('/test')
def test():
    return "This is a test page"

# Only run the web-server if app.py is run directly; don't start a web-server if it is imported into another file
if __name__ == '__main__':
    app.run()