import streamlit as st
from datetime import date
import pandas as pd
import urllib.parse

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Barbearia Inova V3.0", layout="wide")

# Estilo para deixar mais profissional (Cores escuras e limpas)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2E2E2E; color: white; }
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
for chave in ['vendas', 'fidelidade', 'checkins', 'avaliacoes', 'estoque']:
    if chave not in st.session_state:
        if chave == 'estoque':
            st.session_state[chave] = {"Pomada": 10, "Gilete": 50}
        elif chave == 'fidelidade': st.session_state[chave] = {}
        else: st.session_state[chave] = []

if 'logado' not in st.session_state: st.session_state['logado'] = False

# --- DADOS FIXOS ---
PRECOS = {"Corte": 40.0, "Barba": 30.0, "Combo": 60.0, "Sobrancelha": 15.0, "Pezinho": 10.0}
BARBEIROS = {"Pedro": "👤", "Felipe": "✂️"}
HORARIOS = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]

def iniciar_app():
    st.sidebar.title("💈 INOVA V3.0")
    menu = ["🏠 Início", "📱 Área do Cliente", "🪑 Caixa do Barbeiro", "📊 Painel ADM"]
    escolha = st.sidebar.selectbox("Ir para:", menu)

    if escolha == "🏠 Início":
        st.title("✂️ Barbearia Inova")
        st.info("🎁 A cada 10 cortes, o 11º é GRÁTIS!")
        c1, c2 = st.columns(2)
        c1.metric("Barbeiro", "Pedro", "Online")
        c2.metric("Barbeiro", "Felipe", "Online")
        st.divider()
        st.subheader("Tabela de Preços")
        for s, v in PRECOS.items(): st.write(f"**{s}**: R$ {v:.2f}")

    elif escolha == "📱 Área do Cliente":
        st.title("📱 Agendamento Online")
        t1, t2 = st.tabs(["📅 Novo Agendamento", "⭐ Avaliar"])
        
        with t1:
            nome_cliente = st.text_input("Seu Nome")
            tel_cliente = st.text_input("Seu WhatsApp (com DDD)")
            col_b, col_h = st.columns(2)
            barbeiro_p = col_b.selectbox("Barbeiro:", list(BARBEIROS.keys()))
            hora_p = col_h.selectbox("Horário:", HORARIOS)
            servs = st.multiselect("Serviços:", list(PRECOS.keys()))
            
            if servs:
                total = sum(PRECOS[s] for s in servs)
                pts = st.session_state['fidelidade'].get(tel_cliente, 0)
                valor_f = 0.0 if pts >= 10 else total * 0.95
                
                st.write(f"### Total: R$ {valor_f:.2f}")
                
                if st.button("Confirmar Horário"):
                    if nome_cliente and tel_cliente:
                        # Salva no sistema
                        st.session_state['checkins'].append({
                            "data": str(date.today()), "hora": hora_p, "cliente": nome_cliente, 
                            "tel": tel_cliente, "barbeiro": barbeiro_p, "servico": ", ".join(servs), "valor": valor_f
                        })
                        
                        # GERAR LINK DO WHATSAPP (Profissional)
                        msg = f"Olá {barbeiro_p}! Agendei um {', '.join(servs)} para as {hora_p} hoje. Nome: {nome_cliente}"
                        link_zap = f"https://wa.me/5599999999999?text={urllib.parse.quote(msg)}" # Substitua pelo seu número
                        
                        st.success(f"Agendado para {hora_p}!")
                        st.markdown(f"[✅ Clique aqui para avisar no WhatsApp]({link_zap})")
                    else: st.error("Preencha Nome e WhatsApp!")

        with t2:
            st.subheader("Avalie nosso serviço")
            nota = st.select_slider("Nota:", options=[1, 2, 3], value=3)
            obs = st.text_area("O que podemos melhorar?")
            if st.button("Enviar Avaliação"):
                st.session_state['avaliacoes'].append({"data": str(date.today()), "nota": nota, "obs": obs})
                st.success("Obrigado!")

    elif escolha == "🪑 Caixa do Barbeiro":
        st.title("🪑 Lançamento de Atendimento")
        if not st.session_state['logado']:
            u = st.selectbox("Barbeiro:", list(BARBEIROS.keys()))
            if st.text_input("Senha", type="password") == "123":
                if st.button("Entrar"):
                    st.session_state.update({'logado': True, 'user': u})
                    st.rerun()
        else:
            st.info(f"Logado como: {st.session_state['user']}")
            serv_caixa = st.multiselect("Serviços:", list(PRECOS.keys()))
            metodo = st.selectbox("Pagamento:", ["Pix", "Dinheiro", "Cartão"])
            if serv_caixa:
                total_l = sum(PRECOS[s] for s in serv_caixa) * 0.95
                if st.button(f"Finalizar Venda (R$ {total_l:.2f})"):
                    st.session_state['vendas'].append({
                        "data": str(date.today()), "barbeiro": st.session_state['user'], 
                        "valor": total_l, "pagamento": metodo, "comissao": total_l * 0.5
                    })
                    st.success("Venda registrada!")
            if st.button("Sair"):
                st.session_state['logado'] = False
                st.rerun()

    elif escolha == "📊 Painel ADM":
        if st.text_input("Senha ADM", type="password") == "123":
            aba1, aba2, aba3 = st.tabs(["📅 Agenda", "💰 Finanças", "📦 Estoque"])
            
            with aba1:
                for i, c in enumerate(st.session_state['checkins']):
                    st.write(f"⏰ {c['hora']} - {c['cliente']} ({c['servico']})")
                    if st.button("Confirmar", key=f"c_{i}"):
                        st.session_state['fidelidade'][c['tel']] = st.session_state['fidelidade'].get(c['tel'], 0) + 1
                        st.session_state['vendas'].append(c)
                        st.session_state['checkins'].pop(i)
                        st.rerun()

            with aba2:
                if st.session_state['vendas']:
                    df = pd.DataFrame(st.session_state['vendas'])
                    st.metric("Faturamento", f"R$ {df['valor'].sum():.2f}")
                    st.dataframe(df)
            
            with aba3:
                for item, qtd in st.session_state['estoque'].items():
                    st.session_state['estoque'][item] = st.number_input(f"Qtd {item}", value=qtd)

if __name__ == "__main__":
    iniciar_app()