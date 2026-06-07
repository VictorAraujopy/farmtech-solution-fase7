"""
FarmTech Solutions - Fase 7 | Pessoa 1
crud_operacoes.py - CRUD do manejo agricola (tabela talhoes).

As 4 operacoes (inserir, listar, atualizar, deletar) usam a conexao
central do conexao_db.py, que ja liga as chaves estrangeiras.
"""

import conexao_db as db


def inserir_talhao(cultura_id, nome, area_m2, ruas, metros_por_rua, dose_ml_por_m, litros):
    """Insere um talhao e devolve o id gerado."""
    con = db.conectar()
    cur = con.execute(
        """INSERT INTO talhoes
               (cultura_id, nome, area_m2, ruas, metros_por_rua, dose_ml_por_m, litros)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (cultura_id, nome, area_m2, ruas, metros_por_rua, dose_ml_por_m, litros),
    )
    con.commit()
    novo_id = cur.lastrowid
    con.close()
    return novo_id


def listar_talhoes():
    """Lista todos os talhoes ja com o nome da cultura (JOIN)."""
    con = db.conectar()
    linhas = con.execute(
        """SELECT t.id, c.nome AS cultura, t.nome, t.area_m2, t.litros
             FROM talhoes t
             JOIN culturas c ON c.id = t.cultura_id
         ORDER BY t.id"""
    ).fetchall()
    con.close()
    return linhas


def atualizar_talhao(talhao_id, campo, novo_valor):
    """Atualiza UM campo de um talhao.

    O nome da coluna nao pode ser parametrizado com '?', entao validamos
    contra uma lista branca para evitar SQL injection.
    """
    campos_ok = {"nome", "area_m2", "ruas", "metros_por_rua",
                 "dose_ml_por_m", "litros", "cultura_id"}
    if campo not in campos_ok:
        raise ValueError(f"Campo invalido: {campo}")

    con = db.conectar()
    con.execute(f"UPDATE talhoes SET {campo} = ? WHERE id = ?", (novo_valor, talhao_id))
    con.commit()
    con.close()


def deletar_talhao(talhao_id):
    """Remove um talhao pelo id."""
    con = db.conectar()
    con.execute("DELETE FROM talhoes WHERE id = ?", (talhao_id,))
    con.commit()
    con.close()


def _mostrar(titulo):
    print(titulo)
    for t in listar_talhoes():
        print(f"  [{t['id']}] {t['cultura']:5} | {t['nome']:18} | "
              f"area={t['area_m2']:.2f} m2 | {t['litros']:.1f} L")


if __name__ == "__main__":
    db.criar_banco()  # banco limpo para a demonstracao
    print(">> Inserindo 2 talhoes (cafe e soja)...")
    id1 = inserir_talhao(1, "Talhao Cafe Sul", 30000.0, 25, 80.0, 400.0, 800.0)
    id2 = inserir_talhao(2, "Pivo Soja 1", 17671.46, 30, 100.0, 350.0, 1050.0)

    _mostrar(">> Lista apos INSERT:")
    print(">> UPDATE: litros do talhao 1 -> 850")
    atualizar_talhao(id1, "litros", 850.0)
    print(">> DELETE: removendo o talhao 2")
    deletar_talhao(id2)
    _mostrar(">> Estado final:")
