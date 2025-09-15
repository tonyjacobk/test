from flask import Flask
from webby import bp
#from nsecodes import nse_bp
#from report_crud import crud_bp
app = Flask(__name__)
app.register_blueprint(bp)
#app.register_blueprint(nse_bp,url_prefix="/code")
#app.register_blueprint(crud_bp,url_prefix="/crud")





if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


