import streamlit as st
from datetime import date
import csv
from io import StringIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Barbearia Inova - Gestão Total", layout="wide")

# Inicialização do Banco de Dados Interno
for chave in ['vendas', 'fidelidade', 'checkins', 'despesas']:
    if chave not in st.session_state:
        st.session_state[chave] = {} if chave == 'fidelidade' else []

if 'logado' not in st.session_state: st.session_state['logado'] = False

# TABELA DE SERVIÇOS
SERVICOS = {
    "Corte Masculino": 25.0,
    "Barba": 15.0,
    "Combo (Corte + Barba)": 60.0,
    "Sobrancelha": 15.0,
    "Pezinho": 10.0,
    "Pigmentação": 20.0,
    "Corte Kids": 35.0,
    "Luzes / Reflexo": 80.0
}

def iniciar_app():
    st.sidebar.title("💈 INOVA")
    menu = ["🏠 Início", "📱 Área do Cliente", "🪑 Caixa do Barbeiro", "📊 Painel ADM"]
    escolha = st.sidebar.selectbox("Menu", menu)

    # --- TELA INICIAL ---
    if escolha == "🏠 Início":
        st.title("✂️ Barbearia Inova")
        st.info("🎁 Promoção: 5% OFF em todos os serviços e o 11º é por nossa conta!")
        st.subheader("Nossos Serviços")
        for s, v in SERVICOS.items(): st.write(f"*{s}*: R$ {v:.2f}")

    # --- ÁREA DO CLIENTE (Múltiplas Opções) ---
    elif escolha == "📱 Área do Cliente":
        st.title("📱 Agendamento e Fidelidade")
        nome = st.text_input("Seu Nome")
        tel = st.text_input("Seu WhatsApp (Somente números)")
        
        servicos_cliente = st.multiselect("Selecione os serviços desejados:", list(SERVICOS.keys()))
        
        if servicos_cliente:
            total_bruto = sum(SERVICOS[s] for s in servicos_cliente)
            pts = st.session_state['fidelidade'].get(tel, 0)
            
            if pts >= 10:
                st.warning("🎉 PARABÉNS! Você completou 10 serviços. Este agendamento é GRÁTIS!")
                valor_final = 0.0
            else:
                valor_final = total_bruto * 0.95
                st.success(f"Total Bruto: R$ {total_bruto:.2f} | Com 5% OFF: R$ {valor_final:.2f}")

            if st.button("Confirmar Agendamento"):
                if nome and tel:
                    st.session_state['checkins'].append({
                        "data": str(date.today()), "cliente": nome, "tel": tel, 
                        "servico": ", ".join(servicos_cliente), "valor": valor_final
                    })
                    st.balloons()
                    st.success("Agendamento realizado! Apresente-se ao barbeiro.")
                else: st.error("Preencha seu nome e telefone.")

    # --- ÁREA DO BARBEIRO (Com Desconto Automático) ---
    elif escolha == "🪑 Caixa do Barbeiro":
        st.title("🪑 Lançamento de Caixa")
        if not st.session_state['logado']:
            u = st.text_input("Barbeiro").lower()
            if st.text_input("Senha", type="password") == "123":
                if st.button("Entrar"):
                    st.session_state.update({'logado': True, 'user': u})
                    st.rerun()
        else:
            st.write(f"Operador: *{st.session_state['user'].upper()}*")
            
            lista_clientes = ["Cliente de Balcão"] + list(set([c['cliente'] for c in st.session_state['checkins']]))
            cliente_ref = st.selectbox("Vincular a qual cliente?", lista_clientes)
            
            serv_marcados = st.multiselect("Serviços prestados:", list(SERVICOS.keys()))
            
            if serv_marcados:
                total_bruto_caixa = sum(SERVICOS[s] for s in serv_marcados)
                total_com_desconto = total_bruto_caixa * 0.95 # DESCONTO AUTOMÁTICO DE 5%
                
                st.subheader(f"Total a Receber: R$ {total_com_desconto:.2f}")
                st.caption(f"(Valor original R$ {total_bruto_caixa:.2f} - 5% de desconto aplicado)")
                
                p_metodo = st.selectbox("Pagamento:", ["Dinheiro", "Pix", "Cartão"])
                
                if st.button("Finalizar Atendimento"):
                    st.session_state['vendas'].append({
                        "data": str(date.today()), "barbeiro": st.session_state['user'], 
                        "cliente": cliente_ref, "servico": ", ".join(serv_marcados), 
                        "valor": total_com_desconto, "pagamento": p_metodo
                    })
                    st.success("Venda finalizada com desconto de 5%!")
            
            if st.button("Sair"):
                st.session_state['logado'] = False
                st.rerun()

    # --- PAINEL ADM ---
    elif escolha == "📊 Painel ADM":
        if st.text_input("Senha Mestra", type="password") == "123":
            aba_age, aba_fid, aba_fin = st.tabs(["📅 Agendamentos", "🎖️ Controle Fidelidade", "💸 Financeiro"])
            
            with aba_age:
                st.subheader("Clientes que agendaram hoje")
                if not st.session_state['checkins']: st.write("Ninguém agendado ainda.")
                for i, c in enumerate(st.session_state['checkins']):
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"*{c['cliente']}* - {c['servico']} (Valor: R$ {c['valor']:.2f})")
                    if col2.button("Confirmar Presença", key=f"age_{i}"):
                        # Adiciona ponto
                        if c['valor'] > 0:
                            st.session_state['fidelidade'][c['tel']] = st.session_state['fidelidade'].get(c['tel'], 0) + 1
                        else:
                            st.session_state['fidelidade'][c['tel']] = 0 # Reseta o cartão
                        
                        st.session_state['vendas'].append(c)
                        st.session_state['checkins'].pop(i)
                        st.rerun()

            with aba_fid:
                st.subheader("Ranking de Fidelidade")
                if not st.session_state['fidelidade']: st.write("Nenhum cliente pontuou ainda.")
                for tel, pts in st.session_state['fidelidade'].items():
                    progresso = pts / 10
                    st.write(f"📱 *Tel: {tel}* | Serviços realizados: *{pts}*")
                    st.progress(progresso if progresso <= 1.0 else 1.0)
                    if pts >= 10: st.success("✅ Este cliente já pode ganhar o serviço grátis!")

            with aba_fin:
                total_total = sum(v['valor'] for v in st.session_state['vendas'])
                st.metric("Faturamento Acumulado", f"R$ {total_total:.2f}")
                
                if st.session_state['vendas']:
                    output = StringIO()
                    writer = csv.DictWriter(output, fieldnames=["data", "barbeiro", "cliente", "servico", "valor", "pagamento", "tel"])
                    writer.writeheader()
                    for v in st.session_state['vendas']:
                        writer.writerow({k: v.get(k, "") for k in ["data", "barbeiro", "cliente", "servico", "valor", "pagamento", "tel"]})
                    st.download_button("📥 Baixar Planilha de Vendas", data=output.getvalue(), file_name=f"vendas_inova_{date.today()}.csv")

if __name__ == "__main__":
    iniciar_app()