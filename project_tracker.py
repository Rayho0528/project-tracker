import streamlit as st
from PIL import Image
import sqlite3
from datetime import datetime, timezone, timedelta
import socket

# 可选导入翻译库
try:
    from googletrans import Translator
    translator = Translator()
    HAVE_TRANSLATOR = True
except ImportError:
    HAVE_TRANSLATOR = False
    translator = None

# 多语言静态文本映射
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

# 本地检测与翻译开关
def is_local():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        return ip.startswith("192.168.") or ip.startswith("10.")
    except:
        return False

USE_TRANSLATION = HAVE_TRANSLATOR and not is_local()

def translate_text(txt: str) -> str:
    if not txt or not USE_TRANSLATION:
        return txt
    lang_code = {"zh":"zh-cn","en":"en","es":"es","pt":"pt"}[st.session_state.get("lang","zh")]
    try:
        return translator.translate(txt, dest=lang_code).text
    except:
        return txt

# 页面布局与样式
st.set_page_config(page_title="项目管理系统", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.stButton>button { border-radius: 8px; padding: 0.5rem 1rem; }
[data-testid=\"stSidebar\"] { background-color: #f0f2f6; }
.main-header { font-size: 2.5rem; color: #0a3d62; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# Logo & 标题
LOGO_PATH = "suntaq_logo.png"
logo_img = Image.open(LOGO_PATH)
col_logo, col_title = st.columns([1,6])
with col_logo:
    st.image(logo_img, width=100)
with col_title:
    st.markdown(f"<h1 class='main-header'>{t('project_overview')}</h1>", unsafe_allow_html=True)

# 侧边栏 菜单
st.sidebar.image(logo_img, width=120)
st.sidebar.selectbox(t("language"), ["中文","English","Español","Português"], index={"zh":0,"en":1,"es":2,"pt":3}[st.session_state.get("lang","zh")], key="lang_selector")
st.session_state["lang"] = {"中文":"zh","English":"en","Español":"es","Português":"pt"}[st.session_state.lang_selector]

# 数据库连接
conn = sqlite3.connect("project_manager.db", check_same_thread=False)
c = conn.cursor()
# 初始化表
c.execute("CREATE TABLE IF NOT EXISTS projects (项目名称 TEXT PRIMARY KEY, 状态 TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS staff (姓名 TEXT PRIMARY KEY)")
c.execute("CREATE TABLE IF NOT EXISTS assignments (项目名称 TEXT, 姓名 TEXT, PRIMARY KEY (项目名称, 姓名))")
c.execute("""
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

# 添加项目
with st.sidebar.expander(t("add_project")):
    with st.form("add_project_form", clear_on_submit=True):
        new_p = st.text_input(t("project_name"))
        new_s = st.selectbox(t("status"), [t("not_started"), t("in_progress")])
        if st.form_submit_button(t("add")) and new_p:
            try:
                c.execute("INSERT INTO projects VALUES (?,?)", (new_p, new_s))
                conn.commit()
                st.success(translate_text(new_p)+" ✔")
            except sqlite3.IntegrityError:
                st.warning(translate_text(new_p)+" 已存在")

# 添加人员
with st.sidebar.expander(t("add_staff")):
    with st.form("add_staff_form", clear_on_submit=True):
        new_name = st.text_input(t("name"))
        if st.form_submit_button(t("add")) and new_name:
            try:
                c.execute("INSERT INTO staff VALUES (?)", (new_name,))
                conn.commit()
                st.success(translate_text(new_name)+" ✔")
            except sqlite3.IntegrityError:
                st.warning(translate_text(new_name)+" 已存在")

# 删除人员
with st.sidebar.expander(t("delete_staff")):
    with st.form("del_staff_form", clear_on_submit=True):
        staff_list = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
        if staff_list:
            sel_n = st.selectbox(t("name"), staff_list)
            if st.form_submit_button(t("delete_staff")):
                c.execute("DELETE FROM staff WHERE 姓名=?", (sel_n,))
                c.execute("DELETE FROM assignments WHERE 姓名=?", (sel_n,))
                c.execute("DELETE FROM progress_updates WHERE 姓名=?", (sel_n,))
                conn.commit()
                st.success(translate_text(sel_n)+" 删除成功")
        else:
            st.info(t("no_staff"))

# 分配项目
with st.sidebar.expander(t("assign")):
    with st.form("assign_form2", clear_on_submit=True):
        proj_list = [r[0] for r in c.execute("SELECT 项目名称 FROM projects").fetchall()]
        staff_list = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
        if proj_list and staff_list:
            disp = [translate_text(p) for p in proj_list]
            sel_disp = st.selectbox(t("project_name"), disp)
            proj_sel = proj_list[disp.index(sel_disp)]
            name_sel = st.selectbox(t("name"), staff_list)
            if st.form_submit_button(t("add")):
                try:
                    c.execute("INSERT INTO assignments VALUES (?,?)", (proj_sel, name_sel))
                    conn.commit()
                    st.success(translate_text(name_sel)+" ➜ "+translate_text(proj_sel))
                except sqlite3.IntegrityError:
                    st.warning("已存在")
        else:
            st.info(t("no_owners"))

# 上传进度
st.sidebar.markdown(f"### {t('upload_progress')}")
staff_list2 = [r[0] for r in c.execute("SELECT 姓名 FROM staff").fetchall()]
if staff_list2:
    sel_n2 = st.sidebar.selectbox(t("your_name"), staff_list2)
    myp_list = [r[0] for r in c.execute("SELECT 项目名称 FROM assignments WHERE 姓名=?",(sel_n2,)).fetchall()]
    if myp_list:
        with st.sidebar.form("progress_form2", clear_on_submit=True):
            disp2 = [translate_text(p) for p in myp_list]
            sel_disp2 = st.selectbox(t("your_projects"), disp2)
            proj2 = myp_list[disp2.index(sel_disp2)]
            notes2 = st.text_area(t("notes"))
            follow2 = st.text_area(t("followup"))
            if st.form_submit_button(t("submit")):
                now2 = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO progress_updates VALUES (NULL,?,?,?,?,?,?)",(proj2,sel_n2,now2,notes2,'',follow2))
                conn.commit()
                st.sidebar.success(t("submit")+" 成功")
    else:
        st.sidebar.info(t("no_owners"))
else:
    st.sidebar.warning(t("no_staff"))

# 主界面展示过滤
st.subheader(t("project_overview"))
rows2 = c.execute("SELECT 项目名称, 状态 FROM projects ORDER BY 状态 DESC, 项目名称").fetchall()
sm = {v:k for k,vs in ALL_STATUS_TRANSLATIONS.items() for v in vs}
codes = list(ALL_STATUS_TRANSLATIONS.keys())
cm = {code:[] for code in codes}
cm['other']=[]
for nm,stt in rows2:
    cm[sm.get(stt,'other')].append(nm)
opts2,heads2=[],[]
for cod in codes+['other']:
    hd=f"— {t(cod)} —"
    opts2.append(hd)
    heads2.append(hd)
    opts2.extend(cm[cod])
sel3=st.selectbox(t("filter_project"),opts2)
data2=[]
if sel3 in heads2:
    idx3=heads2.index(sel3)
    cho3=(codes+['other'])[idx3]
    for pn3 in cm[cho3]: data2.append((pn3,t(cho3) if cho3 in codes else cho3))
elif sel3:
    orig3=next((s for n,s in rows2 if n==sel3),None)
    cd=sm.get(orig3,'other')
    data2=[(sel3,t(cd) if cd in codes else orig3)]

if not data2:
    st.info(t("no_updates"))
else:
    for nm4,st4 in data2:
        st.markdown(f"### 🔹 {translate_text(nm4)}")
        st.text(f"{t('status')}: {st4}")
        own4=[r[0] for r in c.execute("SELECT 姓名 FROM assignments WHERE 项目名称=?",(nm4,)).fetchall()]
        st.markdown(f"**{t('owners')}** "+("，".join(translate_text(o) for o in own4) if own4 else f"_{t('no_owners')}_"))
        ups4=c.execute("SELECT 姓名, 更新时间, 进展说明, 资源需求, 跟进建议 FROM progress_updates WHERE 项目名称=? ORDER BY 更新时间 DESC",(nm4,)).fetchall()
        if ups4:
            st.markdown(f"#### {t('updates')}")
            for u4 in ups4:
                st.write(f"🕓 {u4[1]} | 👤 {translate_text(u4[0])}")
                st.markdown(f"- {t('notes')}: {translate_text(u4[2]) or '—'}")
                st.markdown(f"- {t('followup')}: {translate_text(u4[4]) or '—'}")
                st.markdown('---')
        else:
            st.info(t("no_updates"))
        c1,c2=st.columns(2)
        with c1:
            if st4 not in [t('completed'),t('abandoned')] and st.button(t('complete'),key=f"done_{nm4}"):
                c.execute("UPDATE projects SET 状态=? WHERE 项目名称=?",(t('completed'),nm4))
                conn.commit();st.success(t('completed'));st.experimental_rerun()
        with c2:
            if st4!=t('abandoned') and st.button(t('delete'),key=f"del_{nm4}"):
                c.execute("UPDATE projects SET 状态=? WHERE 项目名称=?",(t('abandoned'),nm4))
                conn.commit();st.success(t('abandoned'));st.experimental_rerun()

