from flask import Flask, render_template, request, redirect, session, jsonify
from database import (
    registrar_usuario,
    validar_login,
    salvar_progresso_modulo,
    modulos_aprovados,
    criar_tabelas,
    buscar_usuario_por_id,
    get_connection
)
import os

# -----------------------------
# Configuração da aplicação
# -----------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave_fallback_insegura")

try:
    criar_tabelas()
except Exception as e:
    print(f"Erro ao criar tabelas: {e}")


# -----------------------------
# Rotas principais
# -----------------------------
@app.route("/")
def home():
    usuario = None
    if "usuario_id" in session:
        usuario = buscar_usuario_por_id(session["usuario_id"])
    return render_template("home.html", usuario=usuario)


@app.route("/sobre")
def sobre():
    usuario = None
    if "usuario_id" in session:
        usuario = buscar_usuario_por_id(session["usuario_id"])
    return render_template("sobre.html", usuario=usuario)


# -----------------------------
# Autenticação
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
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
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
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


# -----------------------------
# Curso e progresso
# -----------------------------
@app.route("/curso")
def curso():
    if "usuario_id" not in session:
        return redirect("/login")

    usuario_id = session["usuario_id"]
    aprovados = modulos_aprovados(usuario_id)
    usuario = buscar_usuario_por_id(usuario_id)

    # Buscar respostas salvas do módulo atual
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT modulo, respostas, aprovado FROM progresso_modulo WHERE usuario_id=%s",
        (usuario_id,)
    )
    progresso = cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "curso.html",
        modulos_aprovados=aprovados,
        usuario=usuario,
        progresso=progresso
    )


@app.route("/salvar-progresso-modulo", methods=["POST"])
def salvar_progresso_modulo_route():
    if "usuario_id" not in session:
        return jsonify({"erro": "não autenticado"}), 403

    dados = request.json
    usuario_id = session["usuario_id"]
    modulo = dados.get("modulo")
    nota = dados.get("nota")
    respostas = dados.get("respostas")

    sucesso = salvar_progresso_modulo(usuario_id, modulo, nota, respostas)

    if not sucesso:
        return jsonify({"erro": "módulo já aprovado, não pode alterar"}), 403

    aprovado = nota >= 60
    return jsonify({
        "aprovado": aprovado,
        "proximo_modulo": modulo + 1 if aprovado else None
    })


# -----------------------------
# Inicialização
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
