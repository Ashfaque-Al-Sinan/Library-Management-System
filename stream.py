import json
import random
import string
from pathlib import Path
from datetime import datetime
import streamlit as st

# ------------------ Library Class (same logic, adapted for Streamlit) ------------------
class Library:
    BASE_DIR = Path(__file__).parent
    database = str(BASE_DIR / "library.json")
    
    @classmethod
    def load_data(cls):
        if Path(cls.database).exists():
            with open(cls.database, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        return {"books": [], "members": []}
    
    @classmethod
    def save_data(cls, data):
        with open(cls.database, "w") as f:
            json.dump(data, f, indent=4, default=str)
    
    @staticmethod
    def gen_id(prefix="B"):
        random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"{prefix}-{random_id}"
    
    @staticmethod
    def add_book(data, title, author, copies):
        book = {
            "id": Library.gen_id(),
            "title": title,
            "author": author,
            "total_copies": copies,
            "available_copies": copies,
            "added_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        data['books'].append(book)
        Library.save_data(data)
        return data
    
    @staticmethod
    def add_member(data, name, email):
        member = {
            "id": Library.gen_id("M"),
            "name": name,
            "email": email,
            "borrowed": []
        }
        data['members'].append(member)
        Library.save_data(data)
        return data
    
    @staticmethod
    def borrow_book(data, member_id, book_id):
        # find member
        member = next((m for m in data['members'] if m['id'] == member_id), None)
        if not member:
            return data, "Member ID not found!"
        # find book
        book = next((b for b in data['books'] if b['id'] == book_id), None)
        if not book:
            return data, "Book ID not found!"
        if book['available_copies'] <= 0:
            return data, "No copies available!"
        # borrow
        borrow_entry = {
            "book_id": book['id'],
            "title": book['title'],
            "borrow_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        member['borrowed'].append(borrow_entry)
        book['available_copies'] -= 1
        Library.save_data(data)
        return data, f"Book '{book['title']}' borrowed successfully!"
    
    @staticmethod
    def return_book(data, member_id, book_index):
        member = next((m for m in data['members'] if m['id'] == member_id), None)
        if not member:
            return data, "Member ID not found!"
        if not member['borrowed']:
            return data, "No borrowed books for this member."
        if book_index < 0 or book_index >= len(member['borrowed']):
            return data, "Invalid selection."
        returned = member['borrowed'].pop(book_index)
        # increase available copies
        book = next((b for b in data['books'] if b['id'] == returned['book_id']), None)
        if book:
            book['available_copies'] += 1
        Library.save_data(data)
        return data, f"Book '{returned['title']}' returned successfully!"

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Library Management System", layout="wide")
st.title("📚 Library Management System")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = Library.load_data()

# Sidebar menu
menu = st.sidebar.radio(
    "Navigation",
    ["Add Book", "List Books", "Add Member", "List Members", "Borrow Book", "Return Book"]
)

st.sidebar.markdown("---")
if st.sidebar.button("💾 Save Data Manually"):
    Library.save_data(st.session_state.data)
    st.sidebar.success("Data saved!")

# ------------------ Add Book ------------------
if menu == "Add Book":
    st.header("➕ Add New Book")
    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        copies = st.number_input("Number of Copies", min_value=1, step=1, value=1)
        submitted = st.form_submit_button("Add Book")
        if submitted and title and author:
            st.session_state.data = Library.add_book(st.session_state.data, title, author, copies)
            st.success(f"Book '{title}' added successfully!")
        elif submitted:
            st.error("Please fill all fields.")

# ------------------ List Books ------------------
elif menu == "List Books":
    st.header("📖 All Books")
    books = st.session_state.data['books']
    if not books:
        st.info("No books in the library.")
    else:
        for b in books:
            with st.expander(f"{b['title']} by {b['author']}"):
                col1, col2 = st.columns(2)
                col1.write(f"**ID:** {b['id']}")
                col1.write(f"**Total Copies:** {b['total_copies']}")
                col1.write(f"**Available Copies:** {b['available_copies']}")
                col2.write(f"**Added On:** {b['added_on']}")

# ------------------ Add Member ------------------
elif menu == "Add Member":
    st.header("👤 Add New Member")
    with st.form("add_member_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Add Member")
        if submitted and name and email:
            st.session_state.data = Library.add_member(st.session_state.data, name, email)
            st.success(f"Member '{name}' added successfully!")
        elif submitted:
            st.error("Please fill all fields.")

# ------------------ List Members ------------------
elif menu == "List Members":
    st.header("👥 All Members")
    members = st.session_state.data['members']
    if not members:
        st.info("No members registered.")
    else:
        for m in members:
            with st.expander(f"{m['name']} ({m['email']})"):
                st.write(f"**ID:** {m['id']}")
                st.write(f"**Email:** {m['email']}")
                if m['borrowed']:
                    st.write("**Currently Borrowed Books:**")
                    for i, bk in enumerate(m['borrowed'], 1):
                        st.write(f"{i}. {bk['title']} (ID: {bk['book_id']}) borrowed on {bk['borrow_on']}")
                else:
                    st.write("No borrowed books.")

# ------------------ Borrow Book ------------------
elif menu == "Borrow Book":
    st.header("📕 Borrow a Book")
    members = st.session_state.data['members']
    books = st.session_state.data['books']
    if not members:
        st.warning("No members found. Please add a member first.")
    elif not books:
        st.warning("No books found. Please add a book first.")
    else:
        member_options = {f"{m['name']} ({m['id']})": m['id'] for m in members}
        selected_member = st.selectbox("Select Member", list(member_options.keys()))
        member_id = member_options[selected_member]
        
        book_options = {f"{b['title']} (ID: {b['id']}) | Available: {b['available_copies']}": b['id'] 
                        for b in books if b['available_copies'] > 0}
        if not book_options:
            st.error("No books available for borrowing.")
        else:
            selected_book = st.selectbox("Select Book", list(book_options.keys()))
            book_id = book_options[selected_book]
            if st.button("Borrow"):
                data, msg = Library.borrow_book(st.session_state.data, member_id, book_id)
                st.session_state.data = data
                if "successfully" in msg:
                    st.success(msg)
                else:
                    st.error(msg)

# ------------------ Return Book ------------------
elif menu == "Return Book":
    st.header("📗 Return a Book")
    members = st.session_state.data['members']
    if not members:
        st.warning("No members found.")
    else:
        member_options = {f"{m['name']} ({m['id']})": m['id'] for m in members}
        selected_member = st.selectbox("Select Member", list(member_options.keys()))
        member_id = member_options[selected_member]
        
        # Find member and show borrowed books
        member = next((m for m in st.session_state.data['members'] if m['id'] == member_id), None)
        if member and member['borrowed']:
            borrowed_list = [f"{i+1}. {bk['title']} (ID: {bk['book_id']})" 
                             for i, bk in enumerate(member['borrowed'])]
            selected_index = st.selectbox("Select book to return", range(len(borrowed_list)), 
                                          format_func=lambda x: borrowed_list[x])
            if st.button("Return"):
                data, msg = Library.return_book(st.session_state.data, member_id, selected_index)
                st.session_state.data = data
                if "successfully" in msg:
                    st.success(msg)
                else:
                    st.error(msg)
        elif member:
            st.info("This member has no borrowed books.")
        else:
            st.error("Member not found.")