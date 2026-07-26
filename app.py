import streamlit as st
import db_manager as db
import pandas as pd
from datetime import datetime
import os
import io

# Importaciones para generación de PDF profesional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración de página
st.set_page_config(layout="wide", page_title="Helicor Management")

# Asegurar carpeta de almacenamiento de imágenes
UPLOAD_DIR = "uploads_evidence"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# CSS: Fondo verde muy tenue, botones en verde subido, menú horizontal superior y texto en color negro
st.markdown("""
    <style>
    /* Fondo general verde muy tenue */
    .stApp { background-color: #E8F5E9 !important; }
    
    /* Textos generales y etiquetas en color negro */
    h1, h2, h3, p, label, div, span, th, td { color: #000000 !important; font-weight: 800 !important; }
    
    /* Botones generales */
    div.stButton > button { background-color: #2E7D32 !important; color: #FFFFFF !important; border: 2px solid #1B5E20 !important; }
    
    /* Inputs y campos de texto */
    input { background-color: #FFFFFF !important; color: #000000 !important; font-weight: bold; }
    
    .row-widget.stHorizontal { display: flex; gap: 10px; }
    </style>
""", unsafe_allow_html=True)

# Inicializar DB
db.init_db()

if 'selected_hpn' not in st.session_state: st.session_state.selected_hpn = None
if 'active_tab' not in st.session_state: st.session_state.active_tab = "Dashboard"

# Menú de navegación horizontal superior
st.title("🏗️ HELICOR MANAGEMENT SYSTEM")
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns([1, 1, 1, 1, 2])

with col_m1:
    if st.button("Dashboard", use_container_width=True, key="nav_dashboard"): 
        st.session_state.selected_hpn = None
        st.session_state.active_tab = "Dashboard"
        st.rerun()

with col_m2:
    if st.button("Add New Project", use_container_width=True, key="nav_add_project"): 
        st.session_state.selected_hpn = "ADD_NEW"
        st.session_state.active_tab = "Add New Project"
        st.rerun()

with col_m3:
    if st.button("Executive Report", use_container_width=True, key="nav_report"): 
        st.session_state.selected_hpn = None
        st.session_state.active_tab = "Report"
        st.rerun()

with col_m4:
    if st.button("Financial", use_container_width=True, key="nav_financial"): 
        st.session_state.selected_hpn = None
        st.session_state.active_tab = "Financial"
        st.rerun()

st.markdown("---")

