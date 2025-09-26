import streamlit as st
import pandas as pd
import os
import hashlib

# -------------------- Data Files --------------------
DATA_FILE = "data/blood_donors.csv"
USER_FILE = "data/users.csv"

os.makedirs("data", exist_ok=True)

# -------------------- Helper Functions --------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        cols = ["ID", "Name", "Age", "Gender", "Blood Group", "Contact"]
        return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    else:
        cols = ["Username", "Password"]
        return pd.DataFrame(columns=cols)

def save_users(df):
    df.to_csv(USER_FILE, index=False)

# -------------------- Donor Functions --------------------
def add_donor(name, age, gender, blood_group, contact):
    df = load_data()
    new_id = 101 if df.empty else df["ID"].max() + 1
    new_row = {
        "ID": new_id,
        "Name": name,
        "Age": age,
        "Gender": gender,
        "Blood Group": blood_group,
        "Contact": contact
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    st.success("✅ Donor added successfully!")

def view_donors():
    df = load_data()
    if df.empty:
        st.info("No donor records yet.")
    else:
        st.subheader("Filter Donors by Blood Group")
        blood_filter = st.selectbox(
            "Select Blood Group",
            ["All", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        )

        filtered_df = df.copy()
        if blood_filter != "All":
            filtered_df = filtered_df[filtered_df["Blood Group"] == blood_filter]

        st.dataframe(filtered_df)
        st.write(f"Total Donors Shown: {len(filtered_df)}")

def edit_donor():
    df = load_data()
    if df.empty:
        st.info("No donor records to edit.")
        return
    donor_id = st.number_input("Enter Donor ID to edit:", min_value=101, step=1)
    if donor_id in df["ID"].values:
        donor = df[df["ID"] == donor_id].iloc[0]
        name = st.text_input("Name", donor["Name"])
        age = st.number_input("Age", 18, 65, int(donor.get("Age", 18)))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male","Female","Other"].index(donor["Gender"]))
        blood_group = st.selectbox(
            "Blood Group",
            ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            index=["A+","A-","B+","B-","AB+","AB-","O+","O-"].index(donor["Blood Group"])
        )
        contact = st.text_input("Contact", donor["Contact"])
        if st.button("Update"):
            if not contact.isdigit() or len(contact) != 10:
                st.error("Contact number must be exactly 10 digits.")
            elif name.strip() == "":
                st.error("Name cannot be empty.")
            else:
                df.loc[df["ID"] == donor_id, ["Name","Age","Gender","Blood Group","Contact"]] = \
                    [name, age, gender, blood_group, contact]
                save_data(df)
                st.success("✅ Donor details updated.")
    else:
        st.warning("ID not found.")

def search_donor():
    df = load_data()
    if df.empty:
        st.info("No donor records to search.")
        return

    st.subheader("Filter Donors by Blood Group")
    blood_filter = st.selectbox(
        "Select Blood Group",
        ["All", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    )

    filtered_df = df.copy()
    if blood_filter != "All":
        filtered_df = filtered_df[filtered_df["Blood Group"] == blood_filter]

    if filtered_df.empty:
        st.warning("No matching donors found.")
    else:
        st.dataframe(filtered_df)
        st.write(f"Total Donors Shown: {len(filtered_df)}")

# -------------------- Authentication --------------------
def register():
    st.header("🔑 Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
            return
        if username.strip() == "" or password.strip() == "":
            st.error("Username and password cannot be empty")
            return
        users = load_users()
        if username in users["Username"].values:
            st.error("Username already exists")
            return
        new_user = {"Username": username, "Password": hash_password(password)}
        users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
        save_users(users)
        st.success("✅ Registration successful. Please login.")

def login():
    st.header("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        hashed_pw = hash_password(password)
        if ((users["Username"] == username) & (users["Password"] == hashed_pw)).any():
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password")

# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="Blood Donation Management", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# -------------------- Login/Register --------------------
if not st.session_state["logged_in"]:
    menu = ["Login", "Register"]
    choice = st.sidebar.radio("Menu", menu)
    if choice == "Login":
        login()
    elif choice == "Register":
        register()
else:
    # -------------------- Top Logout Button --------------------
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.stop()

    st.title(f"🩸 Blood Donation Management System - User: {st.session_state['username']}")
    menu = ["Add Donor", "View Donors", "Edit Donor", "Search"]
    choice = st.sidebar.radio("Menu", menu)

    if choice == "Add Donor":
        st.header("Add New Donor")
        name = st.text_input("Name")
        age = st.number_input("Age", 18, 65, 18)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        contact = st.text_input("Contact Number (10 digits)")
        if st.button("Submit"):
            if not contact.isdigit() or len(contact) != 10:
                st.error("Contact number must be exactly 10 digits.")
            elif name.strip() == "":
                st.error("Name cannot be empty.")
            else:
                add_donor(name, age, gender, blood_group, contact)

    elif choice == "View Donors":
        st.header("All Donors")
        view_donors()

    elif choice == "Edit Donor":
        st.header("Edit Donor Details")
        edit_donor()

    elif choice == "Search":
        st.header("Search Donors")
        search_donor()
