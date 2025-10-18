import streamlit as st
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A2
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import ast
from datetime import datetime
import time



# Streamlit page configuration
st.set_page_config(page_title="Admin Portal", page_icon="🧾", layout="wide")

colo1, colo2, colo3 = st.columns([1,3,1])
with colo2:
    st.title("Daily Unit Update - Admin Portal")
st.markdown("---")

# Today's Date
col1, col2, col3 = st.columns([1,6,1])

with col1:
    st.markdown(f"**Date |** {datetime.now().strftime('%d - %m - %Y')}")

with col3:
    st.markdown(f"**Time |** {datetime.now().strftime('%H:%M:%S')}")
    time.sleep(0.05)
# Load reports

try:
    df = pd.read_csv(r"reports_data\reports.csv")
    df.index = df.index + 1
    # st.success("✅ Reports loaded successfully.")

except FileNotFoundError:
    st.error("Reports File not found, make sure that reports.csv exist in the directory!")
    st.stop()



# Reports Filters

rigs = ["All"] + sorted(df["Rig"].dropna().unique().tolist() if "Rig" in df.columns else [])
client = ["All"] + sorted(df["Client"].dropna().unique().tolist() if "Client" in df.columns else [])

a,b,c = st.columns(3)

with a:
    st.subheader("Filter Reports  -→")

selected_rig = b.selectbox("Rig", rigs)
selected_Client = c.selectbox("Client", client)

# Apply Filters

filtered_df = df.copy()

if selected_rig != "All":
    filtered_df = filtered_df[filtered_df["Rig"] == selected_rig]

if selected_Client != "All":
    filtered_df = filtered_df[filtered_df["Client"] == selected_Client]

# Convert JSON column

if "summary_json" in df.columns:

    try:
        df["summary_json"] = df["summary_json"].apply(ast.literal_eval)
        summary_df = pd.json_normalize(df["summary_json"])
        df = pd.concat([df.drop(columns=["summary_json"]), summary_df], axis=1)
    except Exception as e:
        st.error(f"Error parsing summary: {e}")


if filtered_df is not None:

    st.dataframe(filtered_df, use_container_width=True)

else:
    # Display dataframe
    st.dataframe(df, use_container_width=True)



# Export Options

def create_pdf_from_dataframe(df, pagesize = A2):
    buffer = BytesIO()

    # Setup document with margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesize,
        leftMargin=5,
        rightMargin=5,
        topMargin=10,
        bottomMargin=10,
    )

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>Daily Units Update Report</b>", styles["Title"])
    date = Paragraph(f"<b>Date | {datetime.now().strftime('%d-%m-%Y')}</b>", styles["Title"])
    elements.append(title)
    elements.append(date)
    elements.append(Spacer(1, 12))

    # Convert DataFrame to list of lists
    data = [df.columns.tolist()] + df.astype(str).values.tolist()

    # === 🧠 Dynamic column width calculation ===
    # Measure approximate character width in points (average ~6 per char for Helvetica 9pt)
    avg_char_width = 10
    max_col_widths = []
    for col in df.columns:
        max_len = max(df[col].astype(str).map(len).max(), len(col))
        max_col_widths.append(max_len * avg_char_width)

    # Compute total table width and scale down if needed
    available_width = pagesize[0] - (doc.leftMargin + doc.rightMargin)
    total_width = sum(max_col_widths)
    if total_width > available_width:
        scale_factor = available_width / total_width
        max_col_widths = [w * scale_factor for w in max_col_widths]

    # Create the table
    table = Table(data, colWidths=max_col_widths, repeatRows=1)

    # Table styling
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    table.setStyle(table_style)

    elements.append(table)
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


if not filtered_df.empty:
    pdf_data = create_pdf_from_dataframe(filtered_df)
    filename = f"Daily_Units_Update_{datetime.now().strftime('%d-%m-%Y')}.pdf"

    st.download_button(
        label="📄 Save as PDF",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
    )

else:
    st.warning("No reports to save. Please adjust your filters.")