import json
import random
import string
from pathlib import Path
from datetime import datetime
import os
import sys

#functionalities
class Library:
    
    # # Script ke folder ka path
    BASE_DIR = Path(__file__).parent
    database = str(BASE_DIR / "library.json")
    # database="library.json"
    data={"books":[],"members":[]}
    
    #load existing data to json or create your json
    if Path(database).exists():
        with open(database,"r") as f:
            content = f.read().strip()
            if content:
                data=json.loads(content)
    else:
        with open(database,'w') as f:
            json.dump(data,f,indent=4)
    
            
                    
    
    def gen_id(prefix= "B"):
        random_id = ""
        for i in range(5):
            random_id += random.choice(string.ascii_uppercase + string.digits)
        return prefix + "-" + random_id
    
    @classmethod
    def save_data(cls):
        with open(cls.database,'w') as f:
            json.dump(cls.data,f,indent=4,default=str)
        
        
    def add_book(self):
        title = input("Enter Book Title: ")
        author = input("Enter The Book Author: ")
        copies = int(input("How Many Copies: "))
        
        book={
            "id":Library.gen_id(),
            "title":title,
            "author":author,
            "total_copies":copies,
            "available_copies":copies,
            "added_on":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        Library.data['books'].append(book)
        Library.save_data()
    print()    
    def list_books(self):
        if not Library.data['books']:
            print("No books Found")
            return
        for b in Library.data['books']:
             print(f"{b['id']:12} {b['title'][:24]:25} {b['author'][:19]:20} {b['total_copies']}/{b['available_copies']:>3}")    
    print()
    def add_member(self):
        name=input("enter your name: ")
        email=input("Enter Mail: ")
        
        member={
            "id" : Library.gen_id("M"),
            "name" : name ,
            "email" : email,
            "borrowed":[]  
        }
        Library.data['members'].append(member)
        Library.save_data()
        print("Member added successfully")
        print()
        
    
    def list_members(self):
        if not Library.data['members']:
            print("there are no members")
            return
        for m in Library.data['members']:
            print(f"{m['id']:12} {m['name'][:24]:25} {m['email'][:29]:30}")
            print("This guy is has currently")
            print(f"{m['borrowed']}")
    print()
    
    def borrow(self):
        member_id = input("Enter the member Id : ").strip()
        members=[m for m in Library.data['members'] if m['id']==member_id]
        if not members:
            print("sorry no such id exists")
            return
        member = members[0]
        book_id=input("enter the book id : ")
        books=[b for b in Library.data['books'] if b['id']==book_id]
        
        if not books:
            print("no such a book")
            return
        
        book=books[0]
        
        if book['available_copies'] <= 0 :
            print("Sorry no books exists")
            return
        
        borrow_entry={
            "book_id" : book["id"],
            "title" :book['title'],
            "borrow_on" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        }
        
        member['borrowed'].append(borrow_entry)
        book['available_copies'] -= 1
        Library.save_data()
    
    def return_book(self):
        member_id = input("Enter the member Id : ").strip()
        members=[m for m in Library.data['members'] if m['id']==member_id]
        if not members:
            print("sorry no such id exists")
            return
        
        member = members[0]
        
        if not member['borrowed']:
            print("no borrowed books")
            return
        print("borrowed books")
        for i,b in enumerate(member['borrowed'],start=1):
            print(f"{i}.{b['title']} ({b['book_id']})")
        
        try:
            choice=int(input("enter number to return :- "))
            selected=member['borrowed'].pop(choice-1)
        except Exception as err :
            print("invalid value")
            
        books = [bk for bk in Library.data['books'] if bk['id']==selected['book_id']]
        if books :
            books[0]['available_copies'] +=1
        Library.save_data()                
            
                    
        
    
    
hello=Library()  
  
while True:
    print("="*50)
    print("LIBRARY MANAGEMENT SYSTEM")
    print("="*50)
    print("1. ADD BOOK")
    print("2. LIST BOOKS")
    print("3. ADD MEMBERS")
    print("4. LIST MEMEBERS")
    print("5. BORROW BOOK")
    print("6. RETURN BOOK")
    print("0. EXIT FROM PORTAL")
    print("-"*50)

    choice = input("What Task You Want To Do = ")

    if choice == "1" :
        hello.add_book()
        
    if choice == "2":
        hello.list_books()

    if choice == "3":
        hello.add_member()
        
    if choice == "4":
        hello.list_members()
        
    if choice == "5":
        hello.borrow()
        
    if choice == "6":
        hello.return_book()
    
    if choice == "0":
        Library.save_data()   # optional: last data save
        print("Exiting...")
        sys.exit(0)                       
    
    
    
    
    


