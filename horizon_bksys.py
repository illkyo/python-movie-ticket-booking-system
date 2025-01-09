import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk

import os

# Get the directory where the current Python script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the database file
db_path = os.path.join(script_dir, "sys.db")

con = sqlite3.connect(db_path)
cur = con.cursor()

### Main Entrypoint
def login(email, password):
    cur.execute("SELECT ROLE FROM USERS WHERE EMAIL=? AND PASSWORD=?", (email, password))

    result = cur.fetchone()

    if result:
        return True, result[0]
    else:
        return False, ""
    
def login_main():

    # Create the main window
    main_win = tk.Tk()
    main_win.title("Horizon Cinemas Booking System")

    # Set window size and position
    main_win.geometry("350x200")
    main_win.resizable(False, False)

    # Add email label and entry
    tk.Label(main_win, text="Email:", font=("TkDefaultFont", 11)).pack(pady=10)
    email_entr = tk.Entry(main_win, width=35)
    email_entr.pack()

    # Add password label and entry
    tk.Label(main_win, text="Password:", font=("TkDefaultFont", 11)).pack(pady=10)
    pass_entr = tk.Entry(main_win, width=35, show="*")
    pass_entr.pack()

    def attempt_login():
        email = email_entr.get()
        password = pass_entr.get()

        success, role = login(email, password)

        if success:
            global curr_user
            curr_user =  email
            if role == "Staff":
                staff_view()
            elif role == "Admin":
                admin_view()
            elif role == "Manager":
                mnger_view()
        else:
            messagebox.showerror("Login Failed", "Invalid Email or Password.")

    login_button = tk.Button(main_win, text="Login", command=attempt_login, height=10, width=10)
    login_button.pack(pady=20)
    
    main_win.mainloop()

### Booking Staff Related
def staff_view():
    staff_win = tk.Toplevel()
    
    cur.execute("SELECT ROLE, FULL_NAME FROM USERS WHERE EMAIL=?", (curr_user,))
    result = cur.fetchall()

    user_role = result[0][0]
    user_name = result[0][1]

    staff_win.title(f"{user_role} - {user_name}")

    ## To check window sizes
    # # Create a label to display the current window size
    # size_label = ttk.Label(staff_win, text="")
    # size_label.pack(pady=10)

    # # Update the size label when the window is resized
    # def update_size(event):
    #     width = staff_win.winfo_width()
    #     height = staff_win.winfo_height()
    #     size_label.config(text=f"Current size: {width}x{height}")

    # # Bind the <Configure> event to update the label
    # staff_win.bind("<Configure>", update_size)

    staff_tab = StaffTab(staff_win)
    staff_tab.pack(fill=tk.BOTH, expand=True)

class StaffTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        film_list = FilmListTabSt(notebook)
        bookings_list = BookingsTabSt(notebook)
        make_booking =  MakeTabSt(notebook, bookings_list)
        check_booking = CheckCancelTabSt(notebook, bookings_list)

        notebook.add(film_list, text="Films")
        notebook.add(bookings_list, text="Bookings")
        notebook.add(make_booking, text="Make Booking")
        notebook.add(check_booking, text="Check Booking")

        notebook.bind("<<NotebookTabChanged>>", self.resize)

    def resize(self, event):
        # Get the currently selected tab
        notebook = event.widget
        tab = notebook.nametowidget(notebook.select())

        # Determine the desired size for the selected tab
        if isinstance(tab, FilmListTabSt):
            self.parent.geometry("1440x320")
        elif isinstance(tab, BookingsTabSt):
            self.parent.geometry("1440x320") 
        elif isinstance(tab, MakeTabSt):
            self.parent.geometry("580x340")
        elif isinstance(tab, CheckCancelTabSt):
            self.parent.geometry("1440x320") 


class FilmListTabSt(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns=("Name", "Synopsis", "Genre", "Rating", "Screening Times", "Screen")

        self.tree = ttk.Treeview(self, columns=columns)
        self.tree.heading("#0", text="Film ID")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        cur.execute("SELECT CINEMA_ID FROM USERS WHERE EMAIL=?", (curr_user,))
        user_cin = cur.fetchone()

        try:
            cur.execute("SELECT * FROM FILMS WHERE CINEMA_ID=?", (user_cin[0],)) # Staff can only view films in their cinema
            films = cur.fetchall()
            for film in films:
                self.tree.insert("", "end", text=film[0], values=(film[1], film[2], film[3], film[4], film[5], film[7]))
        except Exception as e:
            self.result.config(text=f"Error fetching films: {e}")


class BookingsTabSt(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns = ("Film Name", "Customer", "Tickets", "Total Price", "Booked Date", "Show Time")
        self.tree = ttk.Treeview(self, columns=columns)
        
        self.tree.heading("#0", text="Reference")
        self.tree.column("#0", anchor="w")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data
        
        cur.execute("SELECT ID FROM USERS WHERE EMAIL=?", (curr_user,))
        user_id = cur.fetchone()

        try:
            cur.execute('''
                SELECT BOOKINGS.REFERENCE, FILMS.NAME, BOOKINGS.CUSTOMER, BOOKINGS.TICKET_COUNT, BOOKINGS.TOTAL_PRICE, BOOKINGS.BOOK_DATE, BOOKINGS.SHOW_TIME
                FROM BOOKINGS
                JOIN FILMS ON BOOKINGS.FILM_ID = FILMS.ID
                WHERE BOOKINGS.STAFF_ID=?              
            ''', (user_id[0],)) 

            bookings = cur.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6]))
        except Exception as e:
            self.result.config(text=f"Error fetching bookings: {e}")


