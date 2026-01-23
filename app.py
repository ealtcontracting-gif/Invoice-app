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

# --- FUNÇÃO DO PDF (LETTER SIZE) ---
def create_pdf(invoice_no, date, client_n, client_a, job_a, items, sub, hst, total, notes):
    pdf = FPDF(orientation='P', unit='mm', format='Letter')
    pdf.add_page()
    
    # Cabeçalho com Logo
    if os.path.exists("Alt Contracting Logo.png"):
        pdf.image("Alt Contracting Logo.png", 10, 8, 45)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, COMPANY["name"], ln=True, align='R')
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, f"{COMPANY['web']} | {COMPANY['phone']}", ln=True, align='R')
    pdf.cell(190, 5, COMPANY['tax_id'], ln=True, align='R')
    pdf.ln(15)
    
    # Informações do Cliente e Invoice
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "BILL TO:", ln=False)
    pdf.cell(95, 10, f"INVOICE #: {invoice_no}", ln=True, align='R')
    pdf.set_font("Arial", '', 11)
    pdf.cell(95, 5, str(client_n), ln=False)
    pdf.cell(95, 5, f"Date: {date}", ln=True, align='R')
    pdf.multi_cell(95, 5, str(client_a))
    pdf.ln(5)
    
    # Jobsite
    pdf.set_fill_color(240, 242, 246)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, f" JOBSITE: {job_a}", ln=True, fill=True)
    pdf.ln(5)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(75, 8, "Description", 1, 0, 'C', True)
    pdf.cell(25, 8, "Price ($)", 1, 0, 'C', True)
    pdf.cell(30, 8, "SQFT", 1, 0, 'C', True)
    pdf.cell(30, 8, "Time (h)", 1, 0, 'C', True)
    pdf.cell(30, 8, "Subtotal", 1, 1, 'C', True)
    
    # Linhas da Tabela
    pdf.set_font("Arial", '', 10)
    for _, row in items.iterrows():
        pdf.cell(75, 7, str(row['Description']), 1)
        pdf.cell(25, 7, f"{float(row['Price']):.2f}", 1, 0, 'C')
        pdf.cell(30, 7, str(row['SQFT']), 1, 0, 'C')
        pdf.cell(30, 7, str(row['Time']), 1, 0, 'C')
        pdf.cell(30, 7, f"{float(row['Subtotal']):.2f}", 1, 1, 'C')
    
    # Totais
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(160, 7, "Subtotal:", 0, 0, 'R')
    pdf.cell(30, 7, f"${sub:,.2f}", 1, 1, 'C')
    pdf.cell(160, 7, "HST (13%):", 0, 0, 'R')
    pdf.cell(30, 7, f"${hst:,.2f}", 1, 1, 'C')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(160, 10, "TOTAL DUE:", 0, 0, 'R')
    pdf.cell(30, 10, f"${total:,.2f}", 1, 1, 'C')
    
    # Instruções e Garantia
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 5, "Instructions & Warranty:", ln=True)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(190, 5, str(notes))
    
    # ASSINATURA (Restaurada para o PDF)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 5, "___________________________________________", ln=True)
    pdf.cell(190, 5, COMPANY['user'], ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(190, 5, COMPANY['email'], ln=True)
    
    # Retorna os bytes diretamente (correção do erro 'bytearray')
    return pdf.output()

# --- INTERFACE NO BROWSER ---
col_l, col_r = st.columns([1, 2])
with col_l:
    if os.path.exists("Alt Contracting Logo.png"):
        st.image("Alt Contracting Logo.png", width=250)
with col_r:
    st.title(COMPANY["name"])
    st.write(f"🌐 {COMPANY['web']} | 📞 {COMPANY['phone']}")
    st.write(f"📄 {COMPANY['tax_id']}")

st.markdown("---")

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

st.subheader("Services / Descrição")
if 'items_data' not in st.session_state:
    st.session_state.items_data = pd.DataFrame([{"Description": "", "Price": 0.00, "SQFT": 0, "Time": 0}])

# Editor
edited_df = st.data_editor(st.session_state.items_data, num_rows="dynamic", use_container_width=True, key="my_editor")

# Cálculos
final_df = edited_df.copy()
def calc_sub(row):
    p, s, t = float(row['Price'] or 0), float(row['SQFT'] or 0), float(row['Time'] or 0)
    return p * s if s > 0 else p * t

final_df['Subtotal'] = final_df.apply(calc_sub, axis=1)

# Preview
st.markdown("### Preview for Client")
st.dataframe(final_df, use_container_width=True, hide_index=True)

# Totais na tela
sub_val = final_df['Subtotal'].sum()
hst_val = sub_val * 0.13
total_val = sub_val + hst_val

col_t1, col_t2 = st.columns([2, 1])
with col_t2:
    st.write(f"**Subtotal:** ${sub_val:,.2f}")
    st.write(f"**HST (13%):** ${hst_val:,.2f}")
    st.subheader(f"Total Due: ${total_val:,.2f}")

instructions = st.text_area("Instructions & Warranty:")

# BOTÃO PDF
if st.button("Generate Official PDF"):
    try:
        # Chamada da função sem o .encode('latin-1') que causava o erro
        pdf_bytes = create_pdf(invoice_no, str(invoice_date), client_name, client_addr, jobsite_addr, final_df, sub_val, hst_val, total_val, instructions)
        
        st.download_button(
            label="⬇️ Download Invoice PDF", 
            data=bytes(pdf_bytes), 
            file_name=f"Invoice_{invoice_no}.pdf", 
            mime="application/pdf"
        )
        st.success("PDF gerado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
