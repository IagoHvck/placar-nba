import streamlit as st
import json
import os
import pandas as pd
from itertools import combinations

st.set_page_config(page_title="Placar NBA", page_icon="🏀", layout="wide")

jogadores = ["Iago", "Luiz", "Seco", "Big", "Iagu", "Guga"]
ARQUIVO_DADOS = "dados_placar.json"

# --- FUNÇÕES DE DADOS ---
def inicializar_dados():
    estatisticas = {j: {"Partidas": 0, "V": 0, "D": 0} for j in jogadores}
    confrontos = {f"{j1} vs {j2}": [0, 0] for j1, j2 in combinations(jogadores, 2)}
    return estatisticas, confrontos

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS) and os.path.getsize(ARQUIVO_DADOS) > 0:
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return dados["estatisticas"], dados["confrontos_diretos"]
        except:
            pass
    return inicializar_dados()

def salvar_dados(estatisticas, confrontos_diretos):
    dados = {"estatisticas": estatisticas, "confrontos_diretos": confrontos_diretos}
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

estatisticas, confrontos_diretos = carregar_dados()

# --- INTERFACE DO SITE ---
st.title("🏀 Registro de Partidas NBA")

st.markdown("### Registrar Resultado")

col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    j1 = st.selectbox("Jogador 1", jogadores)
    vitoria_j1 = st.button("🏆 Venceu", key="v1", use_container_width=True)

with col2:
    st.markdown("<h2 style='text-align: center; margin-top: 25px;'>VS</h2>", unsafe_allow_html=True)

with col3:
    j2 = st.selectbox("Jogador 2", jogadores)
    vitoria_j2 = st.button("🏆 Venceu", key="v2", use_container_width=True)

vencedor = None
perdedor = None

if vitoria_j1:
    vencedor, perdedor = j1, j2
elif vitoria_j2:
    vencedor, perdedor = j2, j1

if vencedor and perdedor:
    if vencedor == perdedor:
        st.warning("⚠️ Um jogador não pode jogar contra ele mesmo!")
    else:
        # Atualiza Geral
        estatisticas[vencedor]["Partidas"] += 1
        estatisticas[vencedor]["V"] += 1
        estatisticas[perdedor]["Partidas"] += 1
        estatisticas[perdedor]["D"] += 1
        
        # Atualiza Confrontos
        chave1 = f"{vencedor} vs {perdedor}"
        chave2 = f"{perdedor} vs {vencedor}"
        
        if chave1 in confrontos_diretos:
            confrontos_diretos[chave1][0] += 1
        elif chave2 in confrontos_diretos:
            confrontos_diretos[chave2][1] += 1
            
        salvar_dados(estatisticas, confrontos_diretos)
        st.success(f"✅ Vitória de {vencedor} sobre {perdedor} registrada!")
        st.rerun() # Atualiza a página instantaneamente para exibir a tabela nova

st.divider()

# --- TABELAS ---
col_geral, col_confrontos = st.columns(2)

with col_geral:
    st.markdown("### 📊 Classificação Geral")
    df_geral = pd.DataFrame.from_dict(estatisticas, orient='index').reset_index()
    df_geral.columns = ["Jogador", "Partidas", "V", "D"]
    df_geral = df_geral.sort_values(by="V", ascending=False).reset_index(drop=True)
    st.dataframe(df_geral, use_container_width=True, hide_index=True)

with col_confrontos:
    st.markdown("### ⚔️ Confrontos Diretos")
    dados_confrontos = []
    for chave, placar in confrontos_diretos.items():
        if placar[0] > 0 or placar[1] > 0: # Só mostra quem já jogou
            jogadorA, jogadorB = chave.split(" vs ")
            dados_confrontos.append({
                "Confronto": f"{jogadorA} x {jogadorB}",
                "Placar Histórico": f"{placar[0]} x {placar[1]}"
            })
    
    if dados_confrontos:
        df_confrontos = pd.DataFrame(dados_confrontos)
        st.dataframe(df_confrontos, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum confronto registrado ainda.")