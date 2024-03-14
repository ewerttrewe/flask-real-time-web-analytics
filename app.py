from flask import Flask
from flask_restful import Api
from users import UsersRegistrationView

# from flask_bcrypt import Bcrypt

app = Flask(__name__)
api = Api(app)
# flask_bcrypt = Bcrypt(api)


api.add_resource(UsersRegistrationView, "/api/users/registration")


if __name__ == "__main__":
    app.run(debug=True)
