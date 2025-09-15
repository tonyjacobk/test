from flask import Flask
from webby import webby_bp
from server import bhav_bp
#from nsecodes import nse_bp
#from report_crud import crud_bp
app = Flask(__name__)
app.register_blueprint(webby_bp)
app.register_blueprint(bhav_bp)
#app.register_blueprint(nse_bp,url_prefix="/code")
#app.register_blueprint(crud_bp,url_prefix="/crud")





if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


