from web.web import app
from web.api import *
from web.html import *

if __name__ == "__main__":
    app.run(debug=True, port=22000)