# -*- coding: utf-8 -*-
"""
salami - برنامه واقعی محاسبات مالی با پایتون
اجرا: streamlit run salami_app.py
"""

import streamlit as st
import json
import os
import traceback
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "salami_data"
DATA_DIR.mkdir(exist_ok=True)
PROJECTS_FILE = DATA_DIR / "projects.json"

def load_projects():
    if PROJECTS_FILE.exists():
        try:
            with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_projects(projects):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def uid():
    return datetime.now().strftime("%Y%m%d%H%M%S") + str(os.urandom(2).hex())

def run_python_code(code: str, input_data: str) -> str:
    safe_globals = {
        "__builtins__": {
            "print": print, "len": len, "str": str, "int": int, "float": float,
            "list": list, "dict": dict, "tuple": tuple, "set": set, "range": range,
            "sum": sum, "min": min, "max": max, "abs": abs, "round": round,
            "sorted": sorted, "enumerate": enumerate, "zip": zip, "map": map,
            "filter": filter, "any": any, "all": all, "isinstance": isinstance,
            "type": type, "True": True, "False": False, "None": None,
        }
    }
    try:
        import re, math, statistics
        safe_globals["re"] = re
        safe_globals["math"] = math
        safe_globals["statistics"] = statistics
    except:
        pass

    local_vars = {"input_data": input_data, "result": None}
    from io import StringIO
    import sys
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()

    try:
        exec(code, safe_globals, local_vars)
        output = captured.getvalue()
        if local_vars.get("result") is not None:
            output += ("\n" if output else "") + str(local_vars["result"])
        if not output.strip():
            output = "(کد اجرا شد اما چیزی چاپ نشد. از print استفاده کنید)"
        return output
    except Exception as e:
        return f"خطا در اجرای کد:\n{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
    finally:
        sys.stdout = old_stdout


