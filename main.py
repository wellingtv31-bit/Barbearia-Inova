import streamlit as st
from datetime import date
import pandas as pd
import csv
from io import StringIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Barbearia Inova V3.0", layout="wide")

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
for chave in ['vendas', 'fidelidade', 'checkins', 'avaliacoes', 'estoque']:
    if chave not in st.session_state:
        if chave == 'estoque':
            st.session_state[chave] = {"Pomada": 10, "Gilete": 50, "Cerveja": 24}
        elif chave == 'fidelidade':
            st.session_state[chave] = {}
        else:
            st.session_state[chave] = []

if 'logado' not in st.session_state: st.session_state['logado'] = False

# --- DADOS FIXOS ---
PRECOS = {"Corte": 40.0, "Barba": 30.0, "Combo": 60.0, "Sobrancelha": 15.0, "Pezinho": 10.0}
BARBEIROS = {"Pedro": "👤", "Felipe": "✂️"}
HORARIOS = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
COMISSAO_PERCENTUAL = 0.50 

def iniciar_app():
    st.sidebar.title("💈 INOVA V3.0")
    menu = ["🏠 Início", "📱 Área do Cliente", "🪑 Caixa do Barbeiro", "📊 Painel ADM"]
    escolha = st.sidebar.selectbox("Ir para:", menu)

    if escolha == "🏠 Início":
        st.title("✂️ Barbearia Inova")
        st.subheader("Nossa Equipe")
        c1, c2 = st.columns(2)
        c1.metric("Barbeiro", "Pedro", "Disponível")
        c2.metric("Barbeiro", "Felipe", "Disponível")
        st.divider()
        st.subheader("Tabela de Preços")
        for s, v in PRECOS.items(): st.write(f"**{s}**: R$ {v:.2f}")

    elif escolha == "📱 Área do Cliente":
        st.title("📱 Agendamento Online")
        t1, t2 = st.tabs(["📅 Novo Agendamento", "⭐ Avaliar"])
        with t1:
            nome = st.text_input("Seu Nome")
            tel = st.text_input("Seu WhatsApp")
            col_b, col_h = st.columns(2)
            barbeiro_p = col_b.selectbox("Escolha o Barbeiro:", list(BARBEIROS.keys()))
            hora_p = col_h.selectbox("Escolha o Horário:", HORARIOS)
            servs = st.multiselect("Serviços:", list(PRECOS.keys()))
            if servs:
                total = sum(PRECOS[s] for s in servs)
                pts = st.session_state['fidelidade'].get(tel, 0)
                valor_f = 0.0 if pts >= 10 else total * 0.95
                if st.button("Confirmar Horário"):
                    if nome and tel:
                        st.session_state['checkins'].append({
                            "data": str(date.today()), "hora": hora_p, "cliente": nome, 
                            "tel": tel, "barbeiro": barbeiro_p, "servico": ", ".join(servs), "valor": valor_f
                        })
                        st.success(f"Reservado para {hora_p} com {barbeiro_p}!")

        with t2:
            st.subheader("Sua opinião vale muito!")
            nota = st.select_slider("Nota:", options=[1, 2, 3], value=3)
            obs = st.text_area("O que podemos melhorar?")
            if st.button("Enviar Avaliação"):
                st.session_state['avaliacoes'].append({"data": str(date.today()), "nota": nota, "obs": obs})
                st.success("Obrigado!")

    elif escolha == "🪑 Caixa do Barbeiro":
        st.title("🪑 Lançamento de Atendimento")
        if not st.session_state['logado']:
            u = st.selectbox("Quem está lançando?", list(BARBEIROS.keys()))
            if st.text_input("Senha", type="password") == "123":
                if st.button("Entrar"):
                    st.session_state.update({'logado': True, 'user': u})
                    st.rerun()
        else:
            st.info(f"Barbeiro: {st.session_state['user']} {BARBEIROS[st.session_state['user']]}")
            serv_caixa = st.multiselect("Serviços Realizados:", list(PRECOS.keys()))
            metodo = st.selectbox("Pagamento:", ["Pix", "Dinheiro", "Cartão"])
            if serv_caixa:
                total_liquido = sum(PRECOS[s] for s in serv_caixa) * 0.95
                st.subheader(f"Total com 5% OFF: R$ {total_liquido:.2f}")
                if st.button("Finalizar Venda"):
                    st.session_state['vendas'].append({
                        "data": str(date.today()), "barbeiro": st.session_state['user'], 
                        "valor": total_liquido, "pagamento": metodo, "comissao": total_liquido * COMISSAO_PERCENTUAL
                    })
                    st.success("Venda registrada!")
            if st.button("Sair"):
                st.session_state['logado'] = False
                st.rerun()

    elif escolha == "📊 Painel ADM":
        if st.text_input("Senha ADM", type="password") == "123":
            aba1, aba2, aba3, aba4 = st.tabs(["📅 Agenda", "💰 Comissão", "📦 Estoque", "⭐ Feedback"])
            with aba1:
                st.subheader("Próximos Clientes")
                for i, c in enumerate(st.session_state['checkins']):
                    st.write(f"⏰ {c['hora']} - **{c['cliente']}** com {c['barbeiro']}")
                    if st.button("Confirmar Presença", key=f"c_{i}"):
                        st.session_state['fidelidade'][c['tel']] = st.session_state['fidelidade'].get(c['tel'], 0) + 1
                        st.session_state['vendas'].append(c)
                        st.session_state['checkins'].pop(i)
                        st.rerun()

            with aba2:
                st.subheader("Relatório de Ganhos")
                if st.session_state['vendas']:
                    for b in BARBEIROS.keys():
                        vendas_b = [v['valor'] for v in st.session_state['vendas'] if v.get('barbeiro') == b]
                        total_b = sum(vendas_b)
                        st.write(f"**{b}**: Total R$ {total_b:.2f} | Comissão (50%): **R$ {total_b * 0.5:.2f}**")
                    st.metric("Faturamento Total", f"R$ {sum(v['valor'] for v in st.session_state['vendas']):.2f}")

            with aba3:
                st.subheader("Controle de Materiais")
                for item, qtd in st.session_state['estoque'].items():
                    nova_qtd = st.number_input(f"Quantidade de {item}", value=qtd, key=f"est_{item}")
                    st.session_state['estoque'][item] = nova_qtd
                if st.button("Atualizar Estoque"): st.success("Estoque salvo!")

            with aba4:
                for av in st.session_state['avaliacoes']:
                    st.write(f"{'⭐' * av['nota']} | {av['obs']}")

if __name__ == "__main__":
    iniciar_app()