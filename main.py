import streamlit as st
from datetime import date
import pandas as pd
import urllib.parse

# --- CONFIGURAÇÃO VISUAL PREMIUM ---
st.set_page_config(page_title="Inova Pro", page_icon="✂️", layout="wide")

st.markdown("""
    <style>
    /* Estilização Geral */
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1e1e1e;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .stMetric {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 15px;
        padding: 20px;
    }
    /* Cartão de Serviço */
    .service-card {
        background-color: #1c2128;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #d4af37;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
for chave in ['vendas', 'fidelidade', 'checkins', 'avaliacoes', 'estoque']:
    if chave not in st.session_state:
        if chave == 'estoque': st.session_state[chave] = {"Pomada": 10, "Gilete": 50}
        elif chave == 'fidelidade': st.session_state[chave] = {}
        else: st.session_state[chave] = []

if 'logado' not in st.session_state: st.session_state['logado'] = False

# --- DADOS ---
PRECOS = {"Corte": 40.0, "Barba": 30.0, "Combo": 60.0, "Sobrancelha": 15.0, "Pezinho": 10.0}
BARBEIROS = {"Pedro": "👨🏻‍🚀", "Felipe": "👨🏻‍🎨"}
HORARIOS = [f"{h:02d}:00" for h in range(8, 19) if h != 12]

# --- APP ---
def iniciar_app():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1154/1154564.png", width=100)
    st.sidebar.title("INOVA PRO")
    menu = st.sidebar.radio("Navegação", ["🏠 Home", "📅 Agendar", "💰 Caixa", "📊 Gestão"])

    # --- HOME ---
    if menu == "🏠 Home":
        st.title("💈 Barbearia Inova")
        st.subheader("Escolha seu profissional favorito")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='service-card'><h3>{BARBEIROS['Pedro']} Pedro</h3><p>Especialista em Degradê</p></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='service-card'><h3>{BARBEIROS['Felipe']} Felipe</h3><p>Mestre da Barba</p></div>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📋 Tabela de Serviços")
        cols = st.columns(len(PRECOS))
        for i, (serv, preco) in enumerate(PRECOS.items()):
            cols[i].metric(serv, f"R$ {preco}")

    # --- AGENDAR ---
    elif menu == "📅 Agendar":
        st.title("📅 Reserva de Horário")
        with st.container():
            nome = st.text_input("Nome completo")
            whatsapp = st.text_input("WhatsApp (ex: 62999999999)")
            
            col1, col2 = st.columns(2)
            barbeiro = col1.selectbox("Profissional", list(BARBEIROS.keys()))
            hora = col2.selectbox("Horário disponível", HORARIOS)
            
            servicos = st.multiselect("Selecione os serviços", list(PRECOS.keys()))
            
            if servicos:
                total = sum(PRECOS[s] for s in servicos)
                # Fidelidade
                pts = st.session_state['fidelidade'].get(whatsapp, 0)
                valor_final = 0.0 if pts >= 10 else total * 0.95
                
                if pts >= 10: st.warning("✨ PARABÉNS! Este corte é por nossa conta!")
                else: st.info(f"Total com 5% de desconto App: **R$ {valor_final:.2f}**")
                
                if st.button("🚀 Confirmar Agendamento"):
                    if nome and whatsapp:
                        st.session_state['checkins'].append({
                            "data": str(date.today()), "hora": hora, "cliente": nome, 
                            "tel": whatsapp, "barbeiro": barbeiro, "servico": ", ".join(servicos), "valor": valor_final
                        })
                        # Mensagem WhatsApp
                        texto_zap = urllib.parse.quote(f"Olá! Agendei um {', '.join(servicos)} às {hora} com {barbeiro}. Nome: {nome}")
                        st.success("Agendado com sucesso!")
                        st.markdown(f"[📲 Clique aqui para confirmar no WhatsApp](https://wa.me/55{whatsapp}?text={texto_zap})")
                    else: st.error("Por favor, preencha todos os campos.")

    # --- CAIXA ---
    elif menu == "💰 Caixa":
        st.title("💰 Lançamento de Caixa")
        if not st.session_state['logado']:
            user = st.selectbox("Barbeiro", list(BARBEIROS.keys()))
            senha = st.text_input("Senha", type="password")
            if st.button("Acessar"):
                if senha == "123":
                    st.session_state.update({'logado': True, 'user': user})
                    st.rerun()
        else:
            st.success(f"Logado: {st.session_state['user']}")
            serv_caixa = st.multiselect("Serviços prestados", list(PRECOS.keys()))
            pag = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão"])
            
            if serv_caixa:
                total_c = sum(PRECOS[s] for s in serv_caixa) * 0.95
                if st.button(f"Finalizar Atendimento (R$ {total_c:.2f})"):
                    st.session_state['vendas'].append({
                        "data": str(date.today()), "barbeiro": st.session_state['user'], 
                        "valor": total_c, "pagamento": pag
                    })
                    st.success("Venda registrada!")
            
            if st.button("Deslogar"):
                st.session_state['logado'] = False
                st.rerun()

    # --- GESTÃO ---
    elif menu == "📊 Gestão":
        st.title("📊 Painel Administrativo")
        if st.text_input("Senha ADM", type="password") == "123":
            t_age, t_fin, t_feed = st.tabs(["📅 Agenda", "💵 Financeiro", "⭐ Feedback"])
            
            with t_age:
                if not st.session_state['checkins']: st.write("Agenda vazia.")
                for i, c in enumerate(st.session_state['checkins']):
                    with st.expander(f"{c['hora']} - {c['cliente']}"):
                        st.write(f"Barbeiro: {c['barbeiro']} | {c['servico']}")
                        if st.button("Confirmar Presença e Pontuar", key=f"c_{i}"):
                            st.session_state['fidelidade'][c['tel']] = st.session_state['fidelidade'].get(c['tel'], 0) + 1
                            st.session_state['vendas'].append(c)
                            st.session_state['checkins'].pop(i)
                            st.rerun()
            
            with t_fin:
                df = pd.DataFrame(st.session_state['vendas'])
                if not df.empty:
                    st.metric("Faturamento do Dia", f"R$ {df['valor'].sum():.2f}")
                    st.dataframe(df)
                else: st.write("Nenhuma venda hoje.")

if __name__ == "__main__":
    iniciar_app()