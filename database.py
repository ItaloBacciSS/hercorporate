import os
import psycopg2

# =========================
# CONEXÃO COM POSTGRES (Render)
# =========================
def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


# =========================
# CRIAÇÃO DAS TABELAS
# =========================
def criar_tabelas():
    conn = get_connection()
    cur = conn.cursor()

    # Tabela de usuários
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );
    """)

    # Progresso por módulo
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progresso_modulo (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            modulo INTEGER NOT NULL,
            nota REAL NOT NULL,
            aprovado BOOLEAN NOT NULL,
            UNIQUE (usuario_id, modulo)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# =========================
# USUÁRIOS
# =========================
def registrar_usuario(nome, email, senha):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (%s, %s, %s)
        """, (nome, email, senha))

        conn.commit()
        return True

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False

    finally:
        cur.close()
        conn.close()


def validar_login(email, senha):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome FROM usuarios
        WHERE email=%s AND senha=%s
    """, (email, senha))

    usuario = cur.fetchone()
    cur.close()
    conn.close()

    return usuario


# =========================
# PROGRESSO DO MÓDULO
# =========================
def salvar_progresso_modulo(usuario_id, modulo, nota):
    aprovado = nota >= 60

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO progresso_modulo (usuario_id, modulo, nota, aprovado)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (usuario_id, modulo)
        DO UPDATE SET nota=%s, aprovado=%s
    """, (usuario_id, modulo, nota, aprovado, nota, aprovado))

    conn.commit()
    cur.close()
    conn.close()


def modulos_aprovados(usuario_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT modulo FROM progresso_modulo
        WHERE usuario_id=%s AND aprovado=true
    """, (usuario_id,))

    modulos = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return modulos
