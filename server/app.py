from flask import Flask

def create_app():
    app = Flask(__name__)
    # Your configuration and routes here
    return app

# Remove the import, just call the function directly
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')