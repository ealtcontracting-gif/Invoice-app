import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os

# Configuração da página
st.set_page_config(page_title="ALT Contracting - Invoice System", layout="wide")

# --- DADOS FIXOS DA EMPRESA ---
COMPANY = {
    "name": "ALT CONTRACTING",
    "web": "www.alt-contracting.ca",
    "phone": "647 865 8176 - Toronto ON",
    "tax_id": "GST/HST: 79688 3338 Evaldo Alberto Althoff",
    "email": "e.alt.contracting@gmail.com",
    "user": "Evaldo A. Althoff"
}

# --- FUNÇÃO PARA GERAR PDF (TAMANHO LETTER) ---
def create_pdf(invoice_no, date, client_n, client_a, job_a, items, sub, hst, total, notes):
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Logo e Cabeçalho
    if os.path.exists("Alt Contracting Logo.png"):
        pdf.image("Alt Contracting Logo.png", 10, 8, 45)
    
    pdf.cell(190, 10, COMPANY["name"], ln=True, align='R')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, f"{COMPANY['web']} | {COMPANY['phone']}", ln=True, align='R')
    pdf.cell(190, 5, COMPANY['tax_id'], ln=True, align='R')
    pdf.ln(15)
    
    # Detalhes do Invoice
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, f"BILL TO:", ln=False)
    pdf.cell(95, 10, f"INVOICE #: {invoice_no}", ln=True, align='R')
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(95, 5, client_n, ln=False)
    pdf.cell(95, 5, f"Date: {date}", ln=True, align='R')
    pdf.multi_cell(95, 5, client_a)
    
    pdf.ln(5)
    # Jobsite com fundo cinza
    pdf.set_fill_color(240, 242, 246)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, f" JOBSITE: {job_a}", ln=True, fill=True)
    pdf.ln(5)
    
    # Tabela de Serviços
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(70, 8, "Description", 1, 0, 'C', True)
    pdf.cell(30, 8, "Price ($)", 1, 0, 'C', True)
    pdf.cell(30, 8, "SQFT", 1, 0, 'C', True)
    pdf.cell(30, 8, "Time (h)", 1, 0, 'C', True)
    pdf.cell(30, 8, "Subtotal", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 10)
    for index, row in items.iterrows():
        pdf.cell(70, 7, str(row['Description']), 1)
        pdf.cell(30, 7, f"{row['Price']:.2f}", 1, 0, 'C')
        pdf.cell(30, 7, str(row['SQFT']), 1, 0, 'C')
        pdf.cell(30, 7, str(row['Time']), 1, 0, 'C')
        pdf.cell(30, 7, f"{row['Subtotal']:.2f}", 1, 1, 'C')
    
    pdf.ln(5)
    # Totais
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(160, 7, "Subtotal:", 0, 0, 'R')
    pdf.cell(30, 7, f"${sub:,.2f}", 1, 1, 'C')
    pdf.cell(160, 7, "HST (13%):", 0, 0, 'R')
    pdf.cell(30, 7, f"${hst:,.2f}", 1, 1, 'C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(160, 10, "TOTAL DUE:", 0, 0, 'R')
    pdf.cell(30, 10, f"${total:,.2f}", 1, 1, 'C')
    
    # Notas e Assinatura
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(190, 5, f"Instructions & Warranty: {notes}")
    
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 5, "___________________________________________", ln=True)
    pdf.cell(190, 5, COMPANY['user'], ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, COMPANY['email'], ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
col_l, col_r = st.columns([1, 2])
with col_l:
    if os.path.exists("Alt Contracting Logo.png"):
        st.image("Alt Contracting Logo.png", width=250)
with col_r:
    st.title(COMPANY["name"])
    st.write(f"🌐 {COMPANY['web']} | 📞 {COMPANY['phone']}")
    st.write(f"📄 {COMPANY['tax_id']}")

st.markdown("---")
# (Lógica de preenchimento idêntica à anterior...)
current_ym = datetime.now().strftime("%Y/%m")
col_s1, col_s2 = st.columns([1, 2])
with col_s1:
    serial_input = st.text_input("Sequence", "001")
    invoice_no = f"{current_ym}-{serial_input}"
col_c1, col_c2 = st.columns(2)
with col_c1:
    client_name = st.text_input("Client Name")
    client_addr = st.text_area("Client Address")
with col_c2:
    invoice_date = st.date_input("Issue Date", datetime.now())
    jobsite_addr = st.text_input("Jobsite:")

# Tabela Editor (Oculta no PDF)
with st.expander("Clique aqui para preencher os serviços", expanded=True):
    if 'items' not in st.session_state:
        st.session_state.items = pd.DataFrame([{"Description": "", "Price": 0.00, "SQFT": 0, "Time": 0}])
    edited_items = st.data_editor(st.session_state.items, num_rows="dynamic", use_container_width=True)

def calculate_row(row):
    p, s, t = float(row['Price'] or 0), float(row['SQFT'] or 0), float(row['Time'] or 0)
    return p * s if s > 0 else p * t

edited_items['Subtotal'] = edited_items.apply(calculate_row, axis=1)

# Resumo na Tela
st.subheader("Preview Services")
st.dataframe(edited_items, use_container_width=True, hide_index=True)

# Totais
subtotal_total = edited_items['Subtotal'].sum()
hst_13 = subtotal_total * 0.13
total_final = subtotal_total + hst_13

st.write(f"**Total Due: ${total_final:,.2f}**")
instructions = st.text_area("Instructions & Warranty:")

# --- GERAÇÃO DO PDF ---
if st.button("Generate Official PDF"):
    pdf_bytes = create_pdf(invoice_no, invoice_date, client_name, client_addr, jobsite_addr, edited_items, subtotal_total, hst_13, total_final, instructions)
    st.download_button(label="Download Invoice PDF", data=pdf_bytes, file_name=f"Invoice_{invoice_no}.pdf", mime="application/pdf")
