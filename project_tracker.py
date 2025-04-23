import streamlit as st
from PIL import Image
import sqlite3
from datetime import datetime, timezone, timedelta
from googletrans import Translator
import socket

# ---------- 多语言静态文本映射 ----------
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
            "completed": "✅ 已完成",
            "abandoned": "🗑 废弃",
            "other": "其他",
            "add": "添加",
            "add_staff": "👤 添加人员",
            "delete_staff": "➖ 删除人员",
            "staff_deleted": "👤 人员已删除",
            "no_staff": "暂无人员",
            "name": "姓名",
            "assign": "🔗 分配项目",
            "upload_progress": "📥 上传进度",
            "your_name": "你的姓名",
            "your_projects": "你的项目",
            "notes": "📄 进展说明",
            "followup": "📌 跟进建议",
            "submit": "提交",
            "complete": "完成项目",
            "delete": "删除项目",
            "language": "🌐 语言",
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
            "completed": "✅ Completed",
            "abandoned": "🗑 Abandoned",
            "other": "Other",
            "add": "Add",
            "add_staff": "👤 Add Staff",
            "delete_staff": "➖ Delete Staff",
            "staff_deleted": "👤 Staff Deleted",
            "no_staff": "No Staff",
            "name": "Name",
            "assign": "🔗 Assign Projects",
            "upload_progress": "📥 Upload Progress",
            "your_name": "Your Name",
            "your_projects": "Your Projects",
            "notes": "📄 Progress Notes",
            "followup": "📌 Follow-up Suggestions",
            "submit": "Submit",
            "complete": "Complete Project",
            "delete": "Delete Project",
            "language": "🌐 Language",
            "owners": "Owners:",
            "no_owners": "No owners",
            "updates": "📈 Update History",
            "no_updates": "No updates",
        },
        "es": {
            "project_overview": "📁 Visión general",
            "filter_project": "🔍 Seleccionar proyecto",
            "all_projects": "Todos los proyectos",
            "add_project": "➕ Agregar proyecto",
            "project_name": "Nombre del proyecto",
            "status": "Estado",
            "not_started": "No iniciado",
            "in_progress": "En progreso",
            "completed": "✅ Completado",
            "abandoned": "🗑 Abandonado",
            "other": "Otro",
            "add": "Agregar",
            "add_staff": "👤 Agregar personal",
            "delete_staff": "➖ Eliminar personal",
            "staff_deleted": "👤 Personal eliminado",
            "no_staff": "Sin personal",
            "name": "Nombre",
            "assign": "🔗 Asignar proyectos",
            "upload_progress": "📥 Cargar progreso",
            "your_name": "Tu nombre",
            "your_projects": "Tus proyectos",
            "notes": "📄 Notas",
            "followup": "📌 Sugerencias",
            "submit": "Enviar",
            "complete": "Completar proyecto",
            "delete": "Eliminar proyecto",
            "language": "🌐 Idioma",
            "owners": "Responsables:",
            "no_owners": "Sin responsables",
            "updates": "📈 Historial",
            "no_updates": "Sin actualizaciones",
        },
        "pt": {
            "project_overview": "📁 Visão geral",
            "filter_project": "🔍 Selecionar projeto",
            "all_projects": "Todos os projetos",
            "add_project": "➕ Adicionar projeto",
            "project_name": "Nome do projeto",
            "status": "Estado",
            "not_started": "Não iniciado",
            "in_progress": "Em andamento",
            "completed": "✅ Concluído",
            "abandoned": "🗑 Abandonado",
            "other": "Outro",
            "add": "Adicionar",
            "add_staff": "👤 Adicionar pessoal",
            "delete_staff": "➖ Excluir pessoal",
            "staff_deleted": "👤 Pessoal excluído",
            "no_staff": "Sem pessoal",
            "name": "Nome",
            "assign": "🔗 Atribuir projetos",
            "upload_progress": "📥 Carregar progresso",
            "your_name": "Seu nome",
            "your_projects": "Seus projetos",
            "notes": "📄 Notas",
            "followup": "📌 Sugestões",
            "submit": "Enviar",
            "complete": "Concluir projeto",
            "delete": "Excluir projeto",
            "language": "🌐 Idioma",
            "owners": "Responsáveis:",
            "no_owners": "Sem responsáveis",
            "updates": "📈 Histórico",
            "no_updates": "Sem atualizações",
        },
    }
    return texts[lang].get(key, key)

# ---------- 翻译工具与环境检测 ----------
translator = Translator()

def is_local():
    try:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        return ip.startswith("192.168.") or ip.startswith("10.") or "DESKTOP-" in host
    except:
        return False

USE_TRANSLATION = st.secrets.get("ENABLE_TRANSLATE", True)
if is_local():
    USE_TRANSLATION = False

