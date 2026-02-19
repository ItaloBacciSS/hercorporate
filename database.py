import os
import psycopg2

def get_connection():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL não está definida")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return psycopg2.connect(url)

def criar_tabelas():
    conn = get_connection()
    cur = conn.cursor()

    # Usuários
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
            respostas JSONB,
            UNIQUE (usuario_id, modulo)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

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
    cur.execute("SELECT id, nome FROM usuarios WHERE email=%s AND senha=%s", (email, senha))
    usuario = cur.fetchone()
    cur.close()
    conn.close()
    return usuario

def buscar_usuario_por_id(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email FROM usuarios WHERE id=%s", (usuario_id,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()
    if usuario:
        return {"id": usuario[0], "nome": usuario[1], "email": usuario[2]}
    return None

def salvar_progresso_modulo(usuario_id, modulo, nota, respostas=None):
    aprovado = nota >= 60
    conn = get_connection()
    cur = conn.cursor()

    # transforma dict em string "q1=b;q2=c;q3=a"
    respostas_str = ";".join([f"{k}={v}" for k,v in respostas.items()]) if respostas else None

    cur.execute("""
        INSERT INTO progresso_modulo (usuario_id, modulo, nota, aprovado, respostas)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (usuario_id, modulo)
        DO UPDATE SET nota=%s, aprovado=%s, respostas=%s
    """, (usuario_id, modulo, nota, aprovado, respostas_str, nota, aprovado, respostas_str))

    conn.commit()
    cur.close()
    conn.close()
    return True


def modulos_aprovados(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT modulo FROM progresso_modulo WHERE usuario_id=%s AND aprovado=true", (usuario_id,))
    modulos = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return modulos

