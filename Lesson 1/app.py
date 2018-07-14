from flask import Flask

# Create a new Flask instance
app = Flask(__name__)

# Create the default route -> www.domain.com points to this route
@app.route('/')
def index():
    return "This is the homepage"

@app.route('/test')
def test():
    return "This is a test page"

if __name__ == '__main__':
    app.run()