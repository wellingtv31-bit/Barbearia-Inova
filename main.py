import streamlit as st
from datetime import date
import csv
from io import StringIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Barbearia Inova - V2.0", layout="wide")

# Inicialização do Banco de Dados Interno
if 'vendas' not in st.session_state: st.session_state['vendas'] = []
if 'fidelidade' not in st.session_state: st.session_state['fidelidade'] = {}
if 'checkins' not in st.session_state: st.session_state['checkins'] = []
if 'avaliacoes' not in st.session_state: st.session_state['avaliacoes'] = [] # Novo: Armazenar avaliações

PRECOS = {"Corte": 25.0, "Barba": 15.0, "Combo assinatura mensal aparti ": 75.0, "Sobrancelha": 10.0, "Pezinho": 10.0}
BARBEIROS = ["Pedro", "Felipe"]

def iniciar_app():
    st.sidebar.title("💈 INOVA 2.0")
    menu = ["🏠 Início", "📱 Cliente", "🪑 Barbeiro", "📊 Painel ADM"]
    escolha = st.sidebar.selectbox("Menu", menu)

    if escolha == "🏠 Início":
        st.title("✂️ Barbearia Inova")
        st.info("🎁 Novidade: Escolha seu barbeiro e avalie nosso serviço!")
        for s, v in PRECOS.items(): st.write(f"*{s}*: R$ {v:.2f}")

    elif escolha == "📱 Cliente":
        st.title("📱 Agendamento & Avaliação")
        
        tab_age, tab_aval = st.tabs(["📅 Agendar", "⭐ Avaliar Serviço"])
        
        with tab_age:
            nome = st.text_input("Nome")
            tel = st.text_input("WhatsApp")
            # --- NOVO: SELEÇÃO DE BARBEIRO ---
            barbeiro_pref = st.selectbox("Escolha seu Barbeiro:", BARBEIROS)
            servs = st.multiselect("Serviços:", list(PRECOS.keys()))
            
            if servs:
                total = sum(PRECOS[s] for s in servs)
                pts = st.session_state['fidelidade'].get(tel, 0)
                valor_final = 0.0 if pts >= 10 else total * 0.95
                
                if st.button("Confirmar Agendamento"):
                    st.session_state['checkins'].append({
                        "data": str(date.today()), "cliente": nome, "tel": tel, 
                        "barbeiro": barbeiro_pref, "servico": ", ".join(servs), "valor": valor_final
                    })
                    st.success(f"Agendado com {barbeiro_pref}!")

        with tab_aval:
            st.subheader("O que achou do atendimento?")
            # --- NOVO: AVALIAÇÃO 3 ESTRELAS ---
            nota = st.select_slider("Sua nota:", options=[1, 2, 3], value=3)
            # --- NOVO: OBSERVAÇÕES ---
            obs = st.text_area("O que podemos melhorar no local?")
            
            if st.button("Enviar Feedback"):
                st.session_state['avaliacoes'].append({
                    "data": str(date.today()), "nota": nota, "observacao": obs
                })
                st.balloons()
                st.success("Obrigado pelo seu feedback!")

    elif escolha == "🪑 Barbeiro":
        st.title("🪑 Caixa")
        if st.text_input("Senha", type="password") == "123":
            barbeiro = st.selectbox("Barbeiro:", BARBEIROS)
            serv_caixa = st.multiselect("Serviços:", list(PRECOS.keys()))
            if st.button("Lançar"):
                total_c = sum(PRECOS[s] for s in serv_caixa) * 0.95
                st.session_state['vendas'].append({"data": str(date.today()), "barbeiro": barbeiro, "valor": total_c})
                st.success("Venda salva!")

    elif escolha == "📊 Painel ADM":
        if st.text_input("Senha ADM", type="password") == "123":
            aba1, aba2, aba3 = st.tabs(["📅 Agendamentos", "📈 Relatório", "⭐ Feedbacks"])
            
            with aba1:
                for i, c in enumerate(st.session_state['checkins']):
                    st.write(f"{c['cliente']} -> {c['barbeiro']} ({c['servico']})")
                    if st.button("Confirmar", key=i):
                        st.session_state['fidelidade'][c['tel']] = st.session_state['fidelidade'].get(c['tel'], 0) + 1
                        st.session_state['vendas'].append(c)
                        st.session_state['checkins'].pop(i)
                        st.rerun()

            with aba2:
                st.metric("Total", f"R$ {sum(v['valor'] for v in st.session_state['vendas']):.2f}")

            with aba3:
                # --- NOVO: VISUALIZAÇÃO DE FEEDBACK NO ADM ---
                for av in st.session_state['avaliacoes']:
                    st.write(f"📅 {av['data']} | Nota: {'⭐' * av['nota']} | Obs: {av['observacao']}")

if __name__ == "__main__":
    iniciar_app()
