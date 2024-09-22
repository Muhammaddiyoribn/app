import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# FastAPI backend URL
API_URL = "https://seashell-app-5ly42.ondigitalocean.app"

# Set page config
st.set_page_config(layout="wide", page_title="IqroAI", page_icon="🧠")

# Custom CSS for improved aesthetics and scarf banner
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 20px;
    }
    .stTextInput, .stTextArea, .stDateInput, .stNumberInput {
        border-radius: 10px;
    }
    .reportcard {
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .scarf-banner {
        background: linear-gradient(45deg, #f3ec78, #af4261);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
        color: white;
    .tit {
        color: #ffffff
        }
    }
</style>
""", unsafe_allow_html=True)

# Add scarf banner
st.markdown('<div class="scarf-banner"><h1 class="tit">IqroAI Learning Assistant</h1></div>', unsafe_allow_html=True)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chats" not in st.session_state:
    st.session_state.chats = []
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "language" not in st.session_state:
    st.session_state.language = "en"

# Language dictionaries
languages = {
    "en": {
        "title": "IqroAI Learning Assistant",
        "login": "Login",
        "register": "Register",
        "email": "Email",
        "password": "Password",
        "first_name": "First Name",
        "last_name": "Last Name",
        "birth_date": "Birth Date",
        "phone_number": "Phone Number",
        "grade": "Grade",
        "interests": "Interests (comma-separated)",
        "consent": "I agree to the terms and conditions",
        "submit": "Submit",
        "logout": "Logout",
        "chat": "Chat",
        "profile": "Profile",
        "reports": "Reports",
        "new_chat": "New Chat",
        "generate_report": "Generate New Report",
        "no_reports": "No reports available. Please generate a new report.",
        "welcome": "Welcome to IqroAI Learning Assistant!",
        "description": "IqroAI is your personal AI-powered learning companion. It's designed to help students in Uzbekistan with their studies, providing personalized assistance, and tracking academic progress.",
        "ask_iqroai": "What would you like to ask IqroAI?",
        "update_profile": "Update Profile",
        "profile_updated": "Profile updated successfully!",
        "profile_update_failed": "Failed to update profile: ",
        "subject_performance": "Subject Performance",
        "percentage": "Percentage",
        "grade": "Grade",
        "report_table": "Report Table",
        "subject": "Subject"
    },
    "uz": {
        "title": "IqroAI O'quv Yordamchisi",
        "login": "Kirish",
        "register": "Ro'yxatdan o'tish",
        "email": "Elektron pochta",
        "password": "Parol",
        "first_name": "Ism",
        "last_name": "Familiya",
        "birth_date": "Tug'ilgan sana",
        "phone_number": "Telefon raqami",
        "grade": "Sinf",
        "interests": "Qiziqishlar (vergul bilan ajratilgan)",
        "consent": "Foydalanish shartlariga roziman",
        "submit": "Yuborish",
        "logout": "Chiqish",
        "chat": "Muloqot",
        "profile": "Profil",
        "reports": "Hisobotlar",
        "new_chat": "Yangi muloqot",
        "generate_report": "Yangi hisobot yaratish",
        "no_reports": "Hisobotlar mavjud emas. Iltimos, yangi hisobot yarating.",
        "welcome": "IqroAI O'quv Yordamchisiga xush kelibsiz!",
        "description": "IqroAI - bu shaxsiy AI-quvvatli o'quv yordamchingiz. U O'zbekistondagi o'quvchilarga o'qishlarida yordam berish, shaxsiy yordam ko'rsatish va akademik yutuqlarni kuzatib borish uchun mo'ljallangan.",
        "ask_iqroai": "IqroAI'dan nimani so'ramoqchisiz?",
        "update_profile": "Profilni yangilash",
        "profile_updated": "Profil muvaffaqiyatli yangilandi!",
        "profile_update_failed": "Profilni yangilashda xatolik yuz berdi: ",
        "subject_performance": "Fan bo'yicha natijalar",
        "percentage": "Foiz",
        "grade": "Baho",
        "report_table": "Hisobot jadvali",
        "subject": "Fan"
    },
    "ru": {
        "title": "Обучающий ассистент IqroAI",
        "login": "Вход",
        "register": "Регистрация",
        "email": "Электронная почта",
        "password": "Пароль",
        "first_name": "Имя",
        "last_name": "Фамилия",
        "birth_date": "Дата рождения",
        "phone_number": "Номер телефона",
        "grade": "Класс",
        "interests": "Интересы (разделенные запятыми)",
        "consent": "Я согласен с условиями использования",
        "submit": "Отправить",
        "logout": "Выйти",
        "chat": "Чат",
        "profile": "Профиль",
        "reports": "Отчеты",
        "new_chat": "Новый чат",
        "generate_report": "Создать новый отчет",
        "no_reports": "Отчеты отсутствуют. Пожалуйста, создайте новый отчет.",
        "welcome": "Добро пожаловать в обучающий ассистент IqroAI!",
        "description": "IqroAI - это ваш личный AI-помощник в обучении. Он разработан для помощи ученикам в Узбекистане в их учебе, предоставляя персонализированную поддержку и отслеживая академический прогресс.",
        "ask_iqroai": "Что бы вы хотели спросить у IqroAI?",
        "update_profile": "Обновить профиль",
        "profile_updated": "Профиль успешно обновлен!",
        "profile_update_failed": "Не удалось обновить профиль: ",
        "subject_performance": "Успеваемость по предметам",
        "percentage": "Процент",
        "grade": "Оценка",
        "report_table": "Таблица отчета",
        "subject": "Предмет"
    }
}

# Helper functions
def login_user(email, password):
    response = requests.post(f"{API_URL}/token", data={"username": email, "password": password})
    if response.status_code == 200:
        data = response.json()
        st.session_state.access_token = data["access_token"]
        st.session_state.user_id = get_user_info()["id"]
        st.success("Login successful!")
        st.rerun()
    else:
        st.error("Invalid credentials. Please try again.")

def register_user(user_data):
    response = requests.post(f"{API_URL}/register_student", json=user_data)
    if response.status_code == 200:
        st.success("Registration successful! Please log in.")
    else:
        st.error(f"Registration failed: {response.json()['detail']}")

def get_user_info():
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{API_URL}/users/me/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch user information")
        return None

def get_user_chats():
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{API_URL}/chats", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch chats")
        return []

def get_chat_messages(chat_id):
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{API_URL}/chats/{chat_id}/messages", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch messages")
        return []

def update_chat_name(chat_id, new_name):
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.put(f"{API_URL}/chats/{chat_id}", params={"name": new_name}, headers=headers)
    if response.status_code == 200:
        st.success("Chat name updated successfully")
    else:
        st.error("Failed to update chat name")

def delete_chat(chat_id):
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.delete(f"{API_URL}/chats/{chat_id}", headers=headers)
    if response.status_code == 200:
        st.success("Chat deleted successfully")
        st.session_state.chat_id = None
        st.session_state.messages = []
        st.rerun()
    else:
        st.error("Failed to delete chat")

def generate_report():
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    with st.spinner("Generating report... This may take a moment."):
        response = requests.post(f"{API_URL}/ai_hisobot", headers=headers)
    if response.status_code == 200:
        st.session_state.report_data = response.json()
        st.success("Report generated successfully!")
    else:
        st.error("Failed to generate report")

def get_student_reports():
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{API_URL}/student_reports", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch student reports")
        return []

def language_selector():
    cols = st.columns(3)
    if cols[0].button("🇺🇿 O'zbek"):
        st.session_state.language = "uz"
        st.rerun()
    if cols[1].button("🇬🇧 English"):
        st.session_state.language = "en"
        st.rerun()
    if cols[2].button("🇷🇺 Русский"):
        st.session_state.language = "ru"
        st.rerun()

def display_chat_interface(lang):
    st.subheader(lang["chat"])
    
    # Chat selection sidebar
    with st.sidebar:
        st.subheader(lang["chat"])
        
        # Fetch user's chats
        st.session_state.chats = get_user_chats()
        
        # Display chats in sidebar with delete button
        for chat in st.session_state.chats:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button(chat["name"], key=f"chat_{chat['id']}"):
                    st.session_state.chat_id = chat["id"]
                    st.session_state.messages = get_chat_messages(chat["id"])
                    st.rerun()
            with col2:
                if st.button("🖊", key=f"edit_{chat['id']}"):
                    new_name = st.text_input("New chat name", value=chat["name"], key=f"new_name_{chat['id']}")
                    if st.button("Update", key=f"update_{chat['id']}"):
                        update_chat_name(chat["id"], new_name)
                        st.rerun()
            with col3:
                if st.button("🗑", key=f"delete_{chat['id']}"):
                    delete_chat(chat["id"])
        
        # New Chat button
        if st.button(lang["new_chat"]):
            st.session_state.chat_id = None
            st.session_state.messages = []
            st.rerun()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(lang["ask_iqroai"]):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Send request to AI assistant
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            data = {
                "query": prompt,
                "chat_id": st.session_state.chat_id
            }
            with requests.post(f"{API_URL}/ai_assistant", json=data, headers=headers, stream=True) as r:
                if r.status_code != 200:
                    st.error("Failed to get response from AI assistant")
                else:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            full_response += chunk.decode()
                            message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Update chat_id if it's a new chat
        if not st.session_state.chat_id:
            st.session_state.chats = get_user_chats()
            if st.session_state.chats:
                st.session_state.chat_id = st.session_state.chats[-1]["id"]
            st.rerun()

def display_profile(lang):
    st.subheader(lang["profile"])
    
    # Fetch current user data
    user_data = get_user_info()
    
    if user_data:
        with st.form("edit_profile_form"):
            first_name = st.text_input(lang["first_name"], value=user_data["first_name"])
            last_name = st.text_input(lang["last_name"], value=user_data["last_name"])
            email = st.text_input(lang["email"], value=user_data["email"])
            birth_date = st.date_input(lang["birth_date"], value=datetime.strptime(user_data["birth_date"], "%Y-%m-%d").date())
            phone_number = st.text_input(lang["phone_number"], value=user_data["phone_number"])
            grade = st.number_input(lang["grade"], value=user_data["grade"], min_value=1, max_value=12)
            interests = st.text_area(lang["interests"], value=user_data.get("interests", ""))
            
            update_button = st.form_submit_button(lang["update_profile"])
            
            if update_button:
                updated_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "birth_date": str(birth_date),
                    "phone_number": phone_number,
                    "grade": grade,
                    "interests": interests
                }
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                response = requests.put(f"{API_URL}/users/me", json=updated_data, headers=headers)
                if response.status_code == 200:
                    st.success(lang["profile_updated"])
                else:
                    st.error(f"{lang['profile_update_failed']}{response.json()['detail']}")

def display_reports(lang):
    st.subheader(lang["reports"])

    # Button to generate a new report
    if st.button(lang["generate_report"]):
        generate_report()

    # Fetch and display existing reports
    reports = get_student_reports()
    
    if reports:
        display_report_charts(reports, lang)
    else:
        st.warning(lang["no_reports"])

def display_report_charts(report_data, lang):
    if report_data:
        df = pd.DataFrame(report_data)
        
        # Bar chart for percentages
        fig_percentage = px.bar(df, x='subject', y='percentage', title=f"{lang['subject_performance']} ({lang['percentage']})")
        st.plotly_chart(fig_percentage, use_container_width=True)
        
        # Line chart for grades
        fig_grade = px.line(df, x='subject', y='grade', title=f"{lang['subject_performance']} ({lang['grade']})", markers=True)
        st.plotly_chart(fig_grade, use_container_width=True)
        
        # Display the report table
        st.subheader(lang["report_table"])
        st.table(df[[lang['subject'], lang['percentage'], lang['grade']]])
    else:
        st.warning(lang["no_reports"])

def main():
    lang = languages[st.session_state.language]

    if not st.session_state.user_id:
        language_selector()
        
        st.write(lang["welcome"])
        st.write(lang["description"])
        
        tab1, tab2 = st.tabs([lang["login"], lang["register"]])
        
        with tab1:
            st.subheader(lang["login"])
            email = st.text_input(lang["email"], key="login_email")
            password = st.text_input(lang["password"], type="password", key="login_password")
            if st.button(lang["login"]):
                login_user(email, password)
        
        with tab2:
            st.subheader(lang["register"])
            with st.form("registration_form"):
                first_name = st.text_input(lang["first_name"])
                last_name = st.text_input(lang["last_name"])
                email = st.text_input(lang["email"])
                password = st.text_input(lang["password"], type="password")
                birth_date = st.date_input(lang["birth_date"])
                phone_number = st.text_input(lang["phone_number"])
                grade = st.number_input(lang["grade"], min_value=1, max_value=12)
                interests = st.text_area(lang["interests"])
                consent = st.checkbox(lang["consent"])
                
                submit_button = st.form_submit_button(lang["submit"])
                
                if submit_button:
                    if not consent:
                        st.error("You must agree to the terms and conditions to register.")
                    else:
                        user_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email,
                            "password": password,
                            "role": "student",
                            "birth_date": str(birth_date),
                            "phone_number": phone_number,
                            "grade": grade,
                            "interests": interests,
                            "consent": "true"
                        }
                        register_user(user_data)
    else:
        # Main menu using option_menu
        selected = option_menu(
            menu_title=None,
            options=[lang["chat"], lang["profile"], lang["reports"], lang["logout"]],
            icons=['chat', 'person', 'file-text', 'box-arrow-right'],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
        
        if selected == lang["logout"]:
            st.session_state.clear()
            st.rerun()
        elif selected == lang["chat"]:
            display_chat_interface(lang)
        elif selected == lang["profile"]:
            display_profile(lang)
        elif selected == lang["reports"]:
            display_reports(lang)

if __name__ == "__main__":
    main()
