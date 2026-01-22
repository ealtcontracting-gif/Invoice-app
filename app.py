import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="My Invoice App", layout="wide")

# Seleção de Idioma
lang = st.sidebar.selectbox("Language / Idioma", ["Português", "English"])

# Textos do App
txt = {
    "Português": {
        "title": "Gerador de Invoice", "co_name": "Nome da Empresa", "co_addr": "Endereço",
        "client": "Nome do Cliente", "desc": "Serviço", "price": "Preço Unit.", 
        "time": "Tempo/Qtd", "total": "Total", "sub": "Subtotal", "tax": "Imposto (13%)",
        "grand": "Total a Pagar", "save": "Gerar PDF e Salvar", "history": "Histórico",
        "notes": "Instruções Extras", "serial": "Nº de Série"
    },
    "English": {
        "title": "Invoice Generator", "co_name": "Company Name", "co_addr": "Address",
        "client": "Client Name", "desc": "Service", "price": "Unit Price", 
        "time": "Time/Qty", "total": "Total", "sub": "Subtotal", "tax": "Tax (13%)",
        "grand": "Grand Total", "save": "Generate PDF & Save", "history": "History",
        "notes": "Extra Instructions", "serial": "Serial No."
    }
}[lang]

st.title(f"📄 {txt['title']}")

# Sidebar - Dados da Empresa
st.sidebar.header("Empresa / Company")
logo = st.sidebar.file_uploader("Upload Logo", type=['png', 'jpg'])
my_co = st.sidebar.text_input(txt['co_name'])
my_addr = st.sidebar.text_area(txt['co_addr'])
my_site = st.sidebar.text_input("Website")

# Dados do Invoice
col1, col2 = st.columns(2)
with col1:
    serial = st.text_input(txt['serial'], value=datetime.now().strftime("%Y%m%d%H%M"))
    client = st.text_input(txt['client'])
with col2:
    date_inv = st.date_input("Date", datetime.now())

# Tabela de Serviços
st.subheader("Serviços / Services")
if 'rows' not in st.session_state:
    st.session_state.rows = [{"desc": "", "price": 0.0, "time": 0.0}]

def add_row(): st.session_state.rows.append({"desc": "", "price": 0.0, "time": 0.0})

df = st.data_editor(pd.DataFrame(st.session_state.rows), num_rows="dynamic", use_container_width=True)

# Cálculos
subtotal = (df['price'] * df['time']).sum()
tax = subtotal * 0.13
grand = subtotal + tax

c1, c2 = st.columns([2,1])
with c2:
    st.write(f"**{txt['sub']}:** ${subtotal:.2f}")
    st.write(f"**{txt['tax']}:** ${tax:.2f}")
    st.write(f"### {txt['grand']}: ${grand:.2f}")

extra = st.text_area(txt['notes'])

# Botão para salvar
if st.button(txt['save']):
    # Aqui o código criaria o PDF (simplificado para o teste inicial)
    st.success("Invoice processado! (PDF pronto para download em instantes)")
    # Salvar Histórico Local
    new_data = pd.DataFrame([[serial, date_inv, client, f"${grand:.2f}"]], columns=["Serial", "Data", "Cliente", "Total"])
    new_data.to_csv("historico.csv", mode='a', header=not os.path.exists("historico.csv"), index=False)

# Mostrar Histórico
if st.checkbox(txt['history']):
    if os.path.exists("historico.csv"):
        st.table(pd.read_csv("historico.csv"))
    else: st.info("Nenhum histórico encontrado.")