class MakeTabSt(ttk.Frame):
    def __init__(self, parent, bookings_list):
        super().__init__(parent)

        self.bookings_list = bookings_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Fields for managing films
        ttk.Label(container, text="Reference:").grid(row=0, column=0, padx=10, pady=5)
        self.ref = tk.StringVar()
        ref_entry = ttk.Entry(container, textvariable=self.ref)
        ref_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(container, text="Film ID:").grid(row=1, column=0, padx=10, pady=5)
        self.id = tk.IntVar()
        id_entry = ttk.Entry(container, textvariable=self.id)
        id_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Date:").grid(row=2, column=0, padx=10, pady=5)
        self.date = tk.StringVar()
        ttk.Entry(container, textvariable=self.date).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Tickets:").grid(row=4, column=0, padx=10, pady=5)
        self.tickets = tk.IntVar()
        ttk.Entry(container, textvariable=self.tickets).grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(container, text="Total Price:").grid(row=5, column=0, padx=10, pady=5)
        self.price = tk.DoubleVar()
        ttk.Entry(container, textvariable=self.price).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(container, text="Customer Name:").grid(row=6, column=0, padx=10, pady=5)
        self.name = tk.StringVar()
        ttk.Entry(container, textvariable=self.name).grid(row=6, column=1, padx=10, pady=5)

        tk.Button(container, text="Make Booking", command=self.make_booking).grid(row=7, column=0, columnspan=2, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

    def make_booking(self):
        new_booking = {
            "reference": self.ref.get(),
            "film_id": self.id.get(),
            "book_date": self.date.get(),
            "ticket_count": self.tickets.get(),
            "total_price": self.price.get(),
            "customer": self.name.get()
        }

        if all(new_booking.values()):
            try:
                cur.execute("SELECT ID FROM USERS WHERE EMAIL=?", (curr_user,))
                user_id = cur.fetchone()

                cur.execute("SELECT SCREEN_TIME FROM FILMS WHERE ID=?", (new_booking["film_id"],))
                show_time = cur.fetchone()

                cur.execute(
                    "INSERT INTO BOOKINGS (REFERENCE, FILM_ID, BOOK_DATE, SHOW_TIME, TICKET_COUNT, TOTAL_PRICE, CUSTOMER, STAFF_ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (new_booking["reference"], new_booking["film_id"], new_booking["book_date"], show_time[0], new_booking["ticket_count"], new_booking["total_price"], new_booking["customer"], user_id[0])
                )

                con.commit()
                self.bookings_list.populate_treeview()

                self.result.config(text=f"Booking Added")
            except Exception as e:
                self.result.config(text=f"Error Adding Booking: {e}")
        else:
            self.result.config(text="All fields are required.")

class CheckCancelTabSt(ttk.Frame):
    def __init__(self, parent, bookings_list):
        super().__init__(parent)

        self.bookings_list = bookings_list

        columns = ("Film ID", "Customer", "Tickets", "Total Price", "Booked Date", "Show Time", "Staff ID")

        self.tree = ttk.Treeview(self, columns=columns)

        self.tree.heading("#0", text="Reference")
        self.tree.column("#0", anchor="w")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", columnspan=2)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        ttk.Label(self, text="Reference:", font=("TkDefaultFont", 11)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.ref = tk.StringVar()
        ttk.Entry(self, textvariable=self.ref).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Button(self, text="Load Booking", command=self.load_ref).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        tk.Button(self, text="Cancel Booking", command=self.cancel_ref).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.result = ttk.Label(self, text="")
        self.result.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def load_ref(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        ref = self.ref.get()
        
        try:
            cur.execute("""
                SELECT REFERENCE, FILM_ID, CUSTOMER, TICKET_COUNT, TOTAL_PRICE, BOOK_DATE, SHOW_TIME, STAFF_ID
                FROM BOOKINGS
                WHERE REFERENCE=?
            """, (ref,))

            booking = cur.fetchone()

            if booking:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7])) # BOO!
            else:
                self.result.config(text="Booking Not Found")

        except Exception as e:
            self.result.config(text=f"Error Fetching Booking: {e}")

    def cancel_ref(self):
        ref = self.ref.get()
        try:
            cur.execute("SELECT ID FROM USERS WHERE EMAIL=?", (curr_user,))
            user_id = cur.fetchone()

            cur.execute("SELECT STAFF_ID FROM BOOKINGS WHERE REFERENCE=?", (ref,))
            staff_id = cur.fetchone()

            if user_id[0] == staff_id[0]:
                cur.execute("DELETE FROM BOOKINGS WHERE REFERENCE=?", (ref,))

                con.commit()
                self.bookings_list.populate_treeview()

                self.result.config(text=f"Booking Deleted Successfully. Inform of 50% Cancellation Charge.")
            else:
                self.result.config(text=f"Staff ID does not match Current User ID")

        except Exception as e:
            self.result.config(text=f"Error Deleting Booking: {e}")

### Admin Related
def admin_view():
    admin_win = tk.Toplevel()

    cur.execute("SELECT ROLE, FULL_NAME FROM USERS WHERE EMAIL=?", (curr_user,))
    result = cur.fetchall()

    user_role = result[0][0]
    user_name = result[0][1]

    admin_win.title(f"{user_role} - {user_name}")

    # ## To check window sizes

    # # Create a label to display the current window size
    # size_label = ttk.Label(admin_win, text="")
    # size_label.pack(pady=10)

    # # Update the size label when the window is resized
    # def update_size(event):
    #     width = admin_win.winfo_width()
    #     height = admin_win.winfo_height()
    #     size_label.config(text=f"Current size: {width}x{height}")

    # # Bind the <Configure> event to update the label
    # admin_win.bind("<Configure>", update_size)

    admin_tab = AdminTab(admin_win)
    admin_tab.pack(fill=tk.BOTH, expand=True)

## Admin Tab
class AdminTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        film_list = FilmListTabAd(notebook)
        add_film = AddFilmTabAd(notebook, film_list)
        edit_film = EditFilmTabAd(notebook, film_list)
        user_list = UserListTabAd(notebook)
        add_user = AddUserTabAd(notebook, user_list)
        edit_user = EditUserTabAd(notebook, user_list)
        bookings = BookingsReportTabAd(notebook)

        notebook.add(add_film, text="Add Film")
        notebook.add(film_list, text="Films")
        notebook.add(edit_film, text="Edit Film")
        notebook.add(user_list, text="Users")
        notebook.add(edit_user, text="Edit User")
        notebook.add(add_user, text="Add User")
        notebook.add(bookings, text="Bookings Report")

        notebook.bind("<<NotebookTabChanged>>", self.resize)

    def resize(self, event):
        # Get the currently selected tab
        notebook = event.widget
        tab = notebook.nametowidget(notebook.select())

        # Determine the desired size for the selected tab
        if isinstance(tab, AddFilmTabAd):
            self.parent.geometry("425x330")
        elif isinstance(tab, FilmListTabAd):
            self.parent.geometry("1440x320") 
        elif isinstance(tab, EditFilmTabAd):
            self.parent.geometry("580x340")
        elif isinstance(tab, UserListTabAd):
            self.parent.geometry("840x320") 
        elif isinstance(tab, EditUserTabAd):
            self.parent.geometry("425x340")
        elif isinstance(tab, AddUserTabAd):
            self.parent.geometry("425x340")
        elif isinstance(tab, BookingsReportTabAd):
            self.parent.geometry("1440x320")

