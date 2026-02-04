from flask import Flask

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the homepage ('/')
@app.route('/')
def hello_world():
    return 'Hello, World! This is my first Flask app.'

# Run the application if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True) 