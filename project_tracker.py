import streamlit as st
import sqlite3
from datetime import datetime

# 多语言切换函数
def t(key):
    lang = st.session_state.get("lang", "zh")
    texts = {
        "zh": {
            "project_overview": "📁 项目总览",
            "filter_project": "🔍 选择项目",
            "all_projects": "所有项目",
            "add_project": "➕ 添加项目",
            "project_name": "项目名称",
            "status": "状态",
            "not_started": "未开始",
            "in_progress": "进行中",
            "completed": "已完成",
            "abandoned": "废弃",
            "other": "其他",
            "add": "添加",
            "add_staff": "👤 添加人员",
            "name": "姓名",
            "assign": "🔗 分配项目与人员",
            "upload_progress": "📥 上传项目进度",
            "your_name": "你的姓名",
            "your_projects": "选择你负责的项目",
            "notes": "📄 进展说明",
            "followup": "📌 跟进建议",
            "submit": "提交进度",
            "complete": "✅ 项目完成",
            "delete": "🗑 删除项目",
            "language": "🌐 语言切换",
            "owners": "负责人：",
            "no_owners": "暂无负责人",
            "updates": "📈 更新记录",
            "no_updates": "暂无更新",
        },
        "en": {
            "project_overview": "📁 Project Overview",
            "filter_project": "🔍 Select Project",
            "all_projects": "All Projects",
            "add_project": "➕ Add Project",
            "project_name": "Project Name",
            "status": "Status",
            "not_started": "Not Started",
            "in_progress": "In Progress",
            "completed": "Completed",
            "abandoned": "Abandoned",
            "other": "Other",
            "add": "Add",
            "add_staff": "👤 Add Staff",
            "name": "Name",
            "assign": "🔗 Assign Projects",
            "upload_progress": "📥 Upload Progress",
            "your_name": "Your Name",
            "your_projects": "Select Your Project",
            "notes": "📄 Progress Notes",
            "followup": "📌 Follow-up Suggestions",
            "submit": "Submit",
            "complete": "✅ Complete Project",
            "delete": "🗑 Delete Project",
            "language": "🌐 Language",
            "owners": "Owners:",
            "no_owners": "No owners",
            "updates": "📈 Update History",
            "no_updates": "No updates",
        }
    }
    return texts[lang].get(key, key)

# 页面配置
st.set_page_config(page_title="项目管理系统", layout="wide")
# 语言切换
st.sidebar.selectbox(
    t("language"), ["中文", "English"],
    index=0 if st.session_state.get("lang", "zh") == "zh" else 1,
    key="lang_selector"
)
st.session_state["lang"] = "zh" if st.session_state.lang_selector == "中文" else "en"

# 数据库连接
conn = sqlite3.connect("project_manager.db", check_same_thread=False)
c = conn.cursor()
# 初始化表
c.execute("CREATE TABLE IF NOT EXISTS projects (项目名称 TEXT PRIMARY KEY, 状态 TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS staff (姓名 TEXT PRIMARY KEY)")
c.execute("CREATE TABLE IF NOT EXISTS assignments (项目名称 TEXT, 姓名 TEXT, PRIMARY KEY (项目名称, 姓名))")
c.execute("CREATE TABLE IF NOT EXISTS progress_updates (id INTEGER PRIMARY KEY AUTOINCREMENT, 项目名称 TEXT, 姓名 TEXT, 更新时间 TEXT, 进展说明 TEXT, 资源需求 TEXT, 跟进建议 TEXT)")
conn.commit()

# ➕ 添加项目
with st.sidebar.expander(t("add_project")):
    with st.form("add_project_form", clear_on_submit=True):
        project_name = st.text_input(t("project_name"))
        status = st.selectbox(t("status"), [t("not_started"), t("in_progress")])
        if st.form_submit_button(t("add")) and project_name:
            try:
                c.execute("INSERT INTO projects (项目名称, 状态) VALUES (?, ?)", (project_name, status))
                conn.commit()
                st.success(f"{project_name} ✔")
            except:
                st.warning("项目已存在")

# 👤 添加人员
with st.sidebar.expander(t("add_staff")):
    with st.form("add_staff_form", clear_on_submit=True):
        name = st.text_input(t("name"))
        if st.form_submit_button(t("add")) and name:
            try:
                c.execute("INSERT INTO staff VALUES (?)", (name,))
                conn.commit()
                st.success(f"{name} ✔")
            except:
                st.warning("人员已存在")

# 🔗 分配项目与人员
with st.sidebar.expander(t("assign")):
    with st.form("assign_form", clear_on_submit=True):
        projects = [r[0] for r in c.execute("SELECT 项目名称 FROM projects").fetchall()]
        people = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
        if projects and people:
            proj = st.selectbox(t("project_name"), projects)
            person = st.selectbox(t("name"), people)
            if st.form_submit_button(t("add")):
                try:
                    c.execute("INSERT INTO assignments VALUES (?, ?)", (proj, person))
                    conn.commit()
                    st.success(f"{person} ➜ {proj}")
                except:
                    st.warning("已分配")
        else:
            st.info("请先添加项目和人员")