class AddFilmTabAd(ttk.Frame):
    def __init__(self, parent, film_list):
        super().__init__(parent)

        self.film_list = film_list
        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Fields for managing films
        ttk.Label(container, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        self.name = tk.StringVar()
        name_entry = ttk.Entry(container, textvariable=self.name)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(container, text="Synopsis:").grid(row=1, column=0, padx=10, pady=5)
        self.syn = tk.StringVar()
        syn_entry = ttk.Entry(container, textvariable=self.syn)
        syn_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Genre:").grid(row=2, column=0, padx=10, pady=5)
        self.genre = tk.StringVar()
        ttk.Entry(container, textvariable=self.genre).grid(row=2, column=1, padx=10, pady=5)

        ratings = ['', 'G', 'PG', 'PG-13', 'R', 'NC-17', 'X']

        ttk.Label(container, text="Rating:").grid(row=3, column=0, padx=10, pady=5)
        self.rating = tk.StringVar()
        ttk.OptionMenu(container, self.rating, *ratings).grid(row=3, column=1, padx=10, pady=5)

        screens = ['', 1, 2, 3, 4, 5, 6]

        ttk.Label(container, text="Screen:").grid(row=4, column=0, padx=10, pady=5)
        self.screen = tk.IntVar()
        ttk.OptionMenu(container, self.screen, *screens).grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(container, text="Screening Times:").grid(row=5, column=0, padx=10, pady=5)
        self.screentimes = tk.StringVar()
        ttk.Entry(container, textvariable=self.screentimes).grid(row=5, column=1, padx=10, pady=5)

        tk.Button(container, text="Add Film", command=self.add_film).grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

    def add_film(self):
        new_film = {
            "name": self.name.get(),
            "synopsis": self.syn.get(),
            "genre": self.genre.get(),
            "rating": self.rating.get(),
            "screen": self.screen.get(),
            "screentimes": self.screentimes.get()
        }

        if all(new_film.values()):
            try:
                cur.execute("SELECT CINEMA_ID FROM USERS WHERE EMAIL=?", (curr_user,))
                user_cinema_id = cur.fetchone()

                cur.execute(
                    "INSERT INTO FILMS (NAME, SYNOPSIS, GENRE, RATING, CINEMA_ID, SCREEN_TIME, SCREEN) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (new_film["name"], new_film["synopsis"], new_film["genre"], new_film["rating"], user_cinema_id[0], new_film["screentimes"], new_film["screen"])
                )

                con.commit()
                self.film_list.populate_treeview()

                self.result.config(text=f"Film '{new_film['name']}' added")
            except Exception as e:
                self.result.config(text=f"Error Adding Film: {e}")
        else:
            self.result.config(text="All fields are required.")
       
class FilmListTabAd(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns=("Name", "Synopsis", "Genre", "Rating", "Screening Times", "Screen")

        self.tree = ttk.Treeview(self, columns=columns)
        self.tree.heading("#0", text="Film ID")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        cur.execute("SELECT CINEMA_ID FROM USERS WHERE EMAIL=?", (curr_user,))
        user_cin = cur.fetchone()

        try:
            cur.execute("SELECT * FROM FILMS WHERE CINEMA_ID=?", (user_cin[0],)) # Admin can only view films in their cinema
            films = cur.fetchall()
            for film in films:
                self.tree.insert("", "end", text=film[0], values=(film[1], film[2], film[3], film[4], film[5], film[7]))
        except Exception as e:
            self.result.config(text=f"Error fetching films: {e}")
        
        
class EditFilmTabAd(ttk.Frame):
    def __init__(self, parent, film_list):
        super().__init__(parent)

        self.film_list = film_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Edit Films using ID
        ttk.Label(container, text="Enter Film ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.film_id = tk.IntVar()
        ttk.Entry(container, textvariable=self.film_id).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(container, text="Load Film", command=self.load_film).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(container, text="Update Film", command=self.update_film).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(container, text="Remove Film", command=self.remove_film).grid(row=2, column=2, padx=10, pady=5)

        # Fields for editing film details
        ttk.Label(container, text="Name:").grid(row=1, column=0, padx=10, pady=5)
        self.name = tk.StringVar()
        ttk.Entry(container, textvariable=self.name, width=50).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Synopsis:").grid(row=2, column=0, padx=10, pady=5)
        self.syn = tk.StringVar()
        ttk.Entry(container, textvariable=self.syn, width=50).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Genre:").grid(row=3, column=0, padx=10, pady=5)
        self.genre = tk.StringVar()
        ttk.Entry(container, textvariable=self.genre).grid(row=3, column=1, padx=10, pady=5)

        ratings = ['', 'G', 'PG', 'PG-13', 'R', 'NC-17', 'X']

        ttk.Label(container, text="Rating:").grid(row=4, column=0, padx=10, pady=5)
        self.rating = tk.StringVar()
        ttk.OptionMenu(container, self.rating, *ratings).grid(row=4, column=1, padx=10, pady=5)

        screens = ['', 1, 2, 3, 4, 5, 6]

        ttk.Label(container, text="Screen:").grid(row=5, column=0, padx=10, pady=5)
        self.screen = tk.IntVar()
        ttk.OptionMenu(container, self.screen, *screens).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(container, text="Screening Times:").grid(row=6, column=0, padx=10, pady=5)
        self.screentimes = tk.StringVar()
        ttk.Entry(container, textvariable=self.screentimes, width=50).grid(row=6, column=1, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

    def load_film(self):
        film_id = self.film_id.get()

        if film_id:
            try:
                cur.execute("SELECT CINEMA_ID FROM USERS WHERE EMAIL = ?", (curr_user,))
                curr_user_cin = cur.fetchone()

                cur.execute("SELECT * FROM FILMS WHERE ID = ?", (film_id,))
                film = cur.fetchone()
                if film and film[6] == curr_user_cin[0]:
                    # Display film details
                    self.name.set(film[1])
                    self.syn.set(film[2])
                    self.genre.set(film[3])
                    self.rating.set(film[4])
                    self.screen.set(film[7])
                    self.screentimes.set(film[5])
                    
                    self.result.config(text=f"Loaded Film ID '{film_id}'")
                elif film[6] != curr_user_cin[0]:
                    self.result.config(text="Cannot load Film. Film is in Another Cinema")
                else:
                    self.result.config(text="Film ID Not Found")
            except Exception as e:
                self.result.config(text=f"Error loading film: {e}")
        else:
            self.result.config(text="Film ID field is required.")

    def update_film(self):
        film_id = self.film_id.get()

        name = self.name.get()
        synopsis = self.syn.get()
        genre = self.genre.get()
        rating = self.rating.get()
        screen = self.screen.get()
        screentimes = self.screentimes.get()

        if name and synopsis and genre and rating and screen and screentimes:
            try:
                cur.execute(
                "UPDATE FILMS SET NAME = ?, SYNOPSIS = ?, GENRE = ?, RATING = ?, SCREEN_TIME = ?, SCREEN = ? WHERE ID = ?",
                (name, synopsis, genre, rating, screentimes, screen, film_id)  # Update in DB
            )
                con.commit()
                self.film_list.populate_treeview()

                self.result.config(text=f"Film ID '{film_id}' updated.")
            except Exception as e:
                self.result.config(text=f"Error Updating Film: {e}")
        else:
            self.result.config(text="All fields are required.")

    def remove_film(self):
        film_id = self.film_id.get()

        if film_id:
            try:
                cur.execute("DELETE FROM FILMS WHERE ID=?", (film_id,))

                con.commit()
                self.film_list.populate_treeview()
                
                self.result.config(text=f"Film '{film_id}' removed")

            except Exception as e:
                self.result.config(text=f"Error Deleting Booking: {e}")
        else:
            self.result.config(text="Film ID field is required.")

class UserListTabAd(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns = ("Full Name", "Email", "Role")
        self.tree = ttk.Treeview(self, columns=columns)
        self.tree.heading("#0", text="ID")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            cur.execute("SELECT ID, FULL_NAME, EMAIL, ROLE FROM USERS")
            users = cur.fetchall()
            for user in users:
                self.tree.insert("", "end", text=user[0], values=(user[1], user[2], user[3]))
        except Exception as e:
            self.result.config(text=f"Error fetching users: {e}")


class AddUserTabAd(ttk.Frame):
    def __init__(self, parent, user_list):
        super().__init__(parent)

        self.user_list = user_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Fields for entering user details
        ttk.Label(container, text="Enter User ID:").grid(row=0, column=0, padx=10, pady=5)
        self.id = tk.IntVar()
        ttk.Entry(container, textvariable=self.id).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(container, text="First Name:").grid(row=1, column=0, padx=10, pady=5)
        self.firstname = tk.StringVar()
        ttk.Entry(container, textvariable=self.firstname).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Last Name:").grid(row=2, column=0, padx=10, pady=5)
        self.lastname = tk.StringVar()
        ttk.Entry(container, textvariable=self.lastname).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Email:").grid(row=3, column=0, padx=10, pady=5)
        self.email = tk.StringVar()
        ttk.Entry(container, textvariable=self.email).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(container, text="Password:").grid(row=4, column=0, padx=10, pady=5)
        self.password = tk.IntVar()
        ttk.Entry(container, textvariable=self.password).grid(row=4, column=1, padx=10, pady=5)

        roles = ['', 'Staff', 'Admin']
        
        ttk.Label(container, text="Role:").grid(row=5, column=0, padx=10, pady=5)
        self.role = tk.StringVar()
        ttk.OptionMenu(container, self.role, *roles).grid(row=5, column=1, padx=10, pady=5)

        tk.Button(container, text="Register User", command=self.add_user).grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

    def add_user(self):
        new_user = {
            "id": self.id.get(),
            "first_name": self.firstname.get(),
            "last_name": self.lastname.get(),
            "email": self.email.get(),
            "password": self.password.get(),
            "role": self.role.get(),
        }

        if all(new_user.values()):

            cur.execute("SELECT CINEMA_ID FROM USERS WHERE EMAIL=?", (curr_user,))
            user_cinema_id = cur.fetchone()

            try:
                cur.execute(
                    "INSERT INTO USERS (ID, FIRST_NAME, LAST_NAME, EMAIL, PASSWORD, ROLE, CINEMA_ID) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (new_user["id"], new_user["first_name"], new_user["last_name"], new_user["email"], new_user["password"], new_user["role"], user_cinema_id[0])
                )

                con.commit()
                self.user_list.populate_treeview()

                self.result.config(text=f"User '{new_user['first_name']}' added with Role '{new_user['role']}' ")

            except Exception as e:
                self.result.config(text=f"Error Registering User: {e}")
        else:
            self.result.config(text="All fields are required.")
   
        
class EditUserTabAd(ttk.Frame):
    def __init__(self, parent, user_list):
        super().__init__(parent)

        self.user_list = user_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Components for selecting a user by ID
        ttk.Label(container, text="Enter User ID:").grid(row=0, column=0, padx=10, pady=5)
        self.user_id = tk.StringVar()
        ttk.Entry(container, textvariable=self.user_id).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(container, text="Load User Details", command=self.load_user).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(container, text="Update User Details", command=self.update_user).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(container, text="Remove User", command=self.remove_user).grid(row=2, column=2, padx=10, pady=5)

        # Fields for editing user details
        ttk.Label(container, text="First Name:").grid(row=1, column=0, padx=10, pady=5)
        self.firstname = tk.StringVar()
        ttk.Entry(container, textvariable=self.firstname).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Last Name:").grid(row=2, column=0, padx=10, pady=5)
        self.lastname = tk.StringVar()
        ttk.Entry(container, textvariable=self.lastname).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Email:").grid(row=3, column=0, padx=10, pady=5)
        self.email = tk.StringVar()
        ttk.Entry(container, textvariable=self.email).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(container, text="Password:").grid(row=4, column=0, padx=10, pady=5)
        self.password = tk.StringVar()
        ttk.Entry(container, textvariable=self.password).grid(row=4, column=1, padx=10, pady=5)
        
        roles = ['', 'Staff', 'Admin']
        
        ttk.Label(container, text="Role:").grid(row=5, column=0, padx=10, pady=5)
        self.role = tk.StringVar()
        ttk.OptionMenu(container, self.role, *roles).grid(row=5, column=1, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

    def load_user(self):
        user_id = self.user_id.get()

        if user_id:
            try:
                cur.execute("SELECT * FROM USERS WHERE ID = ?", (user_id,))
                user = cur.fetchone()

                cur.execute("SELECT CINEMA_ID FROM USERS WHERE EMAIL = ?", (curr_user,))
                curr_user_cin = cur.fetchone()

                if user and user[6] != "Manager" and user[7] == curr_user_cin[0]:
                    # Display user details in the entry fields
                    self.firstname.set(user[1])
                    self.lastname.set(user[2])
                    self.email.set(user[4])
                    self.password.set(user[5])
                    self.role.set(user[6])
                    
                    self.result.config(text=f"Loaded {user_id} - {self.firstname.get()}")
                elif user[6] == "Manager":
                    self.result.config(text="Cannot load User. User is Manager")
                elif user[6] != curr_user_cin[0]:
                    self.result.config(text="Cannot load User. User is from Another Cinema")
                else:
                    self.result.config(text="User ID not Found")
            except Exception as e:
                self.result.config(text=f"Error loading user: {e}")
        else:
            self.result.config(text="User ID Field is Required")

    def update_user(self):
        user_id = self.user_id.get()

        firstname = self.firstname.get()
        lastname = self.lastname.get()
        email = self.email.get()
        password = self.password.get()
        role = self.role.get()

        if firstname and lastname and email and password and role:
            try:
                cur.execute(
                "UPDATE USERS SET FIRST_NAME = ?, LAST_NAME = ?, EMAIL = ?, PASSWORD = ?, ROLE = ? WHERE ID = ?",
                (firstname, lastname, email, password, role, user_id)
            )
                con.commit()
                self.user_list.populate_treeview()

                self.result.config(text=f"{user_id} - {self.firstname.get()} updated")
            except Exception as e:
                self.result.config(text=f"Error Updating User: {e}")
        else:
            self.result.config(text="All fields are required.")

    def remove_user(self):
        user_id = self.user_id.get()
        
        if user_id:
            try:
            
                cur.execute("DELETE FROM USERS WHERE ID=?", (user_id,))

                con.commit()
                self.user_list.populate_treeview()
                
                self.result.config(text=f"User '{user_id}' removed")

            except Exception as e:
                self.result.config(text=f"Error Deleting Booking: {e}")
        else:
            self.result.config(text="User ID field is required.")
            
class BookingsReportTabAd(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns = ("Filled by Staff", "Film", "Tickets", "Total Price", "Booked Date", "Show Time")
        self.tree = ttk.Treeview(self, columns=columns)
        
        self.tree.heading("#0", text="Reference")
        self.tree.column("#0", anchor="w")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.populate_treeview()

        tk.Button(self, text=f"Generate Report", command=self.generate_report).grid(row=4, column=0) # Only displays Total Money Earned for now

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            cur.execute('''
                SELECT BOOKINGS.REFERENCE, BOOKINGS.STAFF_ID, FILMS.NAME, BOOKINGS.TICKET_COUNT, BOOKINGS.TOTAL_PRICE, BOOKINGS.BOOK_DATE, BOOKINGS.SHOW_TIME
                FROM BOOKINGS
                JOIN FILMS ON BOOKINGS.FILM_ID = FILMS.ID
            ''')
            bookings = cur.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6]))
        except Exception as e:
            self.result.config(text=f"Error fetching bookings: {e}")

    def generate_report(self):
        report_win = tk.Toplevel()
        report_win.title("Report")
        report_win.geometry("265x145")
        report_win.resizable(False, False)

        cur.execute('''
                    SELECT SUM(TOTAL_PRICE), SUM(TICKET_COUNT)
                    FROM BOOKINGS
            ''')
        booking_sums = cur.fetchall()  # Fetch the sum value from the query result

        rev_result = ttk.Label(report_win, text=f"Total Money Earned: {booking_sums[0][0]}") # Rev for Revenue
        rev_result.pack()

        ticket_result = ttk.Label(report_win, text=f"Total Tickets Booked: {booking_sums[0][1]}")
        ticket_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM SEATS
                    WHERE STATUS = 'Reserved'
            ''')
        seat_sums = cur.fetchall()

        seats_result = ttk.Label(report_win, text=f"Total Seats Reserved: {seat_sums[0][0]}")
        seats_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM FILMS
            ''')
        film_sums = cur.fetchall()

        films_result = ttk.Label(report_win, text=f"Total Films Playing: {film_sums[0][0]}")
        films_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM SCREENS
            ''')
        screen_sums = cur.fetchall()

        screen_result = ttk.Label(report_win, text=f"Total Screens: {screen_sums[0][0]}")
        screen_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM USERS
            ''')
        screen_sums = cur.fetchall()

        users_result = ttk.Label(report_win, text=f"Total Users: {screen_sums[0][0]}")
        users_result.pack()

### Manager Related
def mnger_view():
    mnger_win = tk.Toplevel()
    
    cur.execute("SELECT ROLE, FULL_NAME FROM USERS WHERE EMAIL=?", (curr_user,))
    result = cur.fetchall()

    user_role = result[0][0]
    user_name = result[0][1]

    mnger_win.title(f"{user_role} - {user_name}")

    # # To check window sizes
    # # Create a label to display the current window size
    # size_label = ttk.Label(mnger_win, text="")
    # size_label.pack(pady=10)

    # # Update the size label when the window is resized
    # def update_size(event):
    #     width = mnger_win.winfo_width()
    #     height = mnger_win.winfo_height()
    #     size_label.config(text=f"Current size: {width}x{height}")

    # # Bind the <Configure> event to update the label
    # mnger_win.bind("<Configure>", update_size)

    mnger_tab = ManagerTab(mnger_win)
    mnger_tab.pack(fill=tk.BOTH, expand=True)

class ManagerTab(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        film_list = FilmListTabM(notebook)
        add_film = AddFilmTabM(notebook, film_list)
        edit_film = EditFilmTabM(notebook, film_list)
        user_list = UserListTabM(notebook)
        add_user = AddUserTabM(notebook, user_list)
        edit_user = EditUserTabM(notebook, user_list)
        cinema_list = CinemaListTabM(notebook)
        add_cinema = AddCinemaTabM(notebook, cinema_list)
        edit_cinema = EditCinemaTabM(notebook, cinema_list, film_list, user_list)
        bookings = BookingsReportTabM(notebook)

        notebook.add(add_film, text="Add Film")
        notebook.add(film_list, text="Films")
        notebook.add(edit_film, text="Edit Film")
        notebook.add(user_list, text="Users")
        notebook.add(edit_user, text="Edit User")
        notebook.add(add_user, text="Add User")
        notebook.add(cinema_list, text="Cinemas")
        notebook.add(add_cinema, text="Add Cinema")
        notebook.add(edit_cinema, text="Edit Cinema")
        notebook.add(bookings, text="Bookings Report")

        notebook.bind("<<NotebookTabChanged>>", self.resize)

    def resize(self, event):
        # Get the currently selected tab
        notebook = event.widget
        tab = notebook.nametowidget(notebook.select())

        # Determine the desired size for the selected tab
        if isinstance(tab, AddFilmTabM):
            self.parent.geometry("600x430")
        elif isinstance(tab, FilmListTabM):
            self.parent.geometry("1540x320") 
        elif isinstance(tab, EditFilmTabM):
            self.parent.geometry("600x430")
        elif isinstance(tab, UserListTabM):
            self.parent.geometry("1050x300") 
        elif isinstance(tab, EditUserTabM):
            self.parent.geometry("600x400")
        elif isinstance(tab, AddUserTabM):
            self.parent.geometry("600x400")
        elif isinstance(tab, CinemaListTabM):
            self.parent.geometry("840x300")
        elif isinstance(tab, AddCinemaTabM):
            self.parent.geometry("600x320")
        elif isinstance(tab, EditCinemaTabM):
            self.parent.geometry("650x380")
        elif isinstance(tab, BookingsReportTabM):
            self.parent.geometry("1440x320")


class AddFilmTabM(ttk.Frame):
    def __init__(self, parent, film_list):
        super().__init__(parent)

        self.film_list = film_list
        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Fields for managing films
        ttk.Label(container, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        self.name = tk.StringVar()
        name_entry = ttk.Entry(container, textvariable=self.name)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(container, text="Synopsis:").grid(row=1, column=0, padx=10, pady=5)
        self.syn = tk.StringVar()
        syn_entry = ttk.Entry(container, textvariable=self.syn)
        syn_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Genre:").grid(row=2, column=0, padx=10, pady=5)
        self.genre = tk.StringVar()
        ttk.Entry(container, textvariable=self.genre).grid(row=2, column=1, padx=10, pady=5)

        ratings = ['', 'G', 'PG', 'PG-13', 'R', 'NC-17', 'X']

        ttk.Label(container, text="Rating:").grid(row=3, column=0, padx=10, pady=5)
        self.rating = tk.StringVar()
        ttk.OptionMenu(container, self.rating, *ratings).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(container, text="Cinema ID:").grid(row=4, column=0, padx=10, pady=5)
        self.cinema_id = tk.IntVar()
        ttk.Entry(container, textvariable=self.cinema_id).grid(row=4, column=1, padx=10, pady=5)

        screens = ['', 1, 2, 3, 4, 5, 6]

        ttk.Label(container, text="Screen:").grid(row=5, column=0, padx=10, pady=5)
        self.screen = tk.IntVar()
        ttk.OptionMenu(container, self.screen, *screens).grid(row=5, column=1, padx=10, pady=5)
        
        ttk.Label(container, text="Screening Times:").grid(row=6, column=0, padx=10, pady=5)
        self.screentimes = tk.StringVar()
        ttk.Entry(container, textvariable=self.screentimes).grid(row=6, column=1, padx=10, pady=5)

        tk.Button(container, text="Add Film", command=self.add_film).grid(row=7, column=0, columnspan=2, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

    def add_film(self):
        new_film = {
            "name": self.name.get(),
            "synopsis": self.syn.get(),
            "genre": self.genre.get(),
            "rating": self.rating.get(),
            "cinema_id": self.cinema_id.get(),
            "screen": self.screen.get(),
            "screentimes": self.screentimes.get()
        }

        if all(new_film.values()):
            try:
                cur.execute(
                    "INSERT INTO FILMS (NAME, SYNOPSIS, GENRE, RATING, CINEMA_ID, SCREEN_TIME, SCREEN) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (new_film["name"], new_film["synopsis"], new_film["genre"], new_film["rating"], new_film["cinema_id"], new_film["screentimes"], new_film["screen"])
                )

                con.commit()
                self.film_list.populate_treeview()

                self.result.config(text=f"Film '{new_film['name']}' added")
            except Exception as e:
                self.result.config(text=f"Error Adding Film: {e}")
        else:
            self.result.config(text="All fields are required.")
       
class FilmListTabM(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns=("Name", "Synopsis", "Genre", "Rating", "Screening Times", "Screen", "Cinema")

        self.tree = ttk.Treeview(self, columns=columns)
        self.tree.heading("#0", text="Film ID")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            cur.execute("SELECT * FROM FILMS") # Manager can view all Films in every Cinema

            films = cur.fetchall()
            for film in films:
                cur.execute("SELECT NAME FROM CINEMAS WHERE ID = ?", (film[6],))
                cinema_name = cur.fetchone()
                self.tree.insert("", "end", text=film[0], values=(film[1], film[2], film[3], film[4], film[5], film[7], cinema_name[0]))
        except Exception as e:
             self.result.config(text=f"Error fetching films: {e}")
        
        
class EditFilmTabM(ttk.Frame):
    def __init__(self, parent, film_list):
        super().__init__(parent)

        self.film_list = film_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Edit Films using ID
        ttk.Label(container, text="Enter Film ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.film_id = tk.IntVar()
        ttk.Entry(container, textvariable=self.film_id).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(container, text="Load Film", command=self.load_film).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(container, text="Update Film", command=self.update_film).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(container, text="Remove Film", command=self.remove_film).grid(row=2, column=2, padx=10, pady=5)

        # Fields for editing film details
        ttk.Label(container, text="Name:").grid(row=1, column=0, padx=10, pady=5)
        self.name = tk.StringVar()
        ttk.Entry(container, textvariable=self.name, width=50).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Synopsis:").grid(row=2, column=0, padx=10, pady=5)
        self.syn = tk.StringVar()
        ttk.Entry(container, textvariable=self.syn, width=50).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Genre:").grid(row=3, column=0, padx=10, pady=5)
        self.genre = tk.StringVar()
        ttk.Entry(container, textvariable=self.genre).grid(row=3, column=1, padx=10, pady=5)

        ratings = ['', 'G', 'PG', 'PG-13', 'R', 'NC-17', 'X']

        ttk.Label(container, text="Rating:").grid(row=4, column=0, padx=10, pady=5)
        self.rating = tk.StringVar()
        ttk.OptionMenu(container, self.rating, *ratings).grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(container, text="Cinema ID:").grid(row=5, column=0, padx=10, pady=5)
        self.cinema_id = tk.IntVar()
        ttk.Entry(container, textvariable=self.cinema_id).grid(row=5, column=1, padx=10, pady=5)

        screens = ['', 1, 2, 3, 4, 5, 6]

        ttk.Label(container, text="Screen:").grid(row=6, column=0, padx=10, pady=5)
        self.screen = tk.IntVar()
        ttk.OptionMenu(container, self.screen, *screens).grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(container, text="Screening Times:").grid(row=7, column=0, padx=10, pady=5)
        self.screentimes = tk.StringVar()
        ttk.Entry(container, textvariable=self.screentimes, width=50).grid(row=7, column=1, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

    def load_film(self):
        film_id = self.film_id.get()

        if film_id:
            try:
                cur.execute("SELECT * FROM FILMS WHERE ID = ?", (film_id,))
                film = cur.fetchone()
                if film:
                    # Display film details
                    self.name.set(film[1])
                    self.syn.set(film[2])
                    self.genre.set(film[3])
                    self.rating.set(film[4])
                    self.cinema_id.set(film[6])
                    self.screen.set(film[7])
                    self.screentimes.set(film[5])
                    
                    self.result.config(text=f"Loaded Film ID '{film_id}'")
                else:
                    self.result.config(text="Film ID Not Found")
            except Exception as e:
                self.result.config(text=f"Error loading film: {e}")
        else:
            self.result.config(text="Film ID field is required.")

    def update_film(self):
        film_id = self.film_id.get()

        name = self.name.get()
        synopsis = self.syn.get()
        genre = self.genre.get()
        rating = self.rating.get()
        cinema_id = self.cinema_id.get()
        screen = self.screen.get()
        screentimes = self.screentimes.get()

        if name and synopsis and genre and rating and cinema_id and screen and screentimes:
            try:
                cur.execute(
                "UPDATE FILMS SET NAME = ?, SYNOPSIS = ?, GENRE = ?, RATING = ?, SCREEN_TIME = ?, CINEMA_ID = ?, SCREEN = ? WHERE ID = ?",
                (name, synopsis, genre, rating, screentimes, cinema_id, screen, film_id)  # Update in DB
                )

                con.commit()
                self.film_list.populate_treeview()

                self.result.config(text=f"Film ID '{film_id}' updated.")
            except Exception as e:
                self.result.config(text=f"Error Updating Film: {e}")
        else:
            self.result.config(text="All fields are required.")

    def remove_film(self):
        film_id = self.film_id.get()

        if film_id:
            try:
                cur.execute("DELETE FROM FILMS WHERE ID=?", (film_id,))

                con.commit()
                self.bookings_list.populate_treeview()
                
                self.result.config(text=f"Film '{film_id}' removed")

            except Exception as e:
                self.result.config(text=f"Error Deleting Booking: {e}")
        else:
            self.result.config(text="Film ID field is required.")

class UserListTabM(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns = ("Full Name", "Email", "Role", "Cinema")
        self.tree = ttk.Treeview(self, columns=columns)
        self.tree.heading("#0", text="ID")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            cur.execute("SELECT ID, FULL_NAME, EMAIL, ROLE, CINEMA_ID FROM USERS")
            users = cur.fetchall()
            for user in users:
                cur.execute("SELECT NAME FROM CINEMAS WHERE ID = ?", (user[4],))
                cinema_name = cur.fetchone()
                self.tree.insert("", "end", text=user[0], values=(user[1], user[2], user[3], cinema_name[0]))
        except Exception as e:
            self.result.config(text=f"Error fetching users: {e}")


class AddUserTabM(ttk.Frame):
    def __init__(self, parent, user_list):
        super().__init__(parent)

        self.user_list = user_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Fields for entering user details
        ttk.Label(container, text="Enter User ID:").grid(row=0, column=0, padx=10, pady=5)
        self.id = tk.IntVar()
        ttk.Entry(container, textvariable=self.id).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(container, text="First Name:").grid(row=1, column=0, padx=10, pady=5)
        self.firstname = tk.StringVar()
        ttk.Entry(container, textvariable=self.firstname).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Last Name:").grid(row=2, column=0, padx=10, pady=5)
        self.lastname = tk.StringVar()
        ttk.Entry(container, textvariable=self.lastname).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Email:").grid(row=3, column=0, padx=10, pady=5)
        self.email = tk.StringVar()
        ttk.Entry(container, textvariable=self.email).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(container, text="Password:").grid(row=4, column=0, padx=10, pady=5)
        self.password = tk.IntVar()
        ttk.Entry(container, textvariable=self.password).grid(row=4, column=1, padx=10, pady=5)

        roles = ['', 'Staff', 'Admin', 'Manager']
        
        ttk.Label(container, text="Role:").grid(row=5, column=0, padx=10, pady=5)
        self.role = tk.StringVar()
        ttk.OptionMenu(container, self.role, *roles).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(container, text="Cinema ID:").grid(row=6, column=0, padx=10, pady=5)
        self.cinema_id = tk.IntVar()
        ttk.Entry(container, textvariable=self.cinema_id).grid(row=6, column=1, padx=10, pady=5)

        tk.Button(container, text="Register User", command=self.add_user).grid(row=7, column=0, columnspan=2, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

    def add_user(self):
        new_user = {
            "id": self.id.get(),
            "first_name": self.firstname.get(),
            "last_name": self.lastname.get(),
            "email": self.email.get(),
            "password": self.password.get(),
            "role": self.role.get(),
            "cinema_id": self.cinema_id.get()
        }

        if all(new_user.values()):
            try:
                cur.execute(
                    "INSERT INTO USERS (ID, FIRST_NAME, LAST_NAME, EMAIL, PASSWORD, ROLE, CINEMA_ID) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (new_user["id"], new_user["first_name"], new_user["last_name"], new_user["email"], new_user["password"], new_user["role"], new_user["cinema_id"])
                )

                con.commit()
                self.user_list.populate_treeview()

                self.result.config(text=f"User '{new_user['first_name']}' added with Role '{new_user['role']}' ")
            except Exception as e:
                self.result.config(text=f"Error Registering User: {e}")
        else:
            self.result.config(text="All fields are required.")
   
        
class EditUserTabM(ttk.Frame):
    def __init__(self, parent, user_list):
        super().__init__(parent)

        self.user_list = user_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Components for selecting a user by ID
        ttk.Label(container, text="Enter User ID:").grid(row=0, column=0, padx=10, pady=5)
        self.user_id = tk.StringVar()
        ttk.Entry(container, textvariable=self.user_id).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(container, text="Load User Details", command=self.load_user).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(container, text="Update User Details", command=self.update_user).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(container, text="Remove User", command=self.remove_user).grid(row=2, column=2, padx=10, pady=5)

        # Fields for editing user details
        ttk.Label(container, text="First Name:").grid(row=1, column=0, padx=10, pady=5)
        self.firstname = tk.StringVar()
        ttk.Entry(container, textvariable=self.firstname).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Last Name:").grid(row=2, column=0, padx=10, pady=5)
        self.lastname = tk.StringVar()
        ttk.Entry(container, textvariable=self.lastname).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Email:").grid(row=3, column=0, padx=10, pady=5)
        self.email = tk.StringVar()
        ttk.Entry(container, textvariable=self.email).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(container, text="Password:").grid(row=4, column=0, padx=10, pady=5)
        self.password = tk.StringVar()
        ttk.Entry(container, textvariable=self.password).grid(row=4, column=1, padx=10, pady=5)
        
        roles = ['', 'Staff', 'Admin', 'Manager']
        
        ttk.Label(container, text="Role:").grid(row=5, column=0, padx=10, pady=5)
        self.role = tk.StringVar()
        ttk.OptionMenu(container, self.role, *roles).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(container, text="Cinema ID:").grid(row=6, column=0, padx=10, pady=5)
        self.cinema_id = tk.IntVar()
        ttk.Entry(container, textvariable=self.cinema_id).grid(row=6, column=1, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

    def load_user(self):
        user_id = self.user_id.get()

        if user_id:
            try:
                cur.execute("SELECT * FROM USERS WHERE ID = ?", (user_id,))
                user = cur.fetchone()

                if user:
                    # Display user details in the entry fields
                    self.firstname.set(user[1])
                    self.lastname.set(user[2])
                    self.email.set(user[4])
                    self.password.set(user[5])
                    self.role.set(user[6])
                    self.cinema_id.set(user[7])
                    
                    self.result.config(text=f"Loaded {user_id} - {self.firstname.get()}")
                else:
                    self.result.config(text="User ID not Found")
            except Exception as e:
                self.result.config(text=f"Error loading user: {e}")
        else:
            self.result.config(text="User ID Field is Required")

    def update_user(self):
        user_id = self.user_id.get()

        firstname = self.firstname.get()
        lastname = self.lastname.get()
        email = self.email.get()
        password = self.password.get()
        role = self.role.get()
        cinema_id = self.cinema_id.get()

        if firstname and lastname and email and password and role and cinema_id:
            try:
                cur.execute(
                "UPDATE USERS SET FIRST_NAME = ?, LAST_NAME = ?, EMAIL = ?, PASSWORD = ?, ROLE = ?, CINEMA_ID = ? WHERE ID = ?",
                (firstname, lastname, email, password, role, cinema_id, user_id)
            )
                con.commit()
                self.user_list.populate_treeview()

                self.result.config(text=f"{user_id} - {self.firstname.get()} updated")
            except Exception as e:
                self.result.config(text=f"Error Updating User: {e}")
        else:
            self.result.config(text="All fields are required.")

    def remove_user(self):
        user_id = self.user_id.get()
        
        if user_id:
            try:
            
                cur.execute("DELETE FROM USERS WHERE ID=?", (user_id,))

                con.commit()
                self.user_list.populate_treeview()
                
                self.result.config(text=f"User '{user_id}' removed")
            except Exception as e:
                self.result.config(text=f"Error Deleting Booking: {e}")
        else:
            self.result.config(text="User ID field is required.")
            
class BookingsReportTabM(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns = ("Filled by Staff", "Film", "Tickets", "Total Price", "Booked Date", "Show Time")
        self.tree = ttk.Treeview(self, columns=columns)
        
        self.tree.heading("#0", text="Reference")
        self.tree.column("#0", anchor="w")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.populate_treeview()

        tk.Button(self, text=f"Generate Report", command=self.generate_report).grid(row=4, column=0) # Only displays Total Money Earned for now

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            cur.execute('''
                SELECT BOOKINGS.REFERENCE, BOOKINGS.STAFF_ID, FILMS.NAME, BOOKINGS.TICKET_COUNT, BOOKINGS.TOTAL_PRICE, BOOKINGS.BOOK_DATE, BOOKINGS.SHOW_TIME
                FROM BOOKINGS
                JOIN FILMS ON BOOKINGS.FILM_ID = FILMS.ID
            ''')
            bookings = cur.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6]))
        except Exception as e:
            print(f"Error fetching bookings: {e}")

    def generate_report(self):
        report_win = tk.Toplevel()
        report_win.title("Report")
        report_win.geometry("265x145")
        report_win.resizable(False, False)

        cur.execute('''
                    SELECT SUM(TOTAL_PRICE), SUM(TICKET_COUNT)
                    FROM BOOKINGS
            ''')
        booking_sums = cur.fetchall()  # Fetch the sum value from the query result

        rev_result = ttk.Label(report_win, text=f"Total Money Earned: {booking_sums[0][0]}") # Rev for Revenue
        rev_result.pack()

        ticket_result = ttk.Label(report_win, text=f"Total Tickets Booked: {booking_sums[0][1]}")
        ticket_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM SEATS
                    WHERE STATUS = 'Reserved'
            ''')
        seat_sums = cur.fetchall()

        seats_result = ttk.Label(report_win, text=f"Total Seats Reserved: {seat_sums[0][0]}")
        seats_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM FILMS
            ''')
        film_sums = cur.fetchall()

        films_result = ttk.Label(report_win, text=f"Total Films Playing: {film_sums[0][0]}")
        films_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM SCREENS
            ''')
        screen_sums = cur.fetchall()

        screen_result = ttk.Label(report_win, text=f"Total Screens: {screen_sums[0][0]}")
        screen_result.pack()

        cur.execute('''
                    SELECT COUNT(*)
                    FROM USERS
            ''')
        screen_sums = cur.fetchall()

        users_result = ttk.Label(report_win, text=f"Total Users: {screen_sums[0][0]}")
        users_result.pack()

class CinemaListTabM(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        columns = ("Name", "City", "Address")

        self.tree = ttk.Treeview(self, columns=columns)
        self.tree.heading("#0", text="Cinema ID")

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.result = ttk.Label(self, text="")
        self.result.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            cur.execute("SELECT * FROM CINEMAS") 

            cinemas = cur.fetchall()
            for cinema in cinemas:
                self.tree.insert("", "end", text=cinema[0], values=(cinema[1], cinema[2], cinema[3]))
        except Exception as e:
            self.result.config(text=f"Error fetching cinemas: {e}")

class AddCinemaTabM(ttk.Frame):
    def __init__(self, parent, cinema_list):
        super().__init__(parent)

        self.cinema_list = cinema_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Fields for adding new cinemas
        ttk.Label(container, text="City").grid(row=0, column=0, padx=10, pady=5)
        self.city = tk.StringVar()
        ttk.Entry(container, textvariable=self.city).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(container, text="ID").grid(row=1, column=0, padx=10, pady=5)
        self.id = tk.StringVar()
        ttk.Entry(container, textvariable=self.id).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="Cinema Name").grid(row=2, column=0, padx=10, pady=5)
        self.name = tk.StringVar()
        ttk.Entry(container, textvariable=self.name).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(container, text="Address:").grid(row=3, column=0, padx=10, pady=5)
        self.addr = tk.StringVar()
        ttk.Entry(container, textvariable=self.addr).grid(row=3, column=1, padx=10, pady=5)

        tk.Button(container, text="Add Cinema", command=self.add_cinema).grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

    def add_cinema(self):
        id = self.id.get()
        city = self.city.get()
        name = self.name.get()
        address = self.addr.get()

        if id and city and name and address:
            try:
                cur.execute(
                    "INSERT INTO CINEMAS (ID, CITY, NAME, ADDRESS) VALUES (?, ?, ?, ?)",
                    (id, city, name, address)
                )

                con.commit()
                self.cinema_list.populate_treeview()

                self.result.config(text=f"Cinema '{name}' added to city '{city}' at '{address}' with ID '{id}'.")
            except Exception as e:
                self.result.config(text=f"Error Adding Cinema: {e}")
        else:
            self.result.config(text="All fields are required.")

class EditCinemaTabM(ttk.Frame):
    def __init__(self, parent, cinema_list, film_list, user_list):
        super().__init__(parent)

        self.cinema_list = cinema_list
        self.film_list = film_list
        self.user_list = user_list

        # Container frame
        container = ttk.Frame(self)
        container.grid(row=0, column=0, padx=10, pady=10)

        # Center Container frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Edit Films using ID
        ttk.Label(container, text="Enter Cinema ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.cinema_id = tk.IntVar()
        ttk.Entry(container, textvariable=self.cinema_id).grid(row=0, column=1, padx=10, pady=5)

        tk.Button(container, text="Load Cinema", command=self.load_cinema).grid(row=0, column=2, padx=10, pady=5)
        tk.Button(container, text="Update Cinema Details", command=self.update_cinema).grid(row=1, column=2, padx=10, pady=5)
        tk.Button(container, text="Remove Cinema", command=self.remove_cinema).grid(row=2, column=2, padx=10, pady=5)

        # Fields for editing film details
        ttk.Label(container, text="Name:").grid(row=1, column=0, padx=10, pady=5)
        self.name = tk.StringVar()
        ttk.Entry(container, textvariable=self.name, width=50).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(container, text="City:").grid(row=2, column=0, padx=10, pady=5)
        self.city = tk.StringVar()
        ttk.Entry(container, textvariable=self.city).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(container, text="Address:").grid(row=3, column=0, padx=10, pady=5)
        self.addr = tk.StringVar()
        ttk.Entry(container, textvariable=self.addr).grid(row=3, column=1, padx=10, pady=5)

        self.result = ttk.Label(container, text="")
        self.result.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

    def load_cinema(self):
        cinema_id = self.cinema_id.get()

        if cinema_id:
            try:
                cur.execute("SELECT * FROM CINEMAS WHERE ID = ?", (cinema_id,))
                cinema = cur.fetchone()
                if cinema:
                    self.name.set(cinema[1])
                    self.city.set(cinema[2])
                    self.addr.set(cinema[3])
                    
                    self.result.config(text=f"Loaded Cinema ID '{cinema_id}'")
                else:
                    self.result.config(text="Cinema ID Not Found")
            except Exception as e:
                self.result.config(text=f"Error loading cinema: {e}")
        else:
            self.result.config(text="Cinema ID field is required.")

    def update_cinema(self):
        cinema_id = self.cinema_id.get()

        name = self.name.get()
        city = self.city.get()
        addr = self.addr.get()

        if name and city and addr:
            try:
                cur.execute(
                "UPDATE CINEMAS SET NAME = ?, CITY = ?, ADDRESS = ? WHERE ID = ?",
                (name, city, addr, cinema_id)  # Update in DB
                )

                con.commit()
                self.cinema_list.populate_treeview()
                self.film_list.populate_treeview()
                self.user_list.populate_treeview()

                self.result.config(text=f"Cinema ID '{cinema_id}' updated.")
            except Exception as e:
                self.result.config(text=f"Error Updating cinema: {e}")
        else:
            self.result.config(text="All fields are required.")

    def remove_cinema(self):
        cinema_id = self.cinema_id.get()

        if cinema_id:
            try:
                cur.execute("DELETE FROM CINEMAS WHERE ID=?", (cinema_id,))

                con.commit()
                self.cinema_list.populate_treeview()
                self.film_list.populate_treeview()
                self.user_list.populate_treeview()
                
                self.result.config(text=f"Cinema '{cinema_id}' removed")

            except Exception as e:
                self.result.config(text=f"Error deleting cinema: {e}")
        else:
            self.result.config(text="Cinema ID field is required.")


if __name__ == "__main__":
    login_main()