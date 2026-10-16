from flask import Flask, render_template, request, redirect, url_for,Blueprint 
import pymysql
from aiven import connect
nse_bp=Blueprint("nse",__name__)

def get_db_connection():
    return connect()

@nse_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM codes")
    codes = cursor.fetchall()
    print (codes)
    cursor.close()
    conn.close()
    return render_template('codeindex.html', codes=codes)

@nse_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        company = request.form['company']
        code = request.form['code']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO codes (company, code) VALUES (%s, %s)", (company, code))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('nse.index'))
    return render_template('add.html')

@nse_bp.route('/edit/<code>', methods=['GET', 'POST'])
def edit(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        company = request.form['company']
        code = request.form['code']
        cursor.execute("UPDATE codes SET company = %s  WHERE code = %s", (company, code))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('nse.index'))
    cursor.execute("SELECT * FROM codes WHERE code = %s", (code,))
    company = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit.html', company=company)

@nse_bp.route('/delete/<code>')
def delete(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM codes WHERE code = %s", (code,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('nse.index'))

