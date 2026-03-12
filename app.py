from flask import Flask, render_template, request, redirect
from flask import session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "segredo_super_seguro"

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/funcionarios", methods=["GET","POST"])
def funcionarios():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    areas = conn.execute("SELECT * FROM areas").fetchall()

    if request.method == "POST":
        nome = request.form["nome"]
        funcao = request.form["funcao"]
        area_id = request.form["area_id"]

        conn.execute(
            "INSERT INTO funcionarios (nome, funcao, area_id) VALUES (?,?,?)",
            (nome, funcao, area_id)
        )
        conn.commit()

    funcionarios = conn.execute("""
        SELECT f.*, a.nome as area_nome
        FROM funcionarios f
        LEFT JOIN areas a ON f.area_id = a.id
    """).fetchall()

    return render_template("funcionarios.html", funcionarios=funcionarios, areas=areas)
 

@app.route("/turnos", methods=["GET","POST"])
def turnos():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":
        nome = request.form["nome"]

        conn.execute(
            "INSERT INTO turnos (nome) VALUES (?)",
            (nome,)
        )

        conn.commit()

    turnos = conn.execute("SELECT * FROM turnos").fetchall()

    return render_template("turnos.html", turnos=turnos)

@app.route("/escala", methods=["GET","POST"])
def escala():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    areas = conn.execute("SELECT * FROM areas").fetchall()

    area_id = request.args.get("area_id")

    if area_id:
        funcionarios = conn.execute(
            "SELECT * FROM funcionarios WHERE area_id = ?", (area_id,)
        ).fetchall()
    else:
        funcionarios = []

    dias = list(range(1,32))

    # Depois de buscar funcionários:
    escala_existente = conn.execute("""
        SELECT funcionario_id, data, status FROM escala
    """).fetchall()

    # transformar em dicionário para fácil acesso no template
    escala_dict = {}
    for e in escala_existente:
        escala_dict[(e["funcionario_id"], e["data"])] = e["status"]

    return render_template(
    "escala.html",
    funcionarios=funcionarios,
    dias=dias,
    areas=areas,
    area_id=area_id,
    escala_dict=escala_dict
)


@app.route("/areas", methods=["GET","POST"])
def areas():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":
        nome = request.form["nome"]

        conn.execute(
            "INSERT INTO areas (nome) VALUES (?)",
            (nome,)
        )

        conn.commit()

    areas = conn.execute("SELECT * FROM areas").fetchall()

    return render_template("areas.html", areas=areas)

from flask import jsonify
from datetime import datetime

@app.route("/salvar_escala", methods=["POST"])
def salvar_escala():
    conn = get_db()
    data = request.form["data"]          # formato YYYY-MM-DD
    funcionario_id = request.form["funcionario_id"]
    status = request.form["status"]      # 'X' ou ''

    # Verifica se já existe registro
    existente = conn.execute(
        "SELECT id FROM escala WHERE funcionario_id=? AND data=?",
        (funcionario_id, data)
    ).fetchone()

    if existente:
        conn.execute(
            "UPDATE escala SET status=? WHERE id=?",
            (status, existente["id"])
        )
    else:
        conn.execute(
            "INSERT INTO escala (funcionario_id, data, status) VALUES (?,?,?)",
            (funcionario_id, data, status)
        )

    conn.commit()
    return jsonify({"success": True})

from flask import make_response
from weasyprint import HTML

@app.route("/escala/pdf")
def escala_pdf():

    conn = get_db()

    area_id = request.args.get("area_id")
    if area_id:
        funcionarios = conn.execute(
            "SELECT * FROM funcionarios WHERE area_id = ?", (area_id,)
        ).fetchall()
        area_nome = conn.execute("SELECT nome FROM areas WHERE id=?", (area_id,)).fetchone()["nome"]
    else:
        funcionarios = []
        area_nome = "Todas"

    dias = list(range(1,32))

    escala_existente = conn.execute("SELECT funcionario_id, data, status FROM escala").fetchall()
    escala_dict = {}
    for e in escala_existente:
        escala_dict[(e["funcionario_id"], e["data"])] = e["status"]

    # Renderiza HTML
    rendered = render_template(
        "escala_pdf.html",
        funcionarios=funcionarios,
        dias=dias,
        escala_dict=escala_dict,
        area_nome=area_nome
    )

    # Converte para PDF
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=escala_{area_nome}.pdf'
    return response

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM usuarios WHERE username=? AND password=?",
            (username,password)
        ).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["area_id"] = user["area_id"]

            return redirect("/")

        else:
            return "Login inválido"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

    
    
if __name__ == "__main__":
    app.run(debug=True)
    