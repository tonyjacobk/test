from flask import Flask, send_file
from megclass import MegaMan
app = Flask(__name__)
def read_the_file(path):
    finalpath="https://mega.co.nz/"+path
    MegaMan.mega.download_url(finalpath,dest_filename="sample.pdf")

@app.route('/view/<pdf_path>')
def view_pdf(pdf_path):
    print("PDFpathi is",pdf_path)
    # Replace 'sample.pdf' with the path to your PDF file
    read_the_file(pdf_path)
    return send_file(
        'sample.pdf',
        mimetype='application/pdf',
        as_attachment=False  # Important: allows inline viewing
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    MegaMan.download("https://mega.co.nz/#!jJ1WlShL!zaAL5B3dUwEel5omg4ExHZF01NIl2Oa5pEaT0aM4ypg",sample.pdf) 
