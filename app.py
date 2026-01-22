import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# Configuração Base
st.set_page_config(page_title="ALT Contracting - Invoice System", layout="wide")

# --- DADOS FIXOS DA EMPRESA ---
COMPANY_DATA = {
    "name": "ALT CONTRACTING",
    "web": "www.alt-contracting.ca",
    "phone": "647 865 8176 - Toronto ON",
    "tax_id": "GST/HST: 79688 3338 Evaldo Alberto Althoff",
    "email": "e.alt.contracting@gmail.com",
    "user": "Evaldo A. Althoff"
}

st.title(f"📄 {COMPANY_DATA['name']} - Invoice System")

# --- LÓGICA DO SERIAL NUMBER (Ano/Mês - Sequencial) ---
current_year_month = datetime.now().strftime("%Y/%m")
serial_suffix = st.text_input("Número Sequencial", "001")
invoice_number = f"{current_year_month}-{serial_suffix}"

# --- CAMPOS DO CLIENTE ---
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name")
    client_addr = st.text_area("Client Address (Endereço do Cliente)")
with col2:
    invoice_date = st.date_input("Date of Issue", datetime.now())

# Campo Destacado: Endereço do Trabalho
st.markdown("""
    <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px;">
        <strong>WORK ADDRESS (Endereço do Trabalho)</strong>
    </div>
    """, unsafe_allow_html=True)
work_address = st.text_input("", placeholder="Digite o endereço onde o serviço foi prestado...")

# --- TABELA DE SERVIÇOS (APENAS INGLÊS) ---
st.subheader("Services")
if 'rows' not in st.session_state:
    st.session_state.rows = [{"Description": "", "Price ($CAD)": 0.0, "SQFT": 0, "Time (Hours)": 0}]

df_input = pd.DataFrame(st.session_state.rows)
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# Cálculo da Tabela: Preço x (SQFT ou Horas)
# Nota: Aqui o sistema multiplica pelo que for maior que zero para gerar o subtotal por linha
def calculate_row_total(row):
    if row['SQFT'] > 0:
        return row['Price ($CAD)'] * row['SQFT']
    return row['Price ($CAD)'] * row['Time (Hours)']

edited_df['Subtotal'] = edited_df.apply(calculate_row_total, axis=1)

# --- TOTAIS E IMPOSTOS ---
subtotal_geral = edited_df['Subtotal'].sum()
hst_tax = subtotal_geral * 0.13
total_final = subtotal_geral + hst_tax

c_a, c_b = st.columns([2,1])
with c_b:
    st.write(f"**Subtotal:** ${subtotal_geral:,.2f}")
    st.write(f"**HST (13%):** ${hst_tax:,.2f}")
    st.write(f"### TOTAL DUE: ${total_final:,.2f}")
    st.caption(COMPANY_DATA['tax_id'])

# --- INSTRUÇÕES FINAIS ---
st.subheader("Instructions & Warranty")
instructions = st.text_area("Final orientations, comments, work warranty (Max 5 lines)", height=100)

# --- RODAPÉ DE ASSINATURA ---
st.markdown("---")
st.write(f"✍️ __________________________________")
st.write(f"**{COMPANY_DATA['user']}**")
st.write(COMPANY_DATA['email'])

# --- HISTÓRICO E RELATÓRIOS ---
st.sidebar.header("Management / Gestão")
if st.sidebar.checkbox("Show History & Annual Report"):
    st.header("Annual Report / Relatório Anual")
    
    # Simulação de base de dados (CSV)
    if os.path.exists("history.csv"):
        hist_df = pd.read_csv("history.csv")
        
        # Filtro de Status com cores usando dataframe style
        def color_status(val):
            color = 'green' if val == 'Paid' else 'red'
            return f'color: {color}'
        
        st.dataframe(hist_df.style.applymap(color_status, subset=['Status']))
        
        # Botão para baixar relatório anual
        st.download_button("Download Annual Report (CSV)", hist_df.to_csv(), "report.csv")
    else:
        st.info("No records found yet.")

# Botão para Salvar no Histórico (Teste de Lógica)
if st.button("Save Invoice Data"):
    status_options = ["Paid", "Unpaid", "Overdue"]
    new_entry = pd.DataFrame([[invoice_number, invoice_date, client_name, total_final, "Unpaid"]], 
                             columns=["Invoice #", "Date", "Client", "Total", "Status"])
    new_entry.to_csv("history.csv", mode='a', header=not os.path.exists("history.csv"), index=False)
    st.success("Data saved to history!")
