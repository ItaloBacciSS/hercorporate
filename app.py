from flask import Flask, render_template, request, redirect, session, jsonify
from database import (
    registrar_usuario,
    validar_login,
    salvar_progresso_modulo,
    modulos_aprovados,
    criar_tabelas
)

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# cria tabelas no startup
criar_tabelas()

# ---------------- ROTAS ---------------- #

@app.route("/")
def home():
    return render_template(
        "home.html",
        usuario_logado="usuario_id" in session
    )

@app.route("/sobre")
def sobre():
    return render_template(
        "sobre.html",
        usuario_logado="usuario_id" in session
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = validar_login(email, senha)
        if usuario:
            session["usuario_id"] = usuario[0]
            return redirect("/")
        else:
            return render_template("login.html", erro="Email ou senha incorretos")

    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        if registrar_usuario(nome, email, senha):
            usuario = validar_login(email, senha)
            session["usuario_id"] = usuario[0]
            return redirect("/")
        else:
            return render_template("registro.html", erro="Email já cadastrado")

    return render_template("registro.html")

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    return redirect("/login")

@app.route("/curso")
def curso():
    if "usuario_id" not in session:
        return redirect("/login")

    usuario_id = session["usuario_id"]
    aprovados = modulos_aprovados(usuario_id)

    return render_template(
        "curso.html",
        modulos_aprovados=aprovados
    )

# =========================
# SALVAR RESULTADO DO QUESTIONÁRIO
# =========================
@app.route("/salvar-progresso-modulo", methods=["POST"])
def salvar_progresso_modulo_route():
    if "usuario_id" not in session:
        return jsonify({"erro": "não autenticado"}), 403

    dados = request.json
    usuario_id = session["usuario_id"]
    modulo = dados["modulo"]
    nota = dados["nota"]

    salvar_progresso_modulo(usuario_id, modulo, nota)

    aprovado = nota >= 60

    return jsonify({
        "aprovado": aprovado,
        "proximo_modulo": modulo + 1 if aprovado else None
    })

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
