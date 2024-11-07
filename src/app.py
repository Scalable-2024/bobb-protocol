from flask import Flask
from src.routers.__main__ import router  # Import the router

app = Flask(__name__)

# Register the router
app.register_blueprint(router)

if __name__ == "__main__":
    app.run(debug=True)
