import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página
st.set_page_config(page_title="ALT Contracting System", layout="wide")

# --- DADOS FIXOS ---
COMPANY = {
    "name": "ALT CONTRACTING",
    "web": "www.alt-contracting.ca",
    "phone": "647 865 8176 - Toronto ON",
    "tax_id": "GST/HST: 79688 3338 Evaldo Alberto Althoff",
    "email": "e.alt.contracting@gmail.com",
    "user": "Evaldo A. Althoff"
}

st.title(f"📄 {COMPANY['name']} - Invoice System")

# --- SERIAL E CLIENTE ---
current_ym = datetime.now().strftime("%Y/%m")
col_s1, col_s2 = st.columns([1, 2])
with col_s1:
    serial_num = st.text_input("Serial Sequence (Ex: 001)", "001")
    invoice_no = f"{current_ym}-{serial_num}"
with col_s2:
    st.info(f"**Current Invoice Number:** {invoice_no}")

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name")
    client_addr = st.text_area("Client Address")
with col2:
    invoice_date = st.date_input("Issue Date", datetime.now())

# --- SEÇÃO JOBSITE ---
st.markdown("### **JOBSITE**")
jobsite_addr = st.text_input("Enter the jobsite address below:", placeholder="Job location...")

st.markdown("---")

# --- TABELA DE SERVIÇOS ---
st.subheader("Services")

# Criamos uma estrutura de dados inicial limpa
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Description": "", "Price": 0.00, "SQFT": 0.0, "Time (h)": 0.0}
    ])

# Editor da Tabela configurado para aceitar números corretamente
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Description": st.column_config.TextColumn("Description", width="large"),
        "Price": st.column_config.NumberColumn("Price ($CAD)", format="%.2f", min_value=0.0),
        "SQFT": st.column_config.NumberColumn("SQFT", min_value=0.0),
        "Time (h)": st.column_config.NumberColumn("Time (h)", min_value=0.0),
    }
)

# --- LÓGICA DE CÁLCULO SEGURA ---
def calculate_safe_subtotal(row):
    # Converte para float e trata campos vazios (None/NaN) como zero
    price = float(row.get('Price', 0) or 0)
    sqft = float(row.get('SQFT', 0) or 0)
    time = float(row.get('Time (h)', 0) or 0)
    
    if sqft > 0:
        return price * sqft
    return price * time

# Calcula a coluna Subtotal sem risco de erro
edited_df['Line Subtotal'] = edited_df.apply(calculate_safe_subtotal, axis=1)

# Exibe a tabela final com os cálculos
st.dataframe(edited_df, use_container_width=True)

# --- TOTAIS ---
subtotal_geral = edited_df['Line Subtotal'].sum()
hst_value = subtotal_geral * 0.13
grand_total = subtotal_geral + hst_value

col_a, col_b = st.columns([2,1])
with col_b:
    st.write(f"**Subtotal:** ${subtotal_geral:,.2f}")
    st.write(f"**HST (13%):** ${hst_value:,.2f}")
    st.markdown(f"## **TOTAL DUE: ${grand_total:,.2f}**")
    st.caption(COMPANY['tax_id'])

# --- INSTRUÇÕES E ASSINATURA ---
st.subheader("Instructions & Warranty")
notes = st.text_area("Final orientations, comments, warranty (Max 5 lines)", height=100)

st.markdown("---")
st.write("✍️ __________________________________")
st.write(f"**{COMPANY['user']}**")
st.write(COMPANY['email'])

# --- HISTÓRICO ---
if st.button("Save to History"):
    history_file = "history.csv"
    new_record = pd.DataFrame([{
        "Invoice #": invoice_no,
        "Date": invoice_date,
        "Client": client_name,
        "Total": f"{grand_total:.2f}",
        "Status": "Unpaid"
    }])
    new_record.to_csv(history_file, mode='a', header=not os.path.exists(history_file), index=False)
    st.success("Saved!")

if st.sidebar.checkbox("View Management Report"):
    if os.path.exists("history.csv"):
        st.table(pd.read_csv("history.csv"))
    else:
        st.info("No records yet.")
