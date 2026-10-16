from flask import Flask,Blueprint,send_file,request
from mega import Mega
imega=Mega()
imega.login("tonyjacobk@gmail.com","Seemu@2002")
show_bp=Blueprint("show",__name__)

@show_bp.route("/<tag>")
def view_pdf(tag):
    print(request.full_path)
    finalpath="https://mega.co.nz/#!"+tag
    print("Downloading from",finalpath)
    imega.download_url(finalpath)
    print("Download success")
    return send_file(
        '/tmp/sample.pdf',
        mimetype='application/pdf',
        as_attachment=False  # Important: allows inline viewing
    )