# 📥 上传项目进度
st.sidebar.markdown(f"### {t('upload_progress')}")
all_staff = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
if all_staff:
    selected_name = st.sidebar.selectbox(t("your_name"), all_staff)
    my_projects = [r[0] for r in c.execute("SELECT 项目名称 FROM assignments WHERE 姓名=?", (selected_name,)).fetchall()]
    if my_projects:
        with st.sidebar.form("progress_form", clear_on_submit=True):
            proj = st.selectbox(t("your_projects"), my_projects)
            notes = st.text_area(t("notes"))
            followup = st.text_area(t("followup"))
            if st.form_submit_button(t("submit")):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute(
                    "INSERT INTO progress_updates (项目名称, 姓名, 更新时间, 进展说明, 资源需求, 跟进建议) VALUES (?, ?, ?, ?, ?, ?)",
                    (proj, selected_name, now, notes, '', followup)
                )
                conn.commit()
                st.sidebar.success("✅ 已上传")
    else:
        st.sidebar.info("你没有被分配任何项目")
else:
    st.sidebar.warning("暂无人员")

# 📁 主界面展示及分类过滤
st.subheader(t("project_overview"))
all_data = c.execute("SELECT 项目名称, 状态 FROM projects").fetchall()

# 状态翻译映射到状态码
ALL_STATUS_TRANSLATIONS = {
    "not_started": ["未开始", "Not Started"],
    "in_progress": ["进行中", "In Progress"],
    "completed": ["已完成", "Completed"],
    "abandoned": ["废弃", "Abandoned"]
}
status_code_map = {}
for code, trans_list in ALL_STATUS_TRANSLATIONS.items():
    for trans in trans_list:
        status_code_map[trans] = code

# 分类收集
categories = ["not_started", "in_progress", "completed", "abandoned"]
cat_map = {code: [] for code in categories}
cat_map["other"] = []
for name, stored_status in all_data:
    code = status_code_map.get(stored_status, "other")
    cat_map.setdefault(code, []).append(name)

# 构建下拉选项
options = []
headers = []
for code in categories + ["other"]:
    header = f"— {t(code)} —"
    options.append(header)
    headers.append(header)
    options.extend(cat_map.get(code, []))

sel = st.selectbox(t("filter_project"), options)

# 选中后数据展示
if sel in headers:
    idx = headers.index(sel)
    codes = categories + ["other"]
    sel_code = codes[idx]
    display_data = [(n, t(sel_code)) for n in cat_map.get(sel_code, [])]
elif sel:
    # 单项目展示
    original_status = next((s for n, s in all_data if n == sel), "")
    code = status_code_map.get(original_status, "other")
    display_status = t(code) if code in categories else original_status
    display_data = [(sel, display_status)]
else:
    display_data = []

# 渲染项目及操作按钮
if not display_data:
    st.info("暂无项目")
else:
    for pname, disp_status in display_data:
        st.markdown(f"### 🔹 {pname}")
        st.text(f"{t('status')}: {disp_status}")
        owners = [r[0] for r in c.execute("SELECT 姓名 FROM assignments WHERE 项目名称=?", (pname,)).fetchall()]
        st.markdown(f"**{t('owners')}** " + (", ".join(owners) if owners else f"_{t('no_owners')}_"))
        updates = c.execute(
            "SELECT 姓名, 更新时间, 进展说明, 资源需求, 跟进建议 FROM progress_updates WHERE 项目名称=? ORDER BY 更新时间 DESC",
            (pname,)
        ).fetchall()
        if updates:
            st.markdown(f"#### {t('updates')}")
            for row in updates:
                st.write(f"🕓 {row[1]} | 👤 {row[0]}")
                st.markdown(f"- {t('notes')}: {row[2] or '—'}")
                st.markdown(f"- {t('followup')}: {row[4] or '—'}")
                st.markdown('---')
        else:
            st.info(t("no_updates"))
        col1, col2 = st.columns(2)
        with col1:
            if disp_status != t("completed") and disp_status != t("abandoned") and st.button(f"{t('complete')}", key=f"done_{pname}"):
                c.execute("UPDATE projects SET 状态=? WHERE 项目名称=?", (t("completed"), pname))
                conn.commit()
                st.success("✅ 项目已完成")
                if hasattr(st, "experimental_rerun"):
                    st.experimental_rerun()
        with col2:
            if disp_status != t("abandoned") and st.button(f"{t('delete')}", key=f"del_{pname}"):
                c.execute("UPDATE projects SET 状态=? WHERE 项目名称=?", (t("abandoned"), pname))
                conn.commit()
                st.success(f"🗑 项目已标记为{t('abandoned')}")
                if hasattr(st, "experimental_rerun"):
                    st.experimental_rerun()