def generate_executive_pdf(df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor("#1B5E20"), alignment=1, spaceAfter=15)
    
    elements.append(Paragraph("HELICOR MANAGEMENT - CONSOLIDATED EXECUTIVE REPORT", title_style))
    elements.append(Paragraph(f"Generated Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    table_data = [list(df.columns)] + df.values.tolist()
    t = Table(table_data, colWidths=[90, 75, 75, 85, 85, 95])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E8F5E9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#A5D6A7")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_financial_pdf(proj_name, hpn, total_rev, current_prog, tranches_data, total_paid):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, textColor=colors.HexColor("#1B5E20"), alignment=1, spaceAfter=10)
    
    elements.append(Paragraph(f"FINANCIAL STATEMENT & TRANCHES REPORT", title_style))
    elements.append(Paragraph(f"Project: {proj_name} ({hpn})", styles['Heading2']))
    elements.append(Paragraph(f"Total Revenue: ${total_rev:,.2f} | Current Progress: {current_prog:.0%}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    table_data = [["Tranche Milestone", "Amount ($)", "Invoice Status", "Paid Status"]]
    for item in tranches_data:
        table_data.append([item['label'], f"${item['amount']:,.2f}", item['invoice'], item['paid']])
        
    t = Table(table_data, colWidths=[110, 130, 130, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#E8F5E9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#A5D6A7")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"<b>Total Paid to Date:</b> ${total_paid:,.2f}", styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# 1. REPORTE EJECUTIVO
if st.session_state.active_tab == "Report":
    st.title("📊 CONSOLIDATED EXECUTIVE REPORT")
    df_report = db.get_consolidated_report() if hasattr(db, 'get_consolidated_report') else pd.DataFrame()
    
    if not df_report.empty:
        st.dataframe(df_report, hide_index=True, use_container_width=True)
    else:
        st.info("No consolidated data available.")

    st.markdown("---")
    st.subheader("Export Executive Report")
    col_dl1, col_dl2 = st.columns(2)
    
    if not df_report.empty:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_report.to_excel(writer, index=False, sheet_name='Executive Report')
        excel_data = excel_buffer.getvalue()
        
        col_dl1.download_button(
            label="📥 Download Excel Report (.xlsx)",
            data=excel_data,
            file_name=f"Executive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        pdf_data = generate_executive_pdf(df_report)
        col_dl2.download_button(
            label="📥 Download PDF Report (.pdf)",
            data=pdf_data,
            file_name=f"Executive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# SUBMENÚ FINANCIAL
elif st.session_state.active_tab == "Financial":
    st.title("💰 FINANCIAL TRACKING & MANAGEMENT")
    df_projects = db.get_projects()
    
    if df_projects.empty:
        st.warning("No projects available in the database.")
    else:
        if 'owner' not in df_projects.columns: df_projects['owner'] = ""
        if 'customer' not in df_projects.columns: df_projects['customer'] = ""
        if 'city' not in df_projects.columns: df_projects['city'] = ""
        if 'region' not in df_projects.columns: df_projects['region'] = ""
        if 'start_date' not in df_projects.columns: df_projects['start_date'] = ""
        if 'end_date' not in df_projects.columns: df_projects['end_date'] = ""
        if 'total_revenue' not in df_projects.columns: df_projects['total_revenue'] = 0.0

        f_col1, f_col2, f_col3 = st.columns(3)
        filtered_df = df_projects.copy()
        
        managers = ["All"] + list(filtered_df['owner'].dropna().unique())
        selected_manager = f_col1.selectbox("Project Manager", managers, key="fin_mgr")
        if selected_manager != "All":
            filtered_df = filtered_df[filtered_df['owner'] == selected_manager]
            
        hpns = ["All"] + list(filtered_df['hpn'].dropna().unique())
        selected_hpn_fin = f_col2.selectbox("HPN", hpns, key="fin_hpn")
        if selected_hpn_fin != "All":
            filtered_df = filtered_df[filtered_df['hpn'] == selected_hpn_fin]
            
        customers = ["All"] + list(filtered_df['customer'].dropna().unique())
        selected_customer = f_col3.selectbox("Customer", customers, key="fin_cust")
        if selected_customer != "All":
            filtered_df = filtered_df[filtered_df['customer'] == selected_customer]

        st.markdown("---")

        if not filtered_df.empty:
            row = filtered_df.iloc[0]
            
            st.subheader("Project Details")
            d_col1, d_col2, d_col3, d_col4, d_col5 = st.columns(5)
            d_col1.metric("Project Manager", row.get('owner', 'N/A'))
            d_col2.metric("City", row.get('city', 'N/A'))
            d_col3.metric("Region", row.get('region', 'N/A'))
            d_col4.metric("Start Date", str(row.get('start_date', 'N/A')))
            d_col5.metric("End Date", str(row.get('end_date', 'N/A')))
            
            st.markdown("---")

            total_target = (row.get('round_piles', 0) or 0) + (row.get('square_piles', 0) or 0)
            logs_df = db.get_daily_logs(row['hpn'])
            installed = logs_df['piles_added'].sum() if not logs_df.empty and 'piles_added' in logs_df.columns else 0
            current_progress = installed / total_target if total_target > 0 else 0.0

            total_rev = row.get('total_revenue', 0.0) or 0.0

            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Current Progress Percentage", f"{current_progress:.0%}")
            m_col2.metric("Total Revenue", f"${total_rev:,.2f}")

            st.markdown("---")

            st.subheader("Milestone Distribution & Financial Status")
            tranches = [
                ("20%", 0.20),
                ("40%", 0.20),
                ("60%", 0.20),
                ("80%", 0.20),
                ("100%", 0.20)
            ]
            ratios_acumulados = [0.20, 0.40, 0.60, 0.80, 1.00]

            saved_payments = db.get_tranche_payments(row['hpn'])

            with st.form(f"form_fin_tranches_{row['hpn']}_v2"):
                t_col_left, t_col_right = st.columns([1, 1])
                
                tranche_amounts = {}
                with t_col_left:
                    st.write("### Tranche Amounts")
                    for (label, ratio), _ in zip(tranches, ratios_acumulados):
                        amount = total_rev * ratio
                        tranche_amounts[label] = amount
                        st.text(f"{label}: ${amount:,.2f}")

                paid_checks = {}
                invoice_checks = {}

                with t_col_right:
                    c_inv, c_paid = st.columns(2)
                    
                    with c_inv:
                        st.write("### Invoice (Auto-calculated)")
                        for (label, _), ratio_acum in zip(tranches, ratios_acumulados):
                            auto_checked = current_progress >= ratio_acum
                            invoice_checks[label] = st.checkbox(
                                f"Invoice {label}", 
                                value=auto_checked, 
                                disabled=True, 
                                key=f"inv_auto_{row['hpn']}_{label}"
                            )
                    
                    with c_paid:
                        st.write("### Paid")
                        for label, _ in tranches:
                            default_paid = saved_payments.get(label, False)
                            paid_checks[label] = st.checkbox(f"Paid {label}", value=default_paid, key=f"paid_{row['hpn']}_{label}")

                st.markdown("---")
                save_payments_btn = st.form_submit_button("💾 SAVE PAYMENTS & UPDATES")
                
                if save_payments_btn:
                    for label, _ in tranches:
                        db.save_tranche_payment(row['hpn'], label, paid_checks[label])
                    st.success("Payments and financial status saved successfully! Dashboard alerts updated.")
                    st.rerun()

            tranches_summary_list = []
            total_paid = 0.0
            for (label, _), ratio_acum in zip(tranches, ratios_acumulados):
                is_inv = "Yes" if invoice_checks[label] else "No"
                is_pd = "Yes" if paid_checks.get(label, False) else "No"
                if paid_checks.get(label, False):
                    total_paid += tranche_amounts[label]
                
                tranches_summary_list.append({
                    "label": label,
                    "amount": tranche_amounts[label],
                    "invoice": is_inv,
                    "paid": is_pd
                })

            st.markdown("---")
            st.metric("Total Paid", f"${total_paid:,.2f}")

            st.markdown("---")
            st.subheader("Export Financial Statement")
            
            f_dl1, f_dl2 = st.columns(2)
            
            df_tranches_export = pd.DataFrame(tranches_summary_list)
            df_tranches_export.columns = ["Tranche Milestone", "Amount ($)", "Invoice Status", "Paid Status"]
            
            excel_fin_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_fin_buffer, engine='openpyxl') as writer:
                df_tranches_export.to_excel(writer, index=False, sheet_name='Financial Tranches')
            excel_fin_data = excel_fin_buffer.getvalue()
            
            f_dl1.download_button(
                label="📥 Download Financial Excel (.xlsx)",
                data=excel_fin_data,
                file_name=f"Financial_{row['hpn']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_excel_fin"
            )
            
            pdf_fin_data = generate_financial_pdf(row['name'], row['hpn'], total_rev, current_progress, tranches_summary_list, total_paid)
            f_dl2.download_button(
                label="📥 Download Financial PDF (.pdf)",
                data=pdf_fin_data,
                file_name=f"Financial_{row['hpn']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_pdf_fin"
            )

        else:
            st.info("No projects match the selected filters.")

# 2. AGREGAR PROYECTO
elif st.session_state.selected_hpn == "ADD_NEW":
    st.title("REGISTER NEW PROJECT - ALL DATA")
    
    if 'calc_total_revenue' not in st.session_state:
        st.session_state.calc_total_revenue = 0.0

    with st.form("add_form"):
        c1, c2 = st.columns(2)
        hpn = c1.text_input("HPN (Required)")
        name = c2.text_input("Project Name (Required)")
        
        c3, c4 = st.columns(2)
        customer = c3.text_input("Customer")
        owner = c4.text_input("Project Manager")
        
        c5, c6 = st.columns(2)
        city = c5.text_input("City")
        state = c6.text_input("State")
        
        region = st.text_input("Region")
        
        c7, c8 = st.columns(2)
        start = c7.date_input("Start Date")
        end = c8.date_input("End Date")
        
        c9, c10 = st.columns(2)
        round_piles = c9.number_input("Round Piles", value=0.0)
        square_piles = c10.number_input("Square Piles", value=0.0)
        
        c11, c12 = st.columns(2)
        labor = c11.number_input("Labor ($)", value=0.0)
        transportation = c12.number_input("Transportation Fee ($)", value=0.0)
        
        c13, c14 = st.columns(2)
        machinery = c13.number_input("Machinery Rental ($)", value=0.0)
        other_exp = c14.number_input("Other Expenses ($)", value=0.0)
        
        calculate_clicked = st.form_submit_button("CALCULATE TOTAL REVENUE")
        
        if calculate_clicked:
            base_sq = square_piles * 100
            base_rd = round_piles * 70
            install_sq = square_piles * 1500
            install_rd = round_piles * 900
            
            st.session_state.calc_total_revenue = base_sq + base_rd + install_sq + install_rd + labor + transportation + machinery + other_exp
            st.success(f"Calculated Total Revenue: ${st.session_state.calc_total_revenue:,.2f}")

        st.markdown("---")
        total_revenue = st.number_input("Total Revenue ($)", value=st.session_state.calc_total_revenue)
        
        submitted = st.form_submit_button("SAVE FULL PROJECT DATA")
        
        if submitted:
            if hpn and name:
                db.add_project((hpn, name, customer, owner, city, state, region, str(start), str(end), round_piles, square_piles, total_revenue, labor, transportation, machinery, other_exp))
                st.success("Project saved successfully!")
                st.session_state.calc_total_revenue = 0.0
                st.session_state.selected_hpn = None
                st.session_state.active_tab = "Dashboard"
                st.rerun()
            else:
                st.error("HPN and Project Name are required.")

# 3. DETALLES Y AVANCE
elif st.session_state.selected_hpn:
    hpn = st.session_state.selected_hpn
    df_proj = db.get_projects()
    proj = df_proj[df_proj['hpn'] == hpn].iloc[0]
    st.title(f"DETAILS: {proj['name']} ({hpn}) - Mgr: {proj.get('owner', 'N/A')}")
    
    with st.form("log_form"):
        st.write("### Piles to add & Field Evidence")
        c_sub1, c_sub2 = st.columns(2)
        square_added = c_sub1.number_input("Square Piles Added", min_value=0.0, value=0.0)
        round_added = c_sub2.number_input("Round Piles Added", min_value=0.0, value=0.0)
        
        note = st.text_area("Field Notes / Report Note")
        user_author = st.text_input("Logged By (User / Inspector)", value="Site Supervision")
        uploaded_file = st.file_uploader("Attach Site Photograph (Evidence)", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("ADD PROGRESS & EVIDENCE"):
            total_added = square_added + round_added
            current_date_str = str(datetime.today())
            
            image_path = ""
            if uploaded_file is not None:
                file_ext = uploaded_file.name.split('.')[-1]
                safe_filename = f"{hpn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_ext}"
                image_path = os.path.join(UPLOAD_DIR, safe_filename)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            db.add_daily_log(hpn, total_added, current_date_str, note, user_author, image_path)
            st.success("Progress, field notes, and evidence registered successfully!")
            st.rerun()

    st.markdown("---")
    st.subheader("Project Summary & Accumulated Piles")
    inf_c1, inf_c2, inf_c3, inf_c4 = st.columns(4)
    inf_c1.metric("Start Date", str(proj.get('start_date', 'N/A')))
    inf_c2.metric("End Date", str(proj.get('end_date', 'N/A')))
    
    total_sq_piles = proj.get('square_piles', 0.0)
    total_rd_piles = proj.get('round_piles', 0.0)
    
    inf_c3.metric("Total Square Piles", f"{total_sq_piles:,.0f}")
    inf_c4.metric("Total Round Piles", f"{total_rd_piles:,.0f}")

    st.markdown("---")
    st.write("### Field Notes & Visual Evidence Report")
    
    logs = db.get_daily_logs(hpn)
    if not logs.empty:
        for _, log_row in logs.iterrows():
            with st.container():
                st.markdown(f"**Log Date:** {log_row.get('log_date', 'N/A')} | **User:** {log_row.get('user_author', 'N/A')}")
                st.markdown(f"**Piles Added:** {log_row.get('piles_added', 0)}")
                st.markdown(f"**Field Note:** {log_row.get('note', 'No notes')}")
                
                img_path = log_row.get('image_path', '')
                if img_path and os.path.exists(img_path):
                    st.image(img_path, caption=f"Site Evidence - {log_row.get('log_date', '')}", width=400)
                
                st.markdown("---")
    else:
        st.info("No daily logs or field notes recorded yet for this project.")

# 4. DASHBOARD
else:
    st.title("🏗️ PROJECT PORTFOLIO DASHBOARD")
    df = db.get_projects()
    
    if not df.empty:
        tranches_config_alertas = [("20%", 0.20), ("40%", 0.40), ("60%", 0.60), ("80%", 0.80), ("100%", 1.00)]
        
        for _, row in df.iterrows():
            total_target = row['round_piles'] + row['square_piles'] if (row['round_piles'] or row['square_piles']) else 0
            
            logs_df = db.get_daily_logs(row['hpn'])
            installed = logs_df['piles_added'].sum() if not logs_df.empty and 'piles_added' in logs_df.columns else 0
            
            progress = installed / total_target if total_target > 0 else 0
            progress_percent = min(max(progress * 100, 0), 100) # De 0 a 100%
            
            # Estructura limpia en columnas: HPN, Nombre, Manager, Barra visual personalizada y Botón VIEW
            cols = st.columns([1, 1.5, 1.5, 2, 1])
            cols[0].write(f"### {row['hpn']}")
            cols[1].write(f"### {row['name']}")
            cols[2].write(f"**Mgr:** {row.get('owner', 'N/A')}")
            
            # Barra de progreso visual personalizada mediante HTML/CSS con degradado y porcentaje exacto
            custom_progress_html = f"""
                <div style="margin-top: 5px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                        <span style="font-size: 13px; font-weight: bold; color: #000000;">Progress</span>
                        <span style="font-size: 13px; font-weight: bold; color: #1B5E20;">{progress_percent:.0f}%</span>
                    </div>
                    <div style="background-color: #C8E6C9; border-radius: 10px; height: 16px; width: 100%; overflow: hidden;">
                        <div style="background-image: linear-gradient(90deg, #2E7D32, #4CAF50); width: {progress_percent}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
            """
            cols[3].markdown(custom_progress_html, unsafe_allow_html=True)
            
            if cols[4].button("VIEW", key=f"view_{row['hpn']}"): 
                st.session_state.selected_hpn = row['hpn']
                st.session_state.active_tab = "Details"
                st.rerun()

            saved_payments = db.get_tranche_payments(row['hpn'])

            for label, ratio_ac in tranches_config_alertas:
                if progress >= ratio_ac:
                    is_paid = saved_payments.get(label, False)
                    if not is_paid:
                        st.warning(f"⚠️ Alert: Project **{row['name']} ({row['hpn']})** managed by **{row.get('owner', 'N/A')}** has reached the **{label}** progress milestone and the corresponding tranche has not been marked as paid yet.")
    else:
        st.write("No projects found. Please add a new project.")
