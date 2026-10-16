from flask import Flask
from myapp import report_bp
from nsecodes import nse_bp
from server import bhav_bp
from report_crud import crud_bp
from sector import sector_bp
from show import show_bp
app = Flask(__name__)
app.register_blueprint(report_bp)
app.register_blueprint(bhav_bp)
app.register_blueprint(nse_bp,url_prefix="/code")
app.register_blueprint(crud_bp,url_prefix="/crud")
app.register_blueprint(sector_bp,url_prefix="/sector")
app.register_blueprint(show_bp,url_prefix="/show")



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)


