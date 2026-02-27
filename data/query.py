from src.core.BancoDados import BancodeDados
import pandas as pd

bd = BancodeDados()

def getFundos():
    """
    Traz os fundos e os CUSTs 
    """

    query = """
        select p.id_produto, p.nome 'Fundo', a.administrador, pf.cod_custodiante from onshore.produtos p
        inner join onshore.produtos_fundos pf on pf.id_produto = p.id_produto
        inner join onshore.administradores a on a.id_administrador = pf.id_administrador
        where
        1 = 1
        and pf.id_gestor = 1
        and p.id_status = 1
        and p.ativo = 1
        and pf.cod_custodiante is not null 
        and upper(pf.cod_custodiante) like 'CUST%'
        order by p.nome
    """
    conn = bd.db_connection()
    result = bd.get_multiple_result(conn, query)
    df = pd.DataFrame(result)
    return df