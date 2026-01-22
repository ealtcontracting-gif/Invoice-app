import streamlit as st
import pandas as pd
from fpdf import FPDF
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
col_s1, col_s2 = st.columns([1, 3])
with col_s1:
    serial_num = st.text_input("Serial Sequence", "001")
    invoice_no = f"{current_ym}-{serial_num}"
with col_s2:
    st.write(f"**Invoice Number:** {invoice_no}")

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name")
    client_addr = st.text_area("Client Address")
with col2:
    invoice_date = st.date_input("Issue Date", datetime.now())

# --- SEÇÃO JOBSITE ---
st.markdown("### **JOBSITE**")
jobsite_addr = st.text_input("Enter the jobsite address below:", key="jobsite")

st.markdown("---")

# --- TABELA DE SERVIÇOS ---
st.subheader("Services")

# Inicialização da tabela se não existir
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"Description": "", "Price": 0.00, "SQFT": 0, "Time (h)": 0}
    ])

# Editor da Tabela
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Description": st.column_config.TextColumn("Description", width="large"),
        "Price": st.column_config.NumberColumn("Price ($)", format="%.2f"),
        "SQFT": st.column_config.NumberColumn("SQFT", min_value=0, max_value=60000),
        "Time (h)": st.column_config.NumberColumn("Time (h)", min_value=0, max_value=999),
    }
)

# --- LÓGICA DE CÁLCULO POR LINHA ---
def calculate_subtotal(row):
    # Se tiver SQFT, prioriza Preço x SQFT. Se não, faz Preço x Time.
    if row['SQFT'] > 0:
        return row['Price'] * row['SQFT']
    else:
        return row['Price'] * row['Time (h)']

# Aplica o cálculo e cria a 5ª coluna que você pediu
edited_df['Line Subtotal'] = edited_df.apply(calculate_subtotal, axis=1)

# Mostrar a tabela com o Subtotal para conferência
st.dataframe(edited_df, use_container_width=True)

# --- CÁLCULOS FINAIS ---
subtotal_total = edited_df['Line Subtotal'].sum()
hst_value = subtotal_total * 0.13
grand_total = subtotal_total + hst_value

col_a, col_b = st.columns([2,1])
with col_b:
    st.markdown(f"**Subtotal:** ${subtotal_total:,.2f}")
    st.markdown(f"**HST (13%):** ${hst_value:,.2f}")
    st.markdown(f"## **TOTAL DUE: ${grand_total:,.2f}**")
    st.caption(COMPANY['tax_id'])

# --- INSTRUÇÕES ---
st.subheader("Instructions & Warranty")
notes = st.text_area("Final orientations, comments, warranty (Max 5 lines)", height=120)

# --- ASSINATURA ---
st.markdown("---")
st.write("✍️ __________________________________")
st.write(f"**{COMPANY['user']}**")
st.write(COMPANY['email'])

# --- SALVAR NO HISTÓRICO ---
if st.button("Save to History"):
    history_file = "history.csv"
    new_record = pd.DataFrame([{
        "Invoice #": invoice_no,
        "Date": invoice_date,
        "Client": client_name,
        "Total": f"{grand_total:.2f}",
        "Status": "Unpaid",
        "Sent via": "Pending"
    }])
    new_record.to_csv(history_file, mode='a', header=not os.path.exists(history_file), index=False)
    st.success("Invoice saved successfully!")

# --- VISUALIZAR RELATÓRIO ---
if st.sidebar.checkbox("View Management Report"):
    st.header("Annual & Period Report")
    if os.path.exists("history.csv"):
        h_df = pd.read_csv("history.csv")
        st.table(h_df)
    else:
        st.info("No records found.")