def translate_text(text: str) -> str:
    if not text or not USE_TRANSLATION:
        return text
    code_map = {"zh": "zh-cn", "en": "en", "es": "es", "pt": "pt"}
    dest = code_map.get(st.session_state.get("lang", "zh"), "en")
    try:
        return translator.translate(text, dest=dest).text
    except:
        return text

# ---------- 页面配置与样式 ----------
st.set_page_config(page_title="项目管理系统", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    .stButton>button { border-radius: 8px; padding: 0.5rem 1rem; }
    [data-testid=\"stSidebar\"] { background-color: #f0f2f6; }
    .main-header { font-size: 2.5rem; color: #0a3d62; margin-bottom: 1rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Logo 区 ----------
LOGO_PATH = "suntaq_logo.png"
logo = Image.open(LOGO_PATH)
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image(logo, width=100)
with col_title:
    st.markdown(f"<h1 class='main-header'>{t('project_overview')}</h1>", unsafe_allow_html=True)

# ---------- 侧边栏功能 ----------
st.sidebar.image(logo, width=150)
st.sidebar.selectbox(
    t("language"), ["中文", "English", "Español", "Português"],
    index={"zh":0, "en":1, "es":2, "pt":3}[st.session_state.get("lang","zh")], key="lang_selector"
)
st.session_state["lang"] = {"中文":"zh","English":"en","Español":"es","Português":"pt"}[st.session_state.lang_selector]

# 数据库连接与表初始化
conn = sqlite3.connect("project_manager.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS projects (项目名称 TEXT PRIMARY KEY, 状态 TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS staff (姓名 TEXT PRIMARY KEY)")
c.execute("CREATE TABLE IF NOT EXISTS assignments (项目名称 TEXT, 姓名 TEXT, PRIMARY KEY (项目名称, 姓名))")
c.execute(
    """
    CREATE TABLE IF NOT EXISTS progress_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        项目名称 TEXT,
        姓名 TEXT,
        更新时间 TEXT,
        进展说明 TEXT,
        资源需求 TEXT,
        跟进建议 TEXT
    )
    """
)
conn.commit()

# ---------- 添加项目 ----------
with st.sidebar.expander(t("add_project")):
    with st.form("add_project_form", clear_on_submit=True):
        pname = st.text_input(t("project_name"))
        pstatus = st.selectbox(t("status"), [t("not_started"), t("in_progress")])
        if st.form_submit_button(t("add")) and pname:
            try:
                c.execute("INSERT INTO projects (项目名称, 状态) VALUES (?, ?)", (pname, pstatus))
                conn.commit()
                st.success(f"{translate_text(pname)} ✔")
            except sqlite3.IntegrityError:
                st.warning(f"{translate_text(pname)} 已存在")

# ---------- 添加人员 ----------
with st.sidebar.expander(t("add_staff")):
    with st.form("add_staff_form", clear_on_submit=True):
        sname = st.text_input(t("name"))
        if st.form_submit_button(t("add")) and sname:
            try:
                c.execute("INSERT INTO staff (姓名) VALUES (?)", (sname,))
                conn.commit()
                st.success(f"{translate_text(sname)} ✔")
            except sqlite3.IntegrityError:
                st.warning(f"{translate_text(sname)} 已存在")

# ---------- 删除人员 ----------
with st.sidebar.expander(t("delete_staff")):
    with st.form("delete_staff_form", clear_on_submit=True):
        staff_list = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
        if staff_list:
            sel = st.selectbox(t("name"), staff_list)
            if st.form_submit_button(t("delete_staff")):
                c.execute("DELETE FROM staff WHERE 姓名=?", (sel,))
                c.execute("DELETE FROM assignments WHERE 姓名=?", (sel,))
                c.execute("DELETE FROM progress_updates WHERE 姓名=?", (sel,))
                conn.commit()
                st.success(translate_text(t("staff_deleted")))
        else:
            st.info(t("no_staff"))

# ---------- 分配项目与人员 ----------
with st.sidebar.expander(t("assign")):
    with st.form("assign_form", clear_on_submit=True):
        projs = [r[0] for r in c.execute("SELECT 项目名称 FROM projects").fetchall()]
        staff = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
        if projs and staff:
            display = [translate_text(p) for p in projs]
            sel_trans = st.selectbox(t("project_name"), display)
            idx = display.index(sel_trans)
            proj = projs[idx]
            per = st.selectbox(t("name"), staff)
            if st.form_submit_button(t("add")):
                try:
                    c.execute("INSERT INTO assignments (项目名称, 姓名) VALUES (?, ?)", (proj, per))
                    conn.commit()
                    st.success(f"{translate_text(per)} ➜ {translate_text(proj)}")
                except sqlite3.IntegrityError:
                    st.warning(f"{translate_text(per)} ➜ {translate_text(proj)} 已存在")
        else:
            st.info(t("no_owners"))

# ---------- 上传进度 ----------
st.sidebar.markdown(f"### {t('upload_progress')}")
staffs = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
if staffs:
    sel = st.sidebar.selectbox(t("your_name"), staffs)
    my_prjs = [r[0] for r in c.execute("SELECT 项目名称 FROM assignments WHERE 姓名=?", (sel,)).fetchall()]
    if my_prjs:
        with st.sidebar.form("progress_form", clear_on_submit=True):
            display = [translate_text(p) for p in my_prjs]
            sel_trans = st.selectbox(t("your_projects"), display)
            proj = my_prjs[display.index(sel_trans)]
            notes = st.text_area(t("notes"))
            follow = st.text_area(t("followup"))
            if st.form_submit_button(t("submit")):
                now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                c.execute(
                    "INSERT INTO progress_updates (项目名称, 姓名, 更新时间, 进展说明, 资源需求, 跟进建议) VALUES (?, ?, ?, ?, ?, ?)",
                    (proj, sel, now, notes, '', follow)
                )
                conn.commit()
                st.sidebar.success(f"✅ {t('submit')} 成功")
    else:
        st.sidebar.info(t("no_owners"))
else:
    st.sidebar.warning(t("no_staff"))

# ---------- 主界面展示与过滤 ----------
st.subheader(t("project_overview"))
rows = c.execute("SELECT 项目名称, 状态 FROM projects ORDER BY 状态 DESC, 项目名称").fetchall()
ALL_STATUS_TRANSLATIONS = {
    "not_started": ["未开始","Not Started","No iniciado","Não iniciado"],
    "in_progress": ["进行中","In Progress","En progreso","Em andamento"],
    "completed": ["✅ 已完成","✅ Completed","✅ Completado","✅ Concluído"],
    "abandoned": ["🗑 废弃","🗑 Abandoned","🗑 Abandonado","🗑 Abandonado"],
}
status_map = {v: code for code, vs in ALL_STATUS_TRANSLATIONS.items() for v in vs}
cats = list(ALL_STATUS_TRANSLATIONS.keys())
cat_map = {code: [] for code in cats}
cat_map["other"] = []
for n, stt in rows:
    key = status_map.get(stt, "other")
    cat_map[key].append(n)
opts, heads = [], []
for code in cats + ["other"]:
    hdr = f"— {t(code)} —"
    opts.append(hdr)
    heads.append(hdr)
    opts.extend(cat_map[code])
sel = st.selectbox(t("filter_project"), opts)
data = []
if sel in heads:
    idx = heads.index(sel)
    chosen = (cats + ["other"])[idx]
    for pn in cat_map[chosen]:
        data.append((pn, t(chosen) if chosen in cats else chosen))
elif sel:
    orig = next((s for n, s in rows if n == sel), None)
    code = status_map.get(orig, "other")
    data = [(sel, t(code) if code in cats else orig)]

if not data:
    st.info(t("no_updates"))
else:
    for pname, pstatus in data:
        st.markdown(f"### 🔹 {translate_text(pname)}")
        st.text(f"{t('status')}: {pstatus}")
        owners = [r[0] for r in c.execute("SELECT 姓名 FROM assignments WHERE 项目名称=?", (pname,)).fetchall()]
        st.markdown(f"**{t('owners')}** " + ("，".join(translate_text(o) for o in owners) if owners else f"_{t('no_owners')}_"))
        ups = c.execute("SELECT 姓名, 更新时间, 进展说明, 资源需求, 跟进建议 FROM progress_updates WHERE 项目名称=? ORDER BY 更新时间 DESC", (pname,)).fetchall()
        if ups:
            st.markdown(f"#### {t('updates')}")
            for u in ups:
                st.write(f"🕓 {u[1]} | 👤 {translate_text(u[0])}")
                st.markdown(f"- {t('notes')}: {translate_text(u[2]) or '—'}")
                st.markdown(f"- {t('followup')}: {translate_text(u[4]) or '—'}")
                st.markdown('---')
        else:
            st.info(t("no_updates"))
        col1, col2 = st.columns(2)
        with col1:
            if pstatus not in [t("completed"), t("abandoned")] and st.button(t("complete"), key=f"done_{pname}"):
                c.execute("UPDATE projects SET 状态=? WHERE 项目名称=?", (t("completed"), pname))
                conn.commit()
                st.success(t("completed"))
                st.experimental_rerun()
        with col2:
            if pstatus != t("abandoned") and st.button(t("delete"), key=f"del_{pname}"):
                c.execute("UPDATE projects SET 状态=? WHERE 项目名称=?", (t("abandoned"), pname))
                conn.commit()
                st.success(t("abandoned"))
                st.experimental_rerun()
