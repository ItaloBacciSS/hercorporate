import sqlite3

conn = sqlite3.connect("hercorporate.db", check_same_thread=False)
cursor = conn.cursor()

# Tabela de usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
''')
conn.commit()

# Funções básicas
def registrar_usuario(nome, email, senha):
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def validar_login(email, senha):
    cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
    return cursor.fetchone()

def buscar_usuario_por_id(usuario_id):
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (usuario_id,))
    return cursor.fetchone()

# =========================
# TABELA DE PROGRESSO POR MÓDULO
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS progresso_modulo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    modulo INTEGER NOT NULL,
    nota REAL NOT NULL,
    aprovado INTEGER NOT NULL,
    UNIQUE(usuario_id, modulo)
)
""")
conn.commit()


# =========================
# SALVAR / ATUALIZAR NOTA DO MÓDULO
# =========================
def salvar_progresso_modulo(usuario_id, modulo, nota):
    aprovado = 1 if nota >= 60 else 0

    cursor.execute("""
    INSERT INTO progresso_modulo (usuario_id, modulo, nota, aprovado)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(usuario_id, modulo)
    DO UPDATE SET nota=?, aprovado=?
    """, (usuario_id, modulo, nota, aprovado, nota, aprovado))

    conn.commit()


# =========================
# VERIFICAR SE MÓDULO ESTÁ APROVADO
# =========================
def modulo_aprovado(usuario_id, modulo):
    cursor.execute("""
    SELECT aprovado FROM progresso_modulo
    WHERE usuario_id=? AND modulo=?
    """, (usuario_id, modulo))

    resultado = cursor.fetchone()
    return resultado and resultado[0] == 1

# =========================
# BUSCAR MÓDULOS APROVADOS
# =========================
def modulos_aprovados(usuario_id):
    cursor.execute("""
    SELECT modulo FROM progresso_modulo
    WHERE usuario_id=? AND aprovado=1
    """, (usuario_id,))
    
    return [row[0] for row in cursor.fetchall()]

