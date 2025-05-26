import streamlit as st
import pandas as pd
import numpy as np

# ====== Load & chuẩn hóa dữ liệu ======
@st.cache_data
def load_data():
    df = pd.read_excel("Log.xlsx", sheet_name="WoList")
    return df

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # bán kính trái đất km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

# ====== UI ======
st.set_page_config(page_title="FT Job Assistant", layout="centered")
st.title("📋 Hệ thống hỗ trợ nhân viên kỹ thuật (FT)")

df = load_data()

# --- Chuẩn hóa mã nhân viên ---
available_users = df['Nhân viên thực hiện'].dropna().astype(str).str.lower().unique()
user_code = st.text_input("🔑 Nhập mã nhân viên", value="").strip().lower()

if user_code not in available_users:
    st.warning("Mã nhân viên không hợp lệ hoặc chưa có trong hệ thống.")
    st.stop()

# Lọc các công việc thuộc nhân viên này
user_df = df[df['Nhân viên thực hiện'].astype(str).str.lower() == user_code]

# --- Hiển thị công việc gần quá hạn ---
st.subheader("⚠️ Công việc sắp hết hạn (< 24h)")
near_due = user_df[user_df['Thời gian còn lại (H)'] <= 24]
near_due = near_due[['Mã trạm','Nội dung công việc','Thời gian còn lại (H)']].sort_values('Thời gian còn lại (H)').reset_index(drop=True)
near_due.index += 1
st.dataframe(near_due, use_container_width=True)

# --- Nhập mã trạm ---
st.subheader("🏗️ Kiểm tra công việc tại trạm")
station = st.text_input("📍 Nhập mã trạm (ví dụ: GLI0297)", value="GLI0297").strip().upper()

if station:
    station_df = user_df[user_df['Mã trạm'] == station].sort_values('Thời gian còn lại (H)')
    station_df = station_df[['Nội dung công việc','Thời gian còn lại (H)']].reset_index(drop=True)
    station_df.index += 1
    st.write(f"Các công việc của bạn tại trạm **{station}**:")
    st.dataframe(station_df, use_container_width=True)

    # Gợi ý công việc khác (ưu tiên gần + gần hết hạn)
    st.subheader("🌐 Gợi ý công việc khác gần đó và ưu tiên")
    if not station_df.empty:
        lat0, lon0 = df[df['Mã trạm'] == station].iloc[0]['Vĩ độ'], df[df['Mã trạm'] == station].iloc[0]['Kinh độ']
        other_jobs = user_df[user_df['Mã trạm'] != station].copy()
        other_jobs['Distance_km'] = haversine(lat0, lon0, other_jobs['Vĩ độ'], other_jobs['Kinh độ'])
        suggested = other_jobs.sort_values(['Distance_km','Thời gian còn lại (H)'])
        suggested = suggested[['Mã trạm','Nội dung công việc','Distance_km','Thời gian còn lại (H)']].reset_index(drop=True)
        suggested.index += 1
        st.dataframe(suggested, use_container_width=True)
