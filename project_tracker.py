import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

st.set_page_config(page_title="项目进度管理", layout="wide")
st.title("📊 项目进度管理系统")

# SQLite 数据库连接
DB_FILE = "project_manager.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# 初始化表
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    项目名称 TEXT PRIMARY KEY,
    状态 TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    姓名 TEXT PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    项目名称 TEXT,
    姓名 TEXT,
    PRIMARY KEY (项目名称, 姓名)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS progress_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    项目名称 TEXT,
    姓名 TEXT,
    更新时间 TEXT,
    进展说明 TEXT,
    资源需求 TEXT,
    跟进建议 TEXT
)
""")
conn.commit()

# 👉 添加项目
st.sidebar.header("➕ 添加项目")
with st.sidebar.form("add_project_form"):
    project_name = st.text_input("项目名称")
    status = st.selectbox("状态", ["未开始", "进行中", "已完成"])
    submitted = st.form_submit_button("添加项目")
    if submitted and project_name:
        try:
            cursor.execute("INSERT INTO projects (项目名称, 状态) VALUES (?, ?)", (project_name, status))
            conn.commit()
            st.success(f"✅ 添加项目：{project_name}")
        except sqlite3.IntegrityError:
            st.warning("⚠️ 项目已存在")

# 👉 添加人员
st.sidebar.header("👤 添加人员")
with st.sidebar.form("add_staff_form"):
    staff_name = st.text_input("姓名")
    staff_submitted = st.form_submit_button("添加人员")
    if staff_submitted and staff_name:
        try:
            cursor.execute("INSERT INTO staff (姓名) VALUES (?)", (staff_name,))
            conn.commit()
            st.success(f"✅ 添加人员：{staff_name}")
        except sqlite3.IntegrityError:
            st.warning("⚠️ 人员已存在")

# 👉 分配人员到项目
st.sidebar.header("🔗 分配项目与人员")
with st.sidebar.form("assign_form"):
    cursor.execute("SELECT 项目名称 FROM projects")
    project_list = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT 姓名 FROM staff")
    staff_list = [row[0] for row in cursor.fetchall()]
    if project_list and staff_list:
        proj = st.selectbox("选择项目", project_list)
        person = st.selectbox("选择人员", staff_list)
        assign_submitted = st.form_submit_button("分配")
        if assign_submitted:
            try:
                cursor.execute("INSERT INTO assignments (项目名称, 姓名) VALUES (?, ?)", (proj, person))
                conn.commit()
                st.success(f"🔗 分配成功：{person} -> {proj}")
            except sqlite3.IntegrityError:
                st.warning("⚠️ 已分配，无需重复")
    else:
        st.info("请先添加项目和人员")

# 👉 项目进度更新
st.sidebar.header("📥 上传项目进度")
with st.sidebar.form("update_progress_form"):
    if staff_list:
        person = st.selectbox("你的姓名", staff_list)
        cursor.execute("SELECT 项目名称 FROM assignments WHERE 姓名=?", (person,))
        user_projects = [row[0] for row in cursor.fetchall()]
        if user_projects:
            proj = st.selectbox("选择你负责的项目", user_projects)
            notes = st.text_area("📄 进展说明")
            resources = st.text_area("📦 资源需求")
            followup = st.text_area("📌 跟进建议")
            update_submitted = st.form_submit_button("提交进度")
            if update_submitted:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO progress_updates (项目名称, 姓名, 更新时间, 进展说明, 资源需求, 跟进建议)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (proj, person, now, notes, resources, followup))
                conn.commit()
                st.success(f"📬 已更新 {proj} 的进度记录")
        else:
            st.warning("你还没有被分配到任何项目")
    else:
        st.info("请先添加人员")

# 👉 项目浏览界面（层级结构）
st.header("📁 项目总览")
cursor.execute("SELECT 项目名称 FROM projects")
all_projects = [row[0] for row in cursor.fetchall()]
if not all_projects:
    st.info("暂无项目，请在左侧添加")
else:
    selected_project = st.selectbox("请选择要查看的项目：", all_projects)
    if selected_project:
        cursor.execute("SELECT 状态 FROM projects WHERE 项目名称=?", (selected_project,))
        status = cursor.fetchone()[0]
        st.subheader(f"🧩 {selected_project} - 项目信息")
        st.text(f"状态: {status}")

        cursor.execute("SELECT 姓名 FROM assignments WHERE 项目名称=?", (selected_project,))
        assigned_people = [row[0] for row in cursor.fetchall()]
        if assigned_people:
            st.markdown("**👥 负责人：** " + ", ".join(assigned_people))
        else:
            st.markdown("_暂无负责人_")

        cursor.execute("SELECT 姓名, 更新时间, 进展说明, 资源需求, 跟进建议 FROM progress_updates WHERE 项目名称=? ORDER BY 更新时间 DESC", (selected_project,))
        updates = cursor.fetchall()
        if updates:
            st.markdown("### 📈 项目进度更新记录")
            for row in updates:
                姓名, 更新时间, 进展说明, 资源需求, 跟进建议 = row
                with st.expander(f"📌 {更新时间} | {姓名} 上传的记录"):
                    st.markdown(f"**进展说明：** {进展说明 or '无'}")
                    st.markdown(f"**资源需求：** {资源需求 or '无'}")
                    st.markdown(f"**跟进建议：** {跟进建议 or '无'}")
        else:
            st.info("该项目尚未有进度上传记录")