import streamlit as st
import pandas as pd
import os
from PIL import Image
import io

# Set up the page title and layout
st.set_page_config(
    page_title="ร้านขนมปัง5ก้อนกับปลา2ตัวโฮมเมดเบเกอรี่",
    layout="wide"
)

# Custom CSS for light green theme
st.markdown("""
<style>
    .reportview-container {
        background-color: #f2f7f2;
    }
    .stButton>button {
        background-color: #aed581;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #9ccc65;
        color: white;
    }
    h1, h2, h3 {
        color: #4a4a4a;
    }
</style>
""", unsafe_allow_html=True)

st.title("ระบบรับออเดอร์ร้านขนมปัง5ก้อนกับปลา2ตัวโฮมเมดเบเกอรี่ 🍞🐟")
st.markdown("---")

# File name for data storage
EXCEL_FILE = 'orders.xlsx'
IMAGE_FOLDER = 'images'

# --- Function to load and save data to Excel ---
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            return pd.read_excel(EXCEL_FILE, engine='openpyxl')
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์ Excel: {e}")
            return pd.DataFrame(columns=[
                "ช่องทาง", "สินค้า", "รายละเอียด", "จำนวน", "ราคารวม (บาท)", 
                "สถานะ", "ยอดมัดจำ (บาท)", "ยอดค้างจ่าย (บาท)", 
                "สถานที่นัดรับ", "ผู้รับออเดอร์", "หมายเหตุ", "ไฟล์รูปภาพ"
            ])
    else:
        return pd.DataFrame(columns=[
            "ช่องทาง", "สินค้า", "รายละเอียด", "จำนวน", "ราคารวม (บาท)", 
            "สถานะ", "ยอดมัดจำ (บาท)", "ยอดค้างจ่าย (บาท)", 
            "สถานที่นัดรับ", "ผู้รับออเดอร์", "หมายเหตุ", "ไฟล์รูปภาพ"
        ])

def save_data(df):
    try:
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึกไฟล์ Excel: {e}")

# Load existing data on app startup
orders_df = load_data()

# Order form section
st.header("ฟอร์มรับออเดอร์")
with st.form(key="order_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        channel = st.selectbox("ช่องทาง", ["Facebook", "Line OA", "Tiktok", "ส่วนตัว"])
        
        product_option = st.selectbox("สินค้า", ["เค้กวันเกิด", "คัพเค้ก", "เค้กโบราณ", "ขนมปัง", "ขนมจัดเบรค", "อื่นๆ"])
        if product_option == "อื่นๆ":
            product = st.text_input("ระบุสินค้าอื่นๆ", key="other_product_input")
        else:
            product = product_option
        
        details = st.text_area("รายละเอียดสินค้า", help="เช่น รสชาติ, รูปแบบ, คำอวยพร")
        quantity = st.number_input("จำนวน", min_value=1, step=1)
    
    with col2:
        image_upload = st.file_uploader("แนบรูปภาพ (Reference)", type=["jpg", "png", "jpeg"])
        total_price = st.number_input("รวมยอด (บาท)", min_value=0.0, step=1.0)
        status = st.selectbox("สถานะ", ["ค้างจ่าย", "มัดจำ", "จ่ายแล้ว", "เสร็จสิ้น"])
        
        deposit = 0.0
        remaining = 0.0
        
        if status == "มัดจำ":
            deposit = st.number_input("ยอดมัดจำ (บาท)", min_value=0.0, step=1.0)
            remaining = total_price - deposit
            st.info(f"ยอดค้างชำระ: {remaining:,.2f} บาท")
        elif status == "จ่ายแล้ว":
            deposit = total_price
        else:
            remaining = total_price
        
        pickup_location = st.selectbox("สถานที่นัดรับ", ["สาขา 1", "สาขา 2", "อื่นๆ"])
        if pickup_location == "อื่นๆ":
            pickup_location = st.text_input("ระบุสถานที่นัดรับอื่นๆ", key="other_pickup_input")

        receiver = st.text_input("ชื่อผู้รับออเดอร์")
    
    notes = st.text_area("หมายเหตุ (ถ้ามี)")
    submit_button = st.form_submit_button(label="เพิ่มออเดอร์")
    
    if submit_button:
        image_path = None
        if image_upload is not None:
            if not os.path.exists(IMAGE_FOLDER):
                os.makedirs(IMAGE_FOLDER)
            
            img_name = f"{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}_{image_upload.name}"
            image_path = os.path.join(IMAGE_FOLDER, img_name)
            with open(image_path, "wb") as f:
                f.write(image_upload.getbuffer())
        
        new_row = {
            "ช่องทาง": channel,
            "สินค้า": product,
            "รายละเอียด": details,
            "จำนวน": quantity,
            "ราคารวม (บาท)": total_price,
            "สถานะ": status,
            "ยอดมัดจำ (บาท)": deposit,
            "ยอดค้างจ่าย (บาท)": remaining,
            "สถานที่นัดรับ": pickup_location,
            "ผู้รับออเดอร์": receiver,
            "หมายเหตุ": notes,
            "ไฟล์รูปภาพ": image_path
        }
        
        orders_df = pd.concat([orders_df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(orders_df)
        st.success("รับออเดอร์เรียบร้อยแล้วและบันทึกข้อมูลเรียบร้อย! ✅")
        st.experimental_rerun()

# Display orders section
st.markdown("---")
st.header("รายการออเดอร์ทั้งหมด")

if not orders_df.empty:
    display_df = orders_df.copy()
    display_df['รูปภาพ'] = display_df['ไฟล์รูปภาพ'].apply(lambda)