st.set_page_config(page_title="salami", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0d0d0d; color: #e8e8e8; }
    [data-testid="stSidebar"] { background-color: #161616; }
    h1, h2, h3 { color: #f0f0f0 !important; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1c1c1c !important;
        color: #e8e8e8 !important;
        border: 1px solid #333 !important;
    }
    .stButton > button {
        background-color: #2a2a2a;
        color: #e8e8e8;
        border: 1px solid #444;
    }
    .stButton > button:hover {
        background-color: #3a3a3a;
        border-color: #666;
    }
</style>
""", unsafe_allow_html=True)

if "projects" not in st.session_state:
    st.session_state.projects = load_projects()
if "current_id" not in st.session_state:
    st.session_state.current_id = None
if "show_new" not in st.session_state:
    st.session_state.show_new = False
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

with st.sidebar:
    st.markdown("## 📊 salami")
    st.caption("محاسبات مالی با پایتون")
    st.divider()

    if st.button("＋ ایجاد پروژه جدید", use_container_width=True, type="primary"):
        st.session_state.show_new = True
        st.session_state.edit_mode = False
        st.session_state.current_id = None
        st.rerun()

    st.markdown("### پروژه‌ها")
    projects = st.session_state.projects

    if not projects:
        st.info("هنوز پروژه‌ای ندارید")
    else:
        sorted_p = sorted(projects, key=lambda x: (not x.get("pinned", False), -x.get("created", 0)))
        for p in sorted_p:
            col1, col2 = st.columns([5, 1])
            with col1:
                label = ("📌 " if p.get("pinned") else "") + p["name"]
                if st.button(label, key=f"sel_{p['id']}", use_container_width=True):
                    st.session_state.current_id = p["id"]
                    st.session_state.show_new = False
                    st.session_state.edit_mode = False
                    st.rerun()
            with col2:
                if st.button("⋯", key=f"menu_{p['id']}"):
                    st.session_state[f"menu_open_{p['id']}"] = not st.session_state.get(f"menu_open_{p['id']}", False)

            if st.session_state.get(f"menu_open_{p['id']}", False):
                if st.button("پین / آنپین", key=f"pin_{p['id']}"):
                    p["pinned"] = not p.get("pinned", False)
                    save_projects(st.session_state.projects)
                    st.rerun()
                if st.button("ویرایش", key=f"edit_{p['id']}"):
                    st.session_state.current_id = p["id"]
                    st.session_state.edit_mode = True
                    st.session_state.show_new = True
                    st.rerun()
                if st.button("حذف", key=f"del_{p['id']}"):
                    st.session_state.projects = [x for x in projects if x["id"] != p["id"]]
                    save_projects(st.session_state.projects)
                    if st.session_state.current_id == p["id"]:
                        st.session_state.current_id = None
                    st.rerun()

st.title("salami")

if st.session_state.show_new:
    is_edit = st.session_state.edit_mode and st.session_state.current_id
    st.subheader("ویرایش پروژه" if is_edit else "ایجاد پروژه جدید")

    default_name = ""
    default_code = """# متغیر input_data حاوی متن صورت مالی است
# نتیجه را با print چاپ کنید

text = input_data
print("طول متن:", len(text))
print("---")
# اینجا محاسبات خود را بنویسید
"""
    if is_edit:
        proj = next((x for x in st.session_state.projects if x["id"] == st.session_state.current_id), None)
        if proj:
            default_name = proj["name"]
            default_code = proj.get("code", default_code)

    name = st.text_input("نام پروژه", value=default_name, placeholder="مثال: تحلیل صورت سود و زیان")
    code = st.text_area("کد پایتون (دستورالعمل محاسبه)", value=default_code, height=220)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("💾 ذخیره", type="primary", use_container_width=True):
            if not name.strip():
                st.error("نام پروژه را وارد کنید")
            elif not code.strip():
                st.error("کد پایتون را وارد کنید")
            else:
                if is_edit and proj:
                    proj["name"] = name.strip()
                    proj["code"] = code.strip()
                    st.success("پروژه به‌روزرسانی شد")
                else:
                    new_p = {
                        "id": uid(),
                        "name": name.strip(),
                        "code": code.strip(),
                        "pinned": False,
                        "created": int(datetime.now().timestamp()),
                        "analyses": []
                    }
                    st.session_state.projects.append(new_p)
                    st.session_state.current_id = new_p["id"]
                    st.success("پروژه ساخته شد")
                save_projects(st.session_state.projects)
                st.session_state.show_new = False
                st.session_state.edit_mode = False
                st.rerun()
    with col_b:
        if st.button("انصراف", use_container_width=True):
            st.session_state.show_new = False
            st.session_state.edit_mode = False
            st.rerun()
    with col_c:
        if is_edit and st.button("🗑 حذف پروژه", use_container_width=True):
            st.session_state.projects = [x for x in st.session_state.projects if x["id"] != st.session_state.current_id]
            save_projects(st.session_state.projects)
            st.session_state.current_id = None
            st.session_state.show_new = False
            st.rerun()

elif st.session_state.current_id:
    proj = next((x for x in st.session_state.projects if x["id"] == st.session_state.current_id), None)
    if not proj:
        st.warning("پروژه پیدا نشد")
        st.session_state.current_id = None
    else:
        st.subheader(f"📁 {proj['name']}")
        with st.expander("مشاهده کد پایتون پروژه", expanded=False):
            st.code(proj.get("code", ""), language="python")

        st.markdown("### متن صورت مالی / ورودی")
        input_text = st.text_area(
            "متن را اینجا وارد کنید",
            height=200,
            placeholder="صورت‌های مالی یا هر داده متنی که می‌خواهید محاسبه شود را اینجا بنویسید...",
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            run_clicked = st.button("▶ اجرای محاسبه", type="primary", use_container_width=True)
        with col2:
            save_anal = st.button("💾 ذخیره این تحلیل", use_container_width=True)

        if run_clicked:
            if not input_text.strip():
                st.warning("ابتدا متن ورودی را بنویسید")
            else:
                with st.spinner("در حال محاسبه..."):
                    result = run_python_code(proj.get("code", ""), input_text)
                st.markdown("### نتیجه محاسبه")
                st.code(result, language=None)
                st.session_state.last_input = input_text
                st.session_state.last_output = result

        if save_anal:
            if "last_output" not in st.session_state:
                st.warning("اول محاسبه را اجرا کنید")
            else:
                anal_name = st.text_input("نام تحلیل", value=f"تحلیل {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                if st.button("تأیید ذخیره"):
                    if "analyses" not in proj:
                        proj["analyses"] = []
                    proj["analyses"].append({
                        "id": uid(),
                        "name": anal_name or "بدون نام",
                        "input": st.session_state.get("last_input", ""),
                        "output": st.session_state.get("last_output", ""),
                        "created": int(datetime.now().timestamp())
                    })
                    save_projects(st.session_state.projects)
                    st.success("تحلیل ذخیره شد")
                    st.rerun()

        analyses = proj.get("analyses", [])
        if analyses:
            st.markdown("---")
            st.markdown("### تحلیل‌های ذخیره‌شده")
            for a in sorted(analyses, key=lambda x: -x.get("created", 0)):
                with st.expander(f"📄 {a['name']} — {datetime.fromtimestamp(a.get('created',0)).strftime('%Y-%m-%d %H:%M')}"):
                    st.markdown("**ورودی:**")
                    st.text(a.get("input", "")[:500] + ("..." if len(a.get("input","")) > 500 else ""))
                    st.markdown("**خروجی:**")
                    st.code(a.get("output", ""), language=None)
                    if st.button("حذف این تحلیل", key=f"delanal_{a['id']}"):
                        proj["analyses"] = [x for x in analyses if x["id"] != a["id"]]
                        save_projects(st.session_state.projects)
                        st.rerun()

else:
    st.info("از منوی سمت چپ یک پروژه انتخاب کنید یا پروژه جدید بسازید.")
    st.markdown("""
    ### راهنمای سریع
    1. روی **ایجاد پروژه جدید** کلیک کنید
    2. نام پروژه و کد پایتون را بنویسید
    3. در کد از متغیر `input_data` استفاده کنید و با `print` خروجی بگیرید
    4. پروژه را ذخیره کنید
    5. متن صورت مالی را وارد کنید و **اجرای محاسبه** را بزنید
    """)