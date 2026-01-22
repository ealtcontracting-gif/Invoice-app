import streamlit as st
import pandas as pd
from datetime import datetime
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

# --- CABEÇALHO ---
col_l, col_r = st.columns([1, 2])
with col_l:
    # Ajustado para o nome exato do arquivo que você subiu
    if os.path.exists("Alt Contracting Logo.png"):
        st.image("Alt Contracting Logo.png", width=250)
    else:
        st.warning("Logo 'Alt Contracting Logo.png' não encontrada.")

with col_r:
    st.title(COMPANY["name"])
    st.write(f"🌐 {COMPANY['web']} | 📞 {COMPANY['phone']}")
    st.write(f"📄 {COMPANY['tax_id']}")

st.markdown("---")

# --- SERIAL E CLIENTE ---
current_ym = datetime.now().strftime("%Y/%m")
col_s1, col_s2 = st.columns([1, 2])
with col_s1:
    serial_input = st.text_input("Sequence", "001")
    invoice_no = f"{current_ym}-{serial_input}"
with col_s2:
    st.info(f"**Invoice Number:** {invoice_no}")

col_c1, col_c2 = st.columns(2)
with col_c1:
    client_name = st.text_input("Client Name")
    client_addr = st.text_area("Client Address")
with col_c2:
    invoice_date = st.date_input("Issue Date", datetime.now())

# --- JOBSITE ---
st.markdown("### **JOBSITE**")
jobsite_addr = st.text_input("Local:")

st.markdown("---")

# --- EDITOR DE SERVIÇOS (ÁREA DE PREENCHIMENTO) ---
with st.expander("Clique aqui para preencher os serviços", expanded=True):
    if 'invoice_items' not in st.session_state:
        st.session_state.invoice_items = pd.DataFrame([
            {"Description": "", "Price": 0.00, "SQFT": 0, "Time": 0}
        ])

    edited_items = st.data_editor(
        st.session_state.invoice_items,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Description": st.column_config.TextColumn("Description", width="large"),
            "Price": st.column_config.NumberColumn("Price ($)", format="%.2f"),
            "SQFT": st.column_config.NumberColumn("SQFT"),
            "Time": st.column_config.NumberColumn("Time (h)"),
        }
    )

# Lógica de Cálculo
def calculate_row(row):
    p = float(row['Price'] or 0)
    s = float(row['SQFT'] or 0)
    t = float(row['Time'] or 0)
    return p * s if s > 0 else p * t

# Criar a coluna Subtotal
edited_items['Subtotal'] = edited_items.apply(calculate_row, axis=1)

# --- RESUMO PARA O CLIENTE (O QUE VAI NO PDF) ---
st.subheader("Services / Descrição dos Serviços")
# Mostramos apenas a tabela limpa com o Subtotal
st.dataframe(edited_items, use_container_width=True, hide_index=True)

# --- TOTAIS FINAIS ---
subtotal_total = edited_items['Subtotal'].sum()
hst_13 = subtotal_total * 0.13
total_final = subtotal_total + hst_13

st.markdown("---")
c_left, c_right = st.columns([2, 1])
with c_right:
    st.write(f"**Subtotal:** ${subtotal_total:,.2f}")
    st.write(f"**HST (13%):** ${hst_13:,.2f}")
    st.subheader(f"TOTAL DUE: ${total_final:,.2f}")

# --- INSTRUÇÕES E ASSINATURA ---
st.subheader("Instructions & Warranty")
instructions = st.text_area("Comentários, orientações finais ou garantia do trabalho:", height=100)

st.markdown("<br><br>", unsafe_allow_html=True)
st.write("✍️ ___________________________________________")
st.write(f"**{COMPANY['user']}**")
st.write(COMPANY['email'])

# --- SALVAR ---
if st.button("Save to History"):
    history_file = "history.csv"
    record = pd.DataFrame([{
        "Invoice": invoice_no, 
        "Date": invoice_date, 
        "Client": client_name, 
        "Total": f"{total_final:.2f}"
    }])
    record.to_csv(history_file, mode='a', header=not os.path.exists(history_file), index=False)
    st.success("Dados salvos com sucesso!")
