import streamlit as st
import sqlite3

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Honda Showroom", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

body, .main {
    background-color: white;
}

h1, h2, h3 {
    color: #CC0000;
    font-weight: 700;
}

.stButton>button {
    background-color: #CC0000;
    color: white;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    border: 2px solid black;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: white;
    color: #CC0000;
    border: 2px solid #CC0000;
}

section[data-testid="stSidebar"] {
    background-color: #CC0000;
}

section[data-testid="stSidebar"] * {
    color: white;
}

input, textarea {
    border: 2px solid black !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGO ----------------
st.image("logo.png", width=480)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>Golden Honda Showroom Assistance</h1>", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("showroom.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bikes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    price TEXT,
    engine TEXT,
    fuel_avg TEXT,
    top_speed TEXT,
    stock INTEGER
)
""")

conn.commit()

# ---------------- ADMIN ----------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ---------------- SAMPLE DATA ----------------
def add_sample_data():
    cursor.execute("SELECT COUNT(*) FROM bikes")
    if cursor.fetchone()[0] == 0:
        bikes = [
            ("Honda CD 70", "Commuter", "PKR 159,900/=", "70cc", "60 km/l", "75 km/h", 15),
            ("CD 70 Dream", "Commuter", "PKR 170,900/=", "72cc", "65 km/l", "75 km/h", 20),
            ("Honda CG125", "Commuter", "PKR 295,000/=", "125cc", "35 km/l", "100 km/h", 10),
            ("Honda Pridor 100", "Commuter", "PKR 211,900/=", "100cc", "50 km/l", "95 km/h", 3),
            ("Honda CB 150F", "Mid-range street bike", "PKR 503,900/=", "150cc", "35 km/l", "115 km/h", 2),
        ]
        cursor.executemany("INSERT INTO bikes VALUES (NULL,?,?,?,?,?,?,?)", bikes)
        conn.commit()

add_sample_data()

# ---------------- HELPERS ----------------
def normalize(text):
    return text.lower().replace(" ", "")

def parse_price(price):
    return int("".join(filter(str.isdigit, price)))

def get_all_bikes():
    cursor.execute("SELECT * FROM bikes")
    return cursor.fetchall()

def get_bike_names():
    cursor.execute("SELECT name FROM bikes")
    return [row[0] for row in cursor.fetchall()]

def get_bike_by_name(name):
    cursor.execute("SELECT * FROM bikes")
    for b in cursor.fetchall():
        if normalize(name) == normalize(b[1]):
            return b
    return None

# ---------------- RECOMMENDATION (UPDATED) ----------------
def recommend(budget):
    bikes = get_all_bikes()

    results = []
    for b in bikes:
        price = parse_price(b[3])
        diff = abs(price - budget)
        results.append((diff, b))

    results.sort(key=lambda x: x[0])
    return [r[1] for r in results[:3]]  # top 3 closest

# ---------------- STOCK ----------------
def check_stock(name):
    for b in get_all_bikes():
        if normalize(name) in normalize(b[1]):
            return b[7], b[0]
    return None

def update_stock(bike_id, new_stock):
    cursor.execute("UPDATE bikes SET stock=? WHERE id=?", (new_stock, bike_id))
    conn.commit()

def delete_bike(bike_id):
    cursor.execute("DELETE FROM bikes WHERE id=?", (bike_id,))
    conn.commit()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox(
    "Choose Feature",
    [
        "Home",
        "View Bikes",
        "Bike Details",
        "Recommendation System",
        "Compare Bikes",
        "Availability Checker",
        "EMI Calculator",
        "Admin Login"
    ]
)

# ---------------- HOME ----------------
if menu == "Home":
    st.markdown("""
    <h2>Welcome 👋</h2>
    <h4>Your smart bike buying assistant 🚀</h4>
    """, unsafe_allow_html=True)

# ---------------- VIEW ----------------
elif menu == "View Bikes":
    st.subheader("🚲 Available Bikes")
    for b in get_all_bikes():
        st.write(f"{b[1]} — {b[3]}")

# ---------------- BIKE DETAILS (UPDATED) ----------------
elif menu == "Bike Details":
    st.subheader("🔍 Bike Details")

    bike_names = get_bike_names()
    selected = st.selectbox("Select Bike", bike_names)

    if st.button("Show Details"):
        bike = get_bike_by_name(selected)

        if bike:
            st.success("Bike Found!")
            st.write("Name:", bike[1])
            st.write("Type:", bike[2])
            st.write("Price:", bike[3])
            st.write("Engine:", bike[4])
            st.write("Fuel Avg:", bike[5])
            st.write("Top Speed:", bike[6])
            st.write("Stock:", bike[7])

# ---------------- RECOMMENDATION (UPDATED) ----------------
elif menu == "Recommendation System":
    st.subheader("💡 Recommendation System")

    prices = [parse_price(b[3]) for b in get_all_bikes()]
    st.info(f"Bike Price Range: PKR {min(prices):,} – PKR {max(prices):,}")

    budget = st.number_input("Enter your budget", min_value=50000)

    if st.button("Recommend"):
        results = recommend(budget)

        st.write("### Closest Matches:")

        for r in results:
            st.write(f"🚲 {r[1]} — {r[3]}")

# ---------------- COMPARE ----------------
elif menu == "Compare Bikes":
    st.subheader("⚔️ Compare Bikes")

    names = get_bike_names()
    b1 = st.selectbox("Bike 1", names)
    b2 = st.selectbox("Bike 2", names)

    if st.button("Compare"):
        bike1 = get_bike_by_name(b1)
        bike2 = get_bike_by_name(b2)

        if bike1 and bike2:
            st.table({
                "Feature": ["Price", "Engine", "Fuel", "Top Speed"],
                bike1[1]: [bike1[3], bike1[4], bike1[5], bike1[6]],
                bike2[1]: [bike2[3], bike2[4], bike2[5], bike2[6]],
            })

# ---------------- STOCK CHECK (UPDATED) ----------------
elif menu == "Availability Checker":
    st.subheader("📦 Stock Checker")

    names = get_bike_names()
    name = st.selectbox("Select Bike", names)

    if st.button("Check Stock"):
        result = check_stock(name)

        if result:
            stock, bike_id = result
            st.success(f"Available Stock: {stock}")

            if st.session_state.admin_logged_in:
                new_stock = st.number_input("Update Stock", min_value=0, value=stock)

                if st.button("Update Stock"):
                    update_stock(bike_id, new_stock)
                    st.success("Stock updated!")
                    st.rerun()

# ---------------- EMI ----------------
elif menu == "EMI Calculator":
    st.subheader("💰 EMI Calculator")

    price = st.number_input("Price", min_value=0)
    down = st.number_input("Down Payment", min_value=0)
    months = st.number_input("Months", min_value=1)

    if st.button("Calculate"):
        emi = (price - down) / months
        st.success(f"Monthly EMI: PKR {emi:.2f}")

# ---------------- ADMIN ----------------
elif menu == "Admin Login":
    st.subheader("🔐 Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

    if st.session_state.admin_logged_in:
        st.subheader("🛠 Admin Panel")

        for b in get_all_bikes():
            st.markdown("---")
            st.write(b[1])
            st.write("Stock:", b[7])

            col1, col2 = st.columns(2)

            with col1:
                new_stock = st.number_input(f"Stock {b[1]}", min_value=0, value=b[7], key=f"s_{b[0]}")
                if st.button(f"Update {b[0]}", key=f"u_{b[0]}"):
                    update_stock(b[0], new_stock)
                    st.success("Updated!")
                    st.rerun()

            with col2:
                if st.button(f"Delete {b[0]}", key=f"d_{b[0]}"):
                    delete_bike(b[0])
                    st.warning("Deleted!")
                    st.rerun()