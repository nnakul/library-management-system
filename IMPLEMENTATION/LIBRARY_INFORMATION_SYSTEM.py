
"""
    LIBRARY INFORMATION SYSTEM
    Developed by CODING CONNOISSEURS
        --  Ashwamegh Rathore
        --  Nakul Aggarwal
        --  Rupinder Goyal
""" 

from tkinter import *
from datetime import *
from tkcalendar import *
from tkinter.font import Font
from tkinter import font as tkFont
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from hashlib import md5
from uuid import uuid4
from random import randint
from cryptography.fernet import Fernet
import threading


class ApplicationState :		#initialization of software
    #class attributes
    Root = None
    CurrentUser = None
    CurrentWidgets = list()
    OldPasswordField = None
    NewPasswordField = None
    ConfirmPasswordField = None
    ChooseMemberField = None
    ThreadTimer = None

    @classmethod
    def CheckExpiredReservations ( cls ) :
    	#connect to database "library"
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        cursorr = db.cursor(buffered=True)
        #select books which have been returned
        cursorr.execute("SELECT * FROM ReservedBooks WHERE IsReturned=1")
        results = cursorr.fetchall()
        if ( len(results) == 0 ) :	#if no current reservation of books has been made
            ApplicationState.ThreadTimer = threading.Timer(ApplicationDesign.ThreadCycle, ApplicationState.CheckExpiredReservations)
            ApplicationState.ThreadTimer.start()	#start threading for concurrent program execution
            db.close()
            return
        #if curretn reservation for books is present
        for rec in results :
            dor = datetime.strptime(rec[6], '%d/%m/%Y')
            delay = (datetime.now()-dor).days
            if ( delay > 7 ) :	#if the reserver has not issued  book within 7 days of availabilty of book cancel reservation
                issueId = rec[2]
                cursorr.execute("SELECT * FROM BooksIssuedInPast WHERE IssueId=%s", (issueId,))
                isbn = cursorr.fetchall()[0][1]
                cursorr.execute("UPDATE Catalogue SET Available=Available+1 WHERE ISBN=%s", (isbn,))	#make the reserved book available
                db.commit()
                cursorr.execute("DELETE FROM ReservedBooks WHERE IssueId=%s", (issueId,))		#delete reservation
                db.commit()
                msg = """Dear Member,\nThe reservation of an issued book that you did a while back has gotten expired. You were late in formally issuing the reserved book within 7 days after it was returned. The details of the former reservation are given below.\n\n\tRESERVATION ID    :   {}\n\tISBN              :   {}\n\nThank you.\nRegards.\nLIS.
                      """.format(rec[0], isbn)		#send message to reserver about the cancellation of reservation
                Clerk.NotifyMember("RESERVATION EXPIRED", msg, rec[3])

        db.close()
        ApplicationState.ThreadTimer = threading.Timer(ApplicationDesign.ThreadCycle, ApplicationState.CheckExpiredReservations)
        ApplicationState.ThreadTimer.start()	#start threading for concurrent program execution
        return

    @classmethod
    def ShowHomePage ( cls ) :		#homepage GUI design
    	#clear/unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #homepage has 4 widgets
        Header = Label(ApplicationState.Root, text="LIBRARY INFORMATION SYSTEM", fg="white", bg=ApplicationDesign.Theme, anchor=W, width=48, bd=5, font=('',40,'bold'))
        Header.grid(row=0, column=0, columnspan=36)
        querySection = Button(ApplicationState.Root, text='QUERY SECTION', bg='white',  font=('',30,'bold'), command = ApplicationState.ShowQuerySection)
        signInAsLibrarian = Button(ApplicationState.Root, text='LOGIN AS LIBRARIAN', bg='white',  font=('',30,'bold'), command = ApplicationState.ShowLibrarianLoginPage)
        signInAsClerk = Button(ApplicationState.Root, text='LOGIN AS CLERK', bg='white',  font=('',30,'bold'), command = ApplicationState.ShowClerkLoginPage)
        signInAsMember = Button(ApplicationState.Root, text='LOGIN AS MEMBER', bg='white',  font=('',30,'bold'), command = ApplicationState.ShowMemberLoginPage)
        

        span = 32
        start = 4
        gap = 35
        #adjusting different elements on homepage-
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        col = 1
        querySection.grid(row=start, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+1, minsize=gap)

        signInAsLibrarian.grid(row=start+2, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+3, minsize=gap)

        signInAsClerk.grid(row=start+4, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+5, minsize=gap)

        signInAsMember.grid(row=start+6, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+7, minsize=gap)
        
        ApplicationState.CurrentWidgets = [querySection, signInAsLibrarian, signInAsClerk, signInAsMember]	#widgets on homepage

    @classmethod
    def ShowMemberLoginPage ( cls ) :	#member login page design 
    	#clear/unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #background and heading design
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  LOG IN AS MEMBER", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=0, columnspan=34)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)
        #login id section
        initRow = 6
        askLoginId = Label(ApplicationState.Root, text="LOGIN ID  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        loginId = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        askLoginId.grid(row=initRow, column=2, columnspan=8)
        loginId.grid(row=initRow, column=13, columnspan=20)
        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #password section- the input from user is hidden by replacing text with '●'
        initRow = 8
        askPassword = Label(ApplicationState.Root, text="PASSWORD  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        password = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme, show='●')
        askPassword.grid(row=initRow, column=2, columnspan=8)
        password.grid(row=initRow, column=13, columnspan=20)

        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #go back button
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = ApplicationState.ShowHomePage)
        goBack.grid(row=initRow+2, column=5, columnspan=7, sticky=W+E)
        #login button
        logIn = Button(ApplicationState.Root, text='LOG IN', bg='white',  font=('',20,'bold'), command=lambda : Member.IsValidMember(loginId.get(),password.get()) )
        logIn.grid(row=initRow+2, column=23, columnspan=7, sticky=W+E)

        ApplicationState.CurrentWidgets = [head, askLoginId, loginId, askPassword, password, goBack, logIn]	#list of widget on member login page

    @classmethod
    def ShowClerkLoginPage ( cls ) :	#clerk login page design
    	#clear/unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #background and heading design
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  LOG IN AS CLERK", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=34)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)
        #login id section
        initRow = 6
        askLoginId = Label(ApplicationState.Root, text="LOGIN ID  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        loginId = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        askLoginId.grid(row=initRow, column=2, columnspan=8)
        loginId.grid(row=initRow, column=13, columnspan=20)
        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #password section- the input from user is hidden by replacing text with '●'
        initRow = 8
        askPassword = Label(ApplicationState.Root, text="PASSWORD  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        password = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme, show='●')
        askPassword.grid(row=initRow, column=2, columnspan=8)
        password.grid(row=initRow, column=13, columnspan=20)

        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #go back button-
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = ApplicationState.ShowHomePage)
        goBack.grid(row=initRow+2, column=5, columnspan=7, sticky=W+E)
        #login button-
        logIn = Button(ApplicationState.Root, text='LOG IN', bg='white',  font=('',20,'bold'), command=lambda : Clerk.IsValidClerk(loginId.get(),password.get()) )
        logIn.grid(row=initRow+2, column=23, columnspan=7, sticky=W+E)

        ApplicationState.CurrentWidgets = [head, askLoginId, loginId, askPassword, password, goBack, logIn]		#list of widget on clerk login page
    
    @classmethod
    def ShowLibrarianLoginPage ( cls ) :		#librarian login page design
    	#clear/unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #background and heading design
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  LOG IN AS LIBRARIAN", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=34)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)
        #login id section
        initRow = 6
        askLoginId = Label(ApplicationState.Root, text="LOGIN ID  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        loginId = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        askLoginId.grid(row=initRow, column=2, columnspan=8)
        loginId.grid(row=initRow, column=13, columnspan=20)
        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #password section- the input from user is hidden by replacing text with '●'
        initRow = 8
        askPassword = Label(ApplicationState.Root, text="PASSWORD  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        password = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme, show='●')
        askPassword.grid(row=initRow, column=2, columnspan=8)
        password.grid(row=initRow, column=13, columnspan=20)

        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #go back button-
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = ApplicationState.ShowHomePage)
        goBack.grid(row=initRow+2, column=5, columnspan=7, sticky=W+E)
        #login button-
        logIn = Button(ApplicationState.Root, text='LOG IN', bg='white',  font=('',20,'bold'), command=lambda : Librarian.IsValidLibrarian(loginId.get(),password.get()) )
        logIn.grid(row=initRow+2, column=23, columnspan=7, sticky=W+E)
        #list of widget on librarian login page-
        ApplicationState.CurrentWidgets = [head, askLoginId, loginId, askPassword, password, goBack, logIn]

    @classmethod
    def ShowQuerySection ( cls ) :		#query section GUI design
    	#clear/unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #background and heading design-
        head = Label(ApplicationState.Root, text="  □  CATALOGUE QUERY SECTION", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=3, column=1, columnspan=32)
        #design of drop down menu to select mode of searching-
        criteria = [ "ISBN" , "Title" , "Author" ]
        ApplicationState.ChooseMemberField = StringVar() 
        ApplicationState.ChooseMemberField.set( "CHOOSE SEARCH CRITERIA" ) 
        drop = OptionMenu( ApplicationState.Root , ApplicationState.ChooseMemberField , *criteria )

        helv36 = tkFont.Font(family='', size=22, weight="bold")
        drop.config(font=helv36)

        helv20 = tkFont.Font(family='', size=20)
        menu = ApplicationState.Root.nametowidget(drop.menuname)
        menu.config(font=helv20)

        value = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #search button
        search = Button(ApplicationState.Root, text="SEARCH", bg='white',  font=('',20,'bold'), command = ApplicationState.SearchQuery)
        #go back to homepage
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = ApplicationState.ShowHomePage)

        initRow = 6
        height = 13
        #search result GUI design-
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        #table to display search result  for books 
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=32, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #scroll bar to browse along search result
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #column elements of the search table catalogue
        table['columns'] = ('ISBN', 'TITLE', 'AUTHOR', 'LANGUAGE', 'RACK NO.', 'TOTAL COPIES', 'AVAILABLE COPIES')
        table.column('#0', width=0, stretch=NO)
        table.column('ISBN', width=150, minwidth=25)
        table.column('TITLE', width=340, minwidth=25)
        table.column('AUTHOR', width=330, minwidth=25)
        table.column('LANGUAGE', width=135, minwidth=25)
        table.column('RACK NO.', width=95, minwidth=25)
        table.column('TOTAL COPIES', width=130, minwidth=25)
        table.column('AVAILABLE COPIES', width=130, minwidth=25)
        #heading of each column-
        table.heading('#0', text='')
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('TITLE', text='TITLE', anchor=CENTER)
        table.heading('AUTHOR', text='AUTHOR(s)', anchor=CENTER)
        table.heading('LANGUAGE', text='LANGUAGE', anchor=CENTER)
        table.heading('RACK NO.', text='RACK NO.', anchor=CENTER)
        table.heading('TOTAL COPIES', text='TOTAL', anchor=CENTER)
        table.heading('AVAILABLE COPIES', text='AVAILABLE', anchor=CENTER)

        ApplicationState.Root.grid_rowconfigure(initRow, minsize=4)
        
        start = 4
        gap = 25
        span2 = 17
        #sizing and placement of different widgets-
        ApplicationState.Root.grid_rowconfigure(start, minsize=gap)
        drop.grid(row=start+1, column=2, columnspan=10, sticky=W+E)
        value.grid(row=start+1, column=13, columnspan=span2, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+8, minsize=gap)
        goBack.grid(row=start+13, column=6, columnspan=8, sticky=W+E)
        search.grid(row=start+13, column=22, columnspan=8, sticky=W+E)
        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)
        #list of widgets on search page
        ApplicationState.CurrentWidgets = [ head , drop , value , search , goBack , treeFrame , scrollbar , table ]

    @classmethod
    def SearchQuery ( cls ) :	#backend opeations of search query-

        if ( ApplicationState.ChooseMemberField.get() == "CHOOSE SEARCH CRITERIA" ) :	#error if search method from drop  down menu not selected
            messagebox.showerror("", "Search criteron was not chosen!")
            return
        if ( ApplicationState.CurrentWidgets[2].get().strip() == "" ) :		#if no search query was specified display error
            messagebox.showerror("", "Query was not specified!")
            return
        #connect to database 'Library' storing the books 
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )

        cursorr = db.cursor(buffered=True)

        criterion = ApplicationState.ChooseMemberField.get()
        # search using REGEXP by the criterion specified
        if ( criterion == "Title" ) :
            cursorr.execute("SELECT * FROM Catalogue WHERE Title REGEXP %s", 
                (ApplicationState.CurrentWidgets[2].get().strip(), ))
        elif ( criterion == "Author" ) :
            cursorr.execute("SELECT * FROM Catalogue WHERE AUTHOR REGEXP %s", 
                (ApplicationState.CurrentWidgets[2].get().strip(), ))
        elif ( criterion == "ISBN" ) :
            cursorr.execute("SELECT * FROM Catalogue WHERE ISBN REGEXP %s", 
                (ApplicationState.CurrentWidgets[2].get().strip(), ))
        #extract search results form database-
        results = cursorr.fetchall()

        for rec in ApplicationState.CurrentWidgets[-1].get_children() :
            ApplicationState.CurrentWidgets[-1].delete(rec)
        #add the search result on GUI page
        i = 1
        for rec in results :
            ApplicationState.CurrentWidgets[-1].insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6]))
            i += 1
        
        db.close()
        #if no matching book found-
        if ( i == 1 ) :
            messagebox.showinfo("", "No relevant records discovered!")
        

class ApplicationDesign :		#important attributes for interface and implementation of LIS
	#class attributes-
    BackgroundColor = "#DEB887"		#color theme for background
    Theme = "#D2691E"				#color theme for text padding
    MessagesFernetKey = b'M5JKTgGEX9nwUYYwHab9vuHiNok7tdgK5dMPHuf5iv8=' 		#symmetric key encryption
    Password = ""		#fill in Password for mysql
    DatabaseUser = ""			#enter the username for mysql-default is root
    Penalty = 5.00					
    MaxIssueLimitUG = 2
    MaxIssueLimitPG = 4
    MaxIssueLimitRS = 6
    MaxIssueLimitFC = 10
    HighlightThickness = 4
    ThreadCycle = 21600.00


class Individual :	#class of account holders-
    
    def __init__ ( self , idd , name , dob , regDate ) :	#constructor
        self.__id = idd
        self.__name = name
        self.__dob = dob
        self.__regDate = regDate
        self.__status = None
    
    @staticmethod
    def ResetPassword ( ) :		#GUI to reset password after being assigned default password
        ApplicationState.OldPasswordField.set("")
        ApplicationState.NewPasswordField.set("")
        ApplicationState.ConfirmPasswordField.set("")
    	#clear/unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #bakcground and heading design-
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  RESET PASSWORD", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=34)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)
        #GUI for old password entry-
        initRow = 6
        askOldPw = Label(ApplicationState.Root, text="OLD PASSWORD  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), anchor=CENTER)
        oldPw = Entry(ApplicationState.Root, textvariable = ApplicationState.OldPasswordField, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme, show='●')
        askOldPw.grid(row=initRow, column=2, columnspan=8, sticky=W+E)
        oldPw.grid(row=initRow, column=13, columnspan=20)
        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #GUI for new password entry
        initRow = 8
        askNewPw = Label(ApplicationState.Root, text="NEW PASSWORD  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), anchor=CENTER)
        newPw = Entry(ApplicationState.Root, textvariable = ApplicationState.NewPasswordField, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme, show='●')
        askNewPw.grid(row=initRow, column=2, columnspan=8, sticky=W+E)
        newPw.grid(row=initRow, column=13, columnspan=20)
        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #GUI to enter new password to confirm
        initRow = 10
        askAgain = Label(ApplicationState.Root, text="CONFIRM PASSWORD  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), anchor=CENTER)
        repPw = Entry(ApplicationState.Root, textvariable = ApplicationState.ConfirmPasswordField, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme, show='●')
        askAgain.grid(row=initRow, column=2, columnspan=8, sticky=W+E)
        repPw.grid(row=initRow, column=13, columnspan=20)
        ApplicationState.Root.grid_rowconfigure(initRow+1, minsize=35)
        #go back to user dashboard
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ShowFirstPage)
        goBack.grid(row=initRow+2, column=5, columnspan=7, sticky=W+E)
        #confirm password change-
        change = Button(ApplicationState.Root, text='RESET PASSWORD', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ChangePassword )
        change.grid(row=initRow+2, column=23, columnspan=7, sticky=W+E)
        #list of widgets 
        ApplicationState.CurrentWidgets = [head, askOldPw, oldPw, askNewPw, newPw, askAgain, repPw, goBack, change]


class Member ( Individual ) :	#Member is a specialization of Individual

    def __init__ ( self , idd , name , dob , regDate , issueCount ) :		#constructor 
        self.__issueCount = issueCount 		#set issue count of user 
        Individual.__init__( self , idd , name , dob , regDate )

    @staticmethod
    def IsValidMember ( loginId , password ) :		#check if a user with entered loginid/password is in the database
        #connect to Accounts database
        db = mysql.connector.connect (
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #fetch list of members with matching LMCN
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s", (loginId,))
        nonFacMem = cursorr.fetchall()
        cursorr.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s", (loginId,))
        facMem = cursorr.fetchall()
        db.close()
        #if no matching LMCN found throw error
        if ( not len(nonFacMem) and not len(facMem) ) :
            messagebox.showerror('ERROR', 'Incorrect LMCN entered !')
            return
        #if LMCN matches and password for non faculty member does not then throw error-
        if ( len(nonFacMem) and nonFacMem[0][6] != md5(password.encode()).hexdigest() ) :
            messagebox.showerror('ERROR', 'Incorrect password entered !')
            return
        #if credentials validated for non faculty member login successful
        elif ( len(nonFacMem) ) :
            categ = nonFacMem[0][0][:2]
            if categ == 'UG' :  ApplicationState.CurrentUser = UnderGraduate(loginId , nonFacMem[0][1] , nonFacMem[0][2] , nonFacMem[0][3] , nonFacMem[0][4] , nonFacMem[0][5])
            if categ == 'PG' :  ApplicationState.CurrentUser = PostGraduate(loginId , nonFacMem[0][1] , nonFacMem[0][2] , nonFacMem[0][3] , nonFacMem[0][4] , nonFacMem[0][5])
            if categ == 'RS' :  ApplicationState.CurrentUser = ResearchScholar(loginId , nonFacMem[0][1] , nonFacMem[0][2] , nonFacMem[0][3] , nonFacMem[0][4] , nonFacMem[0][5])

        #if LMCN matches and password for faculty member does not then throw error-
        if ( len(facMem) and facMem[0][5] != md5(password.encode()).hexdigest() ) :
            messagebox.showerror('ERROR', 'Incorrect password entered !')
            return
        #if credentials validated for faculty member login successful
        elif ( len(facMem) ) :
            ApplicationState.CurrentUser = Faculty(loginId , facMem[0][1] , facMem[0][2] , facMem[0][3] , facMem[0][4] , facMem[0][5])
        #enter account of user
        Member.ShowFirstPage()
        return
        
    @staticmethod
    def ShowFirstPage ( ) :		#GUI design for user dashboard
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #buttons for widgets-
        showCurrentlyIssued = Button(ApplicationState.Root, text='SHOW CURRENTLY ISSUED BOOKS', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ShowCurrentlyIssuedBooks)
        showIssuedInPast = Button(ApplicationState.Root, text='SHOW BOOKS ISSUED IN PAST', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ShowBooksIssuedInPast)
        showMessages = Button(ApplicationState.Root, text='SHOW MESSAGES', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ShowMessages)
        resetPassword = Button(ApplicationState.Root, text='RESET PASSWORD', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ResetPassword)
        
        span = 30
        start = 4
        gap = 35
        col = 2
        #design and placement of widgets on GUI-
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        
        showCurrentlyIssued.grid(row=start, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+1, minsize=gap)
        showIssuedInPast.grid(row=start+2, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+3, minsize=gap)
        showMessages.grid(row=start+4, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+5, minsize=gap)
        resetPassword.grid(row=start+6, column=col, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+7, minsize=gap+2)
        #design of logout button. return to homepage after logout
        logOut = Button(ApplicationState.Root, text='LOG OUT', bg='white',  font=('',20,'bold'), command = ApplicationState.ShowHomePage)
        logOut.grid(row=start+8, column=14, columnspan=7, sticky=W+E)
        #list of widgets available after login
        ApplicationState.CurrentWidgets = [showCurrentlyIssued, showIssuedInPast, showMessages, resetPassword, logOut]

    def ShowCurrentlyIssuedBooks ( self ) :		#backend of displaying books currently issued by current user
    	#connect to database Accounts
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #search for books issued wrt issuer LMCN 
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM CurrentlyIssuedBooks WHERE IssuerLMCN=%s", (ApplicationState.CurrentUser._Individual__id,))
        results = cursorr.fetchall()
        
        #no books currently issued by user
        if ( len(results) == 0 ) :
            messagebox.showinfo("", "No currently issued books found!")
            db.close()
            return
        #unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #GUI for displaying list of books issued currently by logged in user
        gap = 20
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  CURRENTLY ISSUED BOOKS", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)

        initRow = 6

        height = 15
        #present list of issued books in tabular form
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
       	# frame design to display the issued books
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=34, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
         #scroll bar for navigating through the table
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #table design to show issued books
        table['columns'] = ('ISSUE ID', 'ISBN', 'TITLE', 'DATE OF ISSUE', 'DUE DATE', 'OVERDUE DAYS')
        table.column('#0', width=0, stretch=NO)
        table.column('ISSUE ID', width=120, minwidth=25)
        table.column('ISBN', width=180, minwidth=25)
        table.column('TITLE', width=350, minwidth=25)
        table.column('DATE OF ISSUE', width=170, minwidth=25)
        table.column('DUE DATE', width=170, minwidth=25)
        table.column('OVERDUE DAYS', width=170, minwidth=25)
        #table headings
        table.heading('#0', text='')
        table.heading('ISSUE ID', text='ISSUE ID', anchor=CENTER)
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('TITLE', text='TITLE', anchor=CENTER)
        table.heading('DATE OF ISSUE', text='DATE OF ISSUE', anchor=CENTER)
        table.heading('DUE DATE', text='DUE DATE', anchor=CENTER)
        table.heading('OVERDUE DAYS', text='OVERDUE DAYS', anchor=CENTER)
        #print issued books on table
        i = 0
        for rec in results :
            cursorr.execute("SELECT Title FROM Catalogue WHERE ISBN=%s", (rec[1],))
            title = cursorr.fetchall()[0][0]
            rd = datetime.strptime(rec[4], '%d/%m/%Y')
            overDays = (datetime.today()-rd).days
            if overDays < 0 :  overDays = 0
            table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], title, rec[3], rec[4], overDays))
            i += 1
        #close database
        db.close()

        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)
        #go back to user dashboard button
        ApplicationState.Root.grid_rowconfigure(17, minsize=35)
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Member.ShowFirstPage)
        goBack.grid(row=18, column=14, columnspan=7, sticky=W+E)
        #widget list 
        ApplicationState.CurrentWidgets = [head, treeFrame, table, goBack, scrollbar]

    def ShowBooksIssuedInPast ( self ) :		#displays all books past and presently issued by user
        #connect to database Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #use BooksIssuedInPast table in Library database
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM BooksIssuedInPast WHERE IssuerLMCN=%s", (ApplicationState.CurrentUser._Individual__id,))
        results = cursorr.fetchall()
        #find all books issued by user till date
        #if no books found then show pop up message
        if ( len(results) == 0 ) :
            messagebox.showinfo("", "No books were issued in the past!")
            db.close()
            return
        #unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design of background and heading of GUI page
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  BOOKS ISSUED IN PAST", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=34)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)

        initRow = 6
        height = 15
        #setting the font and style
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        #creating frame for displaying books issued till date
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=34, rowspan=5, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #scroll bar feaure to navigate through the table of books
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #construct columns of table to display books  issued
        table['columns'] = ('ISSUE ID', 'ISBN', 'TITLE', 'DATE OF ISSUE', 'DATE OF RETURN', 'OVERDUE DAYS', 'PENALTY', 'FINE PAID')
        table.column('#0', width=0, stretch=NO)
        table.column('ISSUE ID', width=90, minwidth=25)
        table.column('ISBN', width=155, minwidth=25)
        table.column('TITLE', width=330, minwidth=25)
        table.column('DATE OF ISSUE', width=170, minwidth=25)
        table.column('DATE OF RETURN', width=170, minwidth=25)
        table.column('OVERDUE DAYS', width=170, minwidth=25)
        table.column('PENALTY', width=100, minwidth=25)
        table.column('FINE PAID', width=110, minwidth=25)
        #insert table headings
        table.heading('#0', text='')
        table.heading('ISSUE ID', text='ISSUE ID', anchor=CENTER)
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('TITLE', text='TITLE', anchor=CENTER)
        table.heading('DATE OF ISSUE', text='DATE OF ISSUE', anchor=CENTER)
        table.heading('DATE OF RETURN', text='DATE OF RETURN', anchor=CENTER)
        table.heading('OVERDUE DAYS', text='OVERDUE DAYS', anchor=CENTER)
        table.heading('PENALTY', text='PENALTY', anchor=CENTER)
        table.heading('FINE PAID', text='FINE PAID', anchor=CENTER)
        #enter the book details in the table if it had been issued by user
        i = 1
        for rec in results :
            cursorr.execute("SELECT Title FROM Catalogue WHERE ISBN=%s", (rec[1],))
            title = cursorr.fetchall()[0][0]
            last = 'NO'
            if ( rec[7] == 1 ) :    last = 'YES'
            table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], title, rec[3], rec[4], rec[5], rec[6], last))
            i += 1
        #close database
        db.close()
        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S) 

        ApplicationState.Root.grid_rowconfigure(17, minsize=35)
        #go back button to return to user dashboard
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Member.ShowFirstPage)
        goBack.grid(row=15, column=14, columnspan=7, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [head, treeFrame, table, goBack, scrollbar]

    def ShowMessages ( self ) :			#GUI frame template for notifications/reminders to the user 
        #connect to database Accounts
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #connect to database Library
        libDb = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #find all books issued by user whose due dates are 4 days away
        libCursor = libDb.cursor(buffered=True)
        libCursor.execute("SELECT * FROM CurrentlyIssuedBooks WHERE IssuerLMCN=%s AND STR_TO_DATE(DateOfReturn, '%d/%m/%Y') <= DATE_ADD(STR_TO_DATE(%s, '%d/%m/%Y'), INTERVAL 4 DAY) AND STR_TO_DATE(DateOfReturn, '%d/%m/%Y') >= STR_TO_DATE(%s, '%d/%m/%Y')", 
                            (ApplicationState.CurrentUser._Individual__id, datetime.today().strftime("%d/%m/%Y"),datetime.today().strftime("%d/%m/%Y")))
        approachingReturns = libCursor.fetchall()
        #find all books by user which are overdue
        libCursor.execute("SELECT * FROM CurrentlyIssuedBooks WHERE IssuerLMCN=%s AND STR_TO_DATE(DateOfReturn, '%d/%m/%Y') < STR_TO_DATE(%s, '%d/%m/%Y')", 
                            (ApplicationState.CurrentUser._Individual__id, datetime.today().strftime("%d/%m/%Y")) )
        pendingReturns = libCursor.fetchall()
        #find all books that user had reserved and now are available for issuing for 7 days
        libCursor.execute( "SELECT * FROM ReservedBooks WHERE ReserverLMCN=%s AND IsReturned=1", 
                            (ApplicationState.CurrentUser._Individual__id, ) )
        waitingReserved = libCursor.fetchall()
        #find all books issued by user with pending fines
        libCursor.execute( "SELECT * FROM BooksIssuedInPast WHERE IssuerLMCN=%s AND FinePaid=0", 
                            (ApplicationState.CurrentUser._Individual__id, ) )
        pendingFines = libCursor.fetchall()
        #close database library
        libDb.close()
        #find all previous messages to user 
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM Messages WHERE LMCN=%s", (ApplicationState.CurrentUser._Individual__id,))
        notifs = cursorr.fetchall()[::-1]
        db.close()
        #case of not notificaions/reminders
        if ( not len(notifs) and not len(approachingReturns) and not len(pendingReturns) and not len(waitingReserved) and not len(pendingFines) ) :
            messagebox.showinfo("", "There are no notifications or reminders!")
            return
        #unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        gap = 5
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  NOTIFICATIONS / REMINDERS", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=0, columnspan=34)
        
        ApplicationState.Root.grid_rowconfigure(5, minsize=5)

        msgHeight = 15
        #desin and placement of scroll bar to navigate
        frame = Frame(ApplicationState.Root, height = msgHeight )
        scrollbar = Scrollbar( frame , orient = VERTICAL )
        messages = Listbox( frame , width = 47 , yscrollcommand = scrollbar.set, font=('',16,'bold'), activestyle='none', height=msgHeight, 
                            selectbackground=ApplicationDesign.Theme, selectforeground="white", selectmode=SINGLE, highlightcolor=ApplicationDesign.Theme)

        start = 6
        #send new notifications-
        for rec in approachingReturns :
            messages.insert(END, "[REM] Return date of the issued book is approaching" )
        for rec in pendingReturns :
            messages.insert(END, "[REM] Return of the issued book is pending" )
        for rec in waitingReserved :
            messages.insert(END, "[REM] Reserved book is waiting" )
        for rec in pendingFines :
            messages.insert(END, "[REM] Fine payment is pending" )
        #display  previous notifications
        for rec in notifs :
            messages.insert(END, "[" + rec[4] + "] [" + rec[5] + "] " + rec[2] )

        scrollbar.config(command=messages.yview)
        scrollbar.grid(row=start, column=14, rowspan=msgHeight, sticky=N+S+W)
        
        frame.grid(row=start, column=1, columnspan=13, rowspan=msgHeight, sticky=N)
        #dynamic switching between messages implemented through bind
        messages.grid(row=start, column=1, columnspan=13, padx=5, pady=5, sticky=N)
        messages.bind('<Double-1>', lambda x : self.DisplayMessage(approachingReturns, pendingReturns, waitingReserved, pendingFines, notifs) )
        #text box to display message
        display = Text( ApplicationState.Root, bg='white', width=70, height=10, font=('Helvetica',16,''), wrap=WORD, padx=4, pady=4 )
        display.insert(END, " YOUR MESSAGE WILL BE DISPLAYED HERE...") 
        display.config(state=DISABLED)
        #placement of display textbox
        display.grid(row=start, column=14, columnspan=5, rowspan=10, sticky=N+S)
        #design and placement of go back button to return to user dashboard
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Member.ShowFirstPage)
        ApplicationState.Root.grid_rowconfigure(16, minsize=20)
        goBack.grid(row=17, column=11, columnspan=5, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [head, frame, messages, scrollbar, display, goBack]
        
    def DisplayMessage(self, approachingReturns, pendingReturns, waitingReserved, pendingFines, notifs) :	#print all messages on display message frame
        idx = ApplicationState.CurrentWidgets[2].curselection()[0]
        
        ApplicationState.CurrentWidgets[-2].config(state=NORMAL)
        ApplicationState.CurrentWidgets[-2].delete(1.0, END)
        #connect to database Accounts
        libDb = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        cursorr = libDb.cursor(buffered=True)

        if ( idx < len(approachingReturns) ) :	#message for approaching due dates
            details = approachingReturns[idx]
            cursorr.execute("SELECT Title FROM Catalogue WHERE ISBN=%s", (details[1], ))	#fetch all books with approaching due dates
            title = cursorr.fetchall()
            msg = """\nDear Member,\nWe have seen that you have not yet returned a book that you issued from the library. The due return date of the issued book is approaching and we request you to return it at the earliest so that other members can also access the book. The details regarding the issued book are as follows.\n\n\tISSUE ID        : {}\n\tISBN            : {}\n\tTITLE           : {}\n\tDATE OF ISSUE   : {}\n\tDATE OF RETURN  : {}\n\nThank you.\nRegards.\nLIS.
                  """.format(details[0], details[1], title, details[3], details[4])
            ApplicationState.CurrentWidgets[-2].insert(END, msg )
        
        elif ( idx - len(approachingReturns) < len(pendingReturns) ) :	#message for over due books
            details = pendingReturns[idx - len(approachingReturns)]
            cursorr.execute("SELECT Title FROM Catalogue WHERE ISBN=%s", (details[1], ))
            title = cursorr.fetchall()
            overDays = (datetime.today() - datetime.strptime(details[4], '%d/%m/%Y')).days 	#calculate no of days the book is overdue
            penalty = ApplicationDesign.Penalty * overDays 	#calculate penalty
            msg = """\nDear Member,\nWe have seen that you have not yet returned a book that you issued from the library. The due return date of the issued book has already crossed and we request you to return it at the earliest so that other members can also access the book. The details regarding the issued book are as follows.\n\n\tISSUE ID            : {}\n\tISBN                : {}\n\tTITLE               : {}\n\tDATE OF ISSUE       : {}\n\tDUE DATE OF RETURN  : {}\n\tOVERDUE DAYS        : {}\n\tPENALTY             : Rs. {}\n\nThank you.\nRegards.\nLIS.
                  """.format(details[0], details[1], title, details[3], details[4], overDays, penalty)
            ApplicationState.CurrentWidgets[-2].insert(END, msg )
        
        elif ( idx - len(approachingReturns) - len(pendingReturns) < len(waitingReserved) ) :	#books with reservations which are now available
            details = waitingReserved[idx - len(approachingReturns) - len(pendingReturns)]
            msg = """\nDear Member,\nWe have seen that you have not yet formally issued a book that you reserved from the library. The reserved book has been returned by the former issuer and the book is waiting for you to be collected. Please do that at the earliest, before the reservation gets expired.\n\n\tRESERVATION ID          : {}\n\tDATE OF RESERVATION     : {}\n\tDATE OF RETURN          : {}\n\nThank you.\nRegards.\nLIS.
                  """.format(details[0], details[4], details[6])
            ApplicationState.CurrentWidgets[-2].insert(END, msg )
        
        elif ( idx - len(approachingReturns) - len(pendingReturns) - len(waitingReserved) < len(pendingFines) ) :	#message for penalty payment
            details = pendingFines[idx - len(approachingReturns) - len(pendingReturns) - len(waitingReserved)]
            msg = """\nDear Member,\nWe have seen that you have not yet paid the fine for the book that you returned to the library. Please do that at the earliest so that you are not disbarred from issuing books from the library.\n\n\tISSUE ID         : {}\n\tISBN             : {}\n\tDATE OF ISSUE    : {}\n\tDATE OF RETURN   : {}\n\tOVERDUE DAYS     : {}\n\tPENALTY          : Rs. {}\n\nThank you.\nRegards.\nLIS.
                  """.format(details[0], details[1], details[3], details[4], details[5], details[6])
            ApplicationState.CurrentWidgets[-2].insert(END, msg )

        elif ( idx - len(approachingReturns) - len(pendingReturns) - len(waitingReserved) - len(pendingFines) < len(notifs) ) :		#load previous messages
            msg = notifs[idx - len(approachingReturns) - len(pendingReturns) - len(waitingReserved) - len(pendingFines)]
            ApplicationState.CurrentWidgets[-2].insert(END, msg[4] + "  " + msg[5] + "\n\n" + Fernet(ApplicationDesign.MessagesFernetKey).decrypt(msg[3].encode()).decode() )
        #close database Library
        libDb.close()
        ApplicationState.CurrentWidgets[-2].config(state=DISABLED)
    
        

class NonFaculty ( Member ) :	#NonFaculty is specializaion of Member class
    
    def __init__ ( self , idd , rollNo , name , dob , regDate , issueCount ) :
        self.__rollNo = rollNo 		#set roll number for nonfaculty(student)
        Member.__init__( self , idd , name , dob , regDate , issueCount )
    
    def ChangePassword ( self ) :	#backend of changing password-
        if ( ApplicationState.OldPasswordField.get() == "" ) :
            messagebox.showerror("", "Old password not specified !")
            return
        if ( ApplicationState.NewPasswordField.get() == "" ) :
            messagebox.showerror("", "New password not specified !")
            return
        if ( ApplicationState.ConfirmPasswordField.get() == "" ) :
            messagebox.showerror("", "Confirmation password not specified !")
            return
        
        #connect to database Accounts-
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
         #select user with matching LMCN form the table NonfacultyMembers form database Accounts
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentUser._Individual__id,))
        pw = cursorr.fetchall()[0][6]

        #old password required to change new password
        if ( md5(ApplicationState.OldPasswordField.get().encode()).hexdigest() != pw ) :
            messagebox.showerror('ERROR', 'Incorrect Old Password !')
            db.close()
            return
        #new password cant have only whitespaces
        if ( ApplicationState.NewPasswordField.get().strip() == "" ) :
            messagebox.showerror('ERROR', 'New password has no characters !')
            db.close()
            return
        #password cant be too short
        if ( len(ApplicationState.NewPasswordField.get()) < 7 ) :
            messagebox.showerror('ERROR', 'Password must be atleast 7 characters long')
            db.close()
            return

        #error if new password and confirm password do not match
        if ( ApplicationState.NewPasswordField.get() != ApplicationState.ConfirmPasswordField.get() ) :
            messagebox.showerror('ERROR', 'Incorrect "New" and "Confirm" Passwords do not match !')
            db.close()
            return
        #save the new password in md5 encryption 
        sql = "UPDATE NonFacultyMembers SET password = md5(%s) WHERE LMCN = %s"
        cursorr.execute(sql, (ApplicationState.NewPasswordField.get(), ApplicationState.CurrentUser._Individual__id))
        #update and close database
        db.commit()
        db.close()
        ApplicationState.OldPasswordField.set("")
        ApplicationState.NewPasswordField.set("")
        ApplicationState.ConfirmPasswordField.set("")
        Member.ShowFirstPage()


class Faculty ( Member ) :		#Faculty is specializaion of Member class
    
    def __init__ ( self , idd , dep , name , dob , regDate , issueCount ) :
        super().__init__( idd , name , dob , regDate , issueCount )
        self.__department = dep	#set department for faculty
        self.__status = 'FAC'
    
    def ChangePassword ( self ) :	#backend of changing password-
        if ( ApplicationState.OldPasswordField.get() == "" ) :
            messagebox.showerror("", "Old password not specified!")
            return
        if ( ApplicationState.NewPasswordField.get() == "" ) :
            messagebox.showerror("", "New password not specified!")
            return
        if ( ApplicationState.ConfirmPasswordField.get() == "" ) :
            messagebox.showerror("", "Confirmation password not specified!")
            return

        #connect to database Accounts-
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #select user with matching LMCN form the table facultyMembers form database Accounts
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentUser._Individual__id,))
        pw = cursorr.fetchall()[0][5]

        #old password required to change new password
        if ( md5(ApplicationState.OldPasswordField.get().encode()).hexdigest() != pw ) :
            messagebox.showerror('ERROR', 'Incorrect Old Password !')
            db.close()
            return
        
        if ( ApplicationState.NewPasswordField.get().strip() == "" ) :
            messagebox.showerror('ERROR', 'New password has no characters !')
            db.close()
            return
        
        if ( len(ApplicationState.NewPasswordField.get()) < 7 ) :
            messagebox.showerror('ERROR', 'Password must be atleast 7 characters long')
            db.close()
            return

        #error if new password and confirm password do not match
        if ( ApplicationState.NewPasswordField.get() != ApplicationState.ConfirmPasswordField.get() ) :
            messagebox.showerror('ERROR', 'Incorrect "New" and "Confirm" Passwords do not match !')
            db.close()
            return
        #save the new password in md5 encryption 
        sql = "UPDATE FacultyMembers SET password = md5(%s) WHERE LMCN = %s"
        cursorr.execute(sql, (ApplicationState.NewPasswordField.get(), ApplicationState.CurrentUser._Individual__id))
        #update and close database
        db.commit()
        db.close()
        ApplicationState.OldPasswordField.set("")
        ApplicationState.NewPasswordField.set("")
        ApplicationState.ConfirmPasswordField.set("")
        Member.ShowFirstPage()


class UnderGraduate ( NonFaculty ) :		#UnderGraduate is specialization of NonFaculty class
    
    def __init__ ( self , idd , rollNo , name , dob , regDate , issueCount ) :
        self.__status = 'UG'
        NonFaculty.__init__( self , idd , rollNo , name , dob , regDate , issueCount )


class PostGraduate ( NonFaculty ) :			#PostGraduate is specialization of NonFaculty class
    
    def __init__ ( self , idd , rollNo , name , dob , regDate , issueCount ) :
        self.__status = 'PG'
        NonFaculty.__init__( self , idd , rollNo , name , dob , regDate , issueCount )


class ResearchScholar ( NonFaculty ) :		#ResearchScholar is specialization of NonFaculty class
    
    def __init__ ( self , idd , rollNo , name , dob , regDate , issueCount ) :
        self.__status = 'RS'
        NonFaculty.__init__( self , idd , rollNo , name , dob , regDate , issueCount )


class Clerk ( Individual ) :	#class Clerk is specialization of Individual 

    def __init__ ( self , idd , name , dob , regDate ) :		#constructor
        self.__status = 'CL'
        Individual.__init__( self, idd, name, dob, regDate )

    @staticmethod
    def IsValidClerk ( loginId , password ) :		#check credentials of a clerk trying to log in
        if ( loginId[:2] != 'CL' ) :		#check if the account is of type clerk
            messagebox.showerror('ERROR', 'Incorrect LOGIN ID entered !')
            return
        #connect to database Accounts
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #open table Adminstrators from datbase Accounts
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM Administrators WHERE ID=%s", (loginId,))
        results = cursorr.fetchall()
        db.close()
        #validate login id here-
        if ( not len(results) ) :
            messagebox.showerror('ERROR', 'Incorrect LOGIN ID entered !')
            return
        #validate password here
        if ( results[0][4] != md5(password.encode()).hexdigest() ) :
            messagebox.showerror('ERROR', 'Incorrect password entered !')
            return
        #if login and password are matching then go to user dashboard
        ApplicationState.CurrentUser = Clerk(loginId, results[0][1], results[0][2], results[0][3])
        Clerk.ShowFirstPage()	#enter user dashboard
        
    @staticmethod
    def ShowFirstPage ( ) :		#GUI design of clerk dashboard
    	#unmap all previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #create buttons for variuous features
        issue = Button(ApplicationState.Root, text='ISSUE BOOK FROM RACK', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.IssueBook)
        issueRes = Button(ApplicationState.Root, text='ISSUE RESERVED BOOK', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.IssueReservedBook)
        returnb = Button(ApplicationState.Root, text='RETURN ISSUED BOOK', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ReturnBook)
        reserve = Button(ApplicationState.Root, text='RESERVE ISSUED BOOK', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ReserveBook)
        add = Button(ApplicationState.Root, text='ADD NEW BOOK', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.AddNewBook)
        remove = Button(ApplicationState.Root, text='REMOVE EXISTING BOOK', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.RemoveExistingBook)
        pay = Button(ApplicationState.Root, text='PAY PENALTY', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.PayFine)
        resetPw = Button(ApplicationState.Root, text='RESET PASSWORD', bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ResetPassword)
        
        span = 12
        start = 4
        gap = 35
        shift = 2

        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        #placement of  buttons below
        issue.grid(row=start, column=2+shift, columnspan=span, sticky=W+E)
        issueRes.grid(row=start, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+1, minsize=gap)

        returnb.grid(row=start+2, column=2+shift, columnspan=span, sticky=W+E)
        reserve.grid(row=start+2, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+3, minsize=gap)
        
        add.grid(row=start+4, column=2+shift, columnspan=span, sticky=W+E)
        remove.grid(row=start+4, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+5, minsize=gap)
        
        pay.grid(row=start+6, column=2+shift, columnspan=span, sticky=W+E)
        resetPw.grid(row=start+6, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+7, minsize=gap)
        #logout and return to application homepage
        logOut = Button(ApplicationState.Root, text='LOG OUT', bg='white',  font=('',20,'bold'), command = ApplicationState.ShowHomePage)
        logOut.grid(row=start+10, column=14, columnspan=7, sticky=W+E)
        #list of widgets
        ApplicationState.CurrentWidgets = [issue, issueRes, returnb, reserve, add, remove, pay, resetPw, logOut]

    @staticmethod
    def NotifyMember ( subject , message , lmcm ) :	#send notification to a member of the library
        #connect to database Accounts
        accountsDb = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        accCursor = accountsDb.cursor(buffered=True)
        #insert notification into Message table in Accounts Database
        sql = "INSERT INTO Messages(LMCN, Subject, Message, Date, Time) VALUES (%s, %s, %s, %s, %s)"
        #store message in encrypted format
        val = (lmcm, subject, Fernet(ApplicationDesign.MessagesFernetKey).encrypt(message.encode()).decode(), 
                datetime.today().strftime("%d/%m/%Y"), datetime.today().strftime("%H%M"))
        accCursor.execute(sql, val)
        #update and close database 
        accountsDb.commit()
        accountsDb.close()

    def IssueBook ( self ) :		#issue book
    	#unmap previous widget 
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design of heading
        head = Label(ApplicationState.Root, text="  □  ISSUE A BOOK FROM RACK", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        #design of label
        askLmcn = Label(ApplicationState.Root, text="ISSUER'S LMCN  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        lmcn = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of label
        askIsbn = Label(ApplicationState.Root, text="ISBN  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        isbn = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #buttton to issue/goback/reserve
        issue = Button(ApplicationState.Root, text="ISSUE BOOK", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.AddIssuedBookToDatabase)
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Clerk.ShowFirstPage)
        issueRes = Button(ApplicationState.Root, text="ISSUE RESERVED BOOK", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.IssueReservedBook)
        
        span1 = 7
        span2 = 17
        gap = 25
        #placement of labels
        ApplicationState.Root.grid_rowconfigure(5, minsize=gap)
        askLmcn.grid(row=6, column=3, columnspan=span1, sticky=W+E)
        lmcn.grid(row=6, column=13, columnspan=span2, sticky=W+E)
        #placement of labels
        ApplicationState.Root.grid_rowconfigure(7, minsize=gap)
        askIsbn.grid(row=8, column=3, columnspan=span1, sticky=W+E)
        isbn.grid(row=8, column=13, columnspan=span2, sticky=W+E)
        #placement of buttons
        ApplicationState.Root.grid_rowconfigure(9, minsize=gap+15)
        goBack.grid(row=10, column=4, columnspan=8, sticky=W+E)
        issue.grid(row=10, column=13, columnspan=8, sticky=W+E)
        issueRes.grid(row=10, column=22, columnspan=8, sticky=W+E)
        #list of widgets
        ApplicationState.CurrentWidgets = [ head , askLmcn, lmcn , askIsbn , isbn , issue , goBack , issueRes ]

    def AddIssuedBookToDatabase ( self ) :		#update database to reflect a book issue 
        #validate LMCN
        if ( len(ApplicationState.CurrentWidgets[2].get().strip()) == 0 ) :
            messagebox.showerror("", "LMCN of the issuer not specified!")
            return
        #validate ISBN
        if ( len(ApplicationState.CurrentWidgets[4].get().strip()) == 0 ) :
            messagebox.showerror("", "ISBN of the book not specified!")
            return
        #connect to database 
        accountsDb = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        accCursor = accountsDb.cursor(buffered=True)
        #find faculty with specified LMCN
        accCursor.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get(),))
        r = accCursor.fetchall()
        check1 = not len(r)

        issuer = None
        
        if check1 :		#if user was not faculty member
            accCursor.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get(),))
            r = accCursor.fetchall()
            check2 = not len(r)
            if check2 :		#LMCN is  incorrect
                messagebox.showerror("", "Specified LMCN not found in the accounts of LIS!")
                accountsDb.close()
                return
            else :
                issuer = r[0]
        else :
            issuer = r[0]
        #connect database Library
        libraryDb = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        libCursor = libraryDb.cursor(buffered=True)
        #find book form catalogue using ISBN
        libCursor.execute("SELECT * FROM Catalogue WHERE ISBN=%s", (ApplicationState.CurrentWidgets[4].get(),))
        results = libCursor.fetchall()
        if ( not len(results) ) :	#verify ISBN 
            messagebox.showerror("", "No book with the specified ISBN was found!")
            libraryDb.close()
            accountsDb.close()
            return
        
        if ( not results[0][6] ) :		#no need for reservation if book is available
            messagebox.showerror("", "No copy in the rack right now!\nYou can reserve an already issued book.")
            libraryDb.close()
            accountsDb.close()
            return
        
        allowedCount = None
        allowedDays = None
        #eligibilty of issueing book depends on user
        if ( issuer[0][:2] == "UG" ) :
            allowedCount = 2
            allowedDays = 30
        elif ( issuer[0][:2] == "PG" ) :
            allowedCount = 4
            allowedDays = 30
        elif ( issuer[0][:2] == "RS" ) :
            allowedCount = 6
            allowedDays = 90
        elif ( issuer[0][:2] == "FC" ) :
            allowedCount = 10
            allowedDays = 180
        
        if ( issuer[0][:2] != "FC" and issuer[5] == allowedCount ) :		#cannot issue books more than limit set by Library
            messagebox.showerror("", "Member has already reached the issue limit!")
            libraryDb.close()
            accountsDb.close()
            return
        
        elif ( issuer[4] == allowedCount ) :	#cannot issue books more than limit set by Library
            messagebox.showerror("", "Member has already reached the issue limit!")
            libraryDb.close()
            accountsDb.close()
            return
        #set date of issue and return
        dateOfIssue = datetime.today().strftime("%d/%m/%Y")
        dateOfReturn = (datetime.today()+timedelta(allowedDays)).strftime("%d/%m/%Y")
        #create encrypted issue id 
        issueId = md5(str(uuid4()).encode()).hexdigest().upper()[:7]

        while True :		#keep crerating issue id till unique one generated
            libCursor.execute("SELECT * FROM CurrentlyIssuedBooks WHERE IssueId=%s", (issueId,))
            result = libCursor.fetchall()
            libCursor.execute("SELECT * FROM BooksIssuedInPast WHERE IssueId=%s", (issueId,))
            result_ = libCursor.fetchall()
            if ( not len(result) and not len(result_) ) :   break
            issueId = md5(str(uuid4()).encode()).hexdigest().upper()[:7]
        
        #add issue details in CurrentlyissuedBooks table
        sql = "INSERT INTO CurrentlyIssuedBooks VALUES (%s, %s, %s, %s, %s, 0)"
        val = (issueId, ApplicationState.CurrentWidgets[4].get(), ApplicationState.CurrentWidgets[2].get(), dateOfIssue, dateOfReturn)
        libCursor.execute(sql, val)
        libraryDb.commit()
        #update catalogue to reflect that no of available copies has reduced
        sql = "UPDATE Catalogue SET Available=Available-1 , LastIssueDate=%s  WHERE ISBN = %s"
        val = (dateOfIssue, ApplicationState.CurrentWidgets[4].get())
        libCursor.execute(sql, val)
        libraryDb.commit()
        #notify the member of successful issue
        msg = """Dear Member,\nThe following book has been succesfully issued. Please return the book before the due date.\n\n\tISSUE ID        :   {}\n\tISBN            :   {}\n\tTITLE           :   {}\n\tAUTHOR          :   {}\n\tDATE OF RETURN  :   {}\n\nThank you.\nRegards.\nLIS.
              """.format(issueId, results[0][0], results[0][1], results[0][2], dateOfReturn)

        Clerk.NotifyMember("BOOK ISSUED SUCCESSFULLY", msg, ApplicationState.CurrentWidgets[2].get())

        if ( issuer[0][:2] != "FC" ) :	#increment the count of currently issued by user 
            sql = "UPDATE NonFacultyMembers SET IssueCount=IssueCount+1 WHERE LMCN = %s"
            val = (ApplicationState.CurrentWidgets[2].get(), )
            accCursor.execute(sql, val)
            accountsDb.commit()
        else :
            sql = "UPDATE FacultyMembers SET IssueCount=IssueCount+1 WHERE LMCN = %s"
            val = (ApplicationState.CurrentWidgets[2].get(), )
            accCursor.execute(sql, val)
            accountsDb.commit()

        libraryDb.close()
        accountsDb.close()
        ApplicationState.CurrentWidgets[2].delete(0, END)
        ApplicationState.CurrentWidgets[4].delete(0, END)
        #pop up message to show book has been issued successfully
        messagebox.showinfo("", "Book is successfully issued.\nMember will be able to see the necessary details in his/her account.")
        
    def IssueReservedBook ( self ) :		#GUI for issuing reserved book
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and positioning of heading
        head = Label(ApplicationState.Root, text="  □  ISSUE A RESERVED BOOK", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        #design of label and entry box for reservation id
        askId = Label(ApplicationState.Root, text="RESERVATION ID  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        idd = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of label and entry box for reservation key
        askKey = Label(ApplicationState.Root, text="RESERVATION KEY  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        key = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #buttons to confirm issue or go back
        issue = Button(ApplicationState.Root, text="ISSUE BOOK", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.AddResIssuedBookToDatabase)
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Clerk.ShowFirstPage)
        issueRack = Button(ApplicationState.Root, text="ISSUE BOOK FROM RACK", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.IssueBook)
        
        span1 = 7
        span2 = 17
        gap = 25
        #position reservation id widgets
        ApplicationState.Root.grid_rowconfigure(5, minsize=gap)
        askId.grid(row=6, column=3, columnspan=span1, sticky=W+E)
        idd.grid(row=6, column=13, columnspan=span2, sticky=W+E)
        #position reservation key widgets
        ApplicationState.Root.grid_rowconfigure(7, minsize=gap)
        askKey.grid(row=8, column=3, columnspan=span1, sticky=W+E)
        key.grid(row=8, column=13, columnspan=span2, sticky=W+E)
        #posiion buttons
        ApplicationState.Root.grid_rowconfigure(9, minsize=gap+15)
        goBack.grid(row=10, column=4, columnspan=8, sticky=W+E)
        issue.grid(row=10, column=13, columnspan=8, sticky=W+E)
        issueRack.grid(row=10, column=22, columnspan=8, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [ head ,askId, idd , askKey , key , issue , goBack , issueRack ]
    
    def AddResIssuedBookToDatabase ( self ) :		#backend of issueing a reserved book
    	#verify reservation id
        if ( len(ApplicationState.CurrentWidgets[2].get().strip()) == 0 ) :
            messagebox.showerror("", "Reservation ID not specified!")
            return
        #verify reservation key
        if ( len(ApplicationState.CurrentWidgets[4].get().strip()) == 0 ) :
            messagebox.showerror("", "Reservation Key not specified!")
            return
        #connect to database Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )

        cursorr = db.cursor(buffered=True)


        #find book to be reserved in the ReservedBooks table using reserve id
        cursorr.execute("SELECT * FROM ReservedBooks WHERE ReserveID=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
        if ( len(cursorr.fetchall()) == 0 ) :		#reservation id does not match 
            messagebox.showerror("", "Reservation ID not found!")
            db.close()
            return
        #find book with same reserved id and key
        cursorr.execute( "SELECT * FROM ReservedBooks WHERE ReserveID=%s AND ReservationKey=%s", 
                          ( ApplicationState.CurrentWidgets[2].get().strip(), 
                            md5(ApplicationState.CurrentWidgets[4].get().strip().encode()).hexdigest() ) )
        if ( len(cursorr.fetchall()) == 0 ) :		#verify reservation key
            messagebox.showerror("", "Reservation Key did not match!")
            db.close()
            return
        
        cursorr.execute( "SELECT * FROM ReservedBooks WHERE ReserveID=%s AND IsReturned=1", 
                          ( ApplicationState.CurrentWidgets[2].get().strip(), ) )
        if ( len(cursorr.fetchall()) == 0 ) :		#check if Reserved book is available after previous issuer returned it
            messagebox.showerror("", "Reserved book is not yet returned!")
            db.close()
            return

        cursorr.execute("SELECT * FROM ReservedBooks WHERE ReserveID=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
        reserver = cursorr.fetchall()[0]
        
        allowedCount = None
        allowedDays = None
        #set allowed book count and allowed days according to user type
        if ( reserver[3][:2] == "UG" ) :
            allowedCount = 2
            allowedDays = 30
        elif ( reserver[3][:2] == "PG" ) :
            allowedCount = 4
            allowedDays = 30
        elif ( reserver[3][:2] == "RS" ) :
            allowedCount = 6
            allowedDays = 90
        elif ( reserver[3][:2] == "FC" ) :
            allowedCount = 10
            allowedDays = 180
        #connect to databse Accounts
        dbAcc = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )

        cursorAcc = dbAcc.cursor(buffered=True)

        recordRes = None

        if ( reserver[3][:2] == "FC" ) :	#check if user is facultyMembers
            cursorAcc.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s", (reserver[3],))
            recordRes = cursorAcc.fetchall()[0]
            if ( recordRes[4] == allowedCount ) :	#check if faculty member has not already exhausted issue limit
                messagebox.showerror("", "Member has already reached the issue limit!")
                dbAcc.close()
                db.close()
                return
        else :	#check if user is NONfacultyMembers
            cursorAcc.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s", (reserver[3],))
            recordRes = cursorAcc.fetchall()[0]
            if ( recordRes[5] == allowedCount ) : 	#check if non faculty member has not already exhausted issue limit
                messagebox.showerror("", "Member has already reached the issue limit!")
                dbAcc.close()
                db.close()
                return
        
        cursorr.execute( "SELECT * FROM BooksIssuedInPast WHERE IssueID=%s", (reserver[2], ) )
        isbn = cursorr.fetchall()[0][1]
        #import book details
        cursorr.execute( "SELECT * FROM Catalogue WHERE ISBN=%s", (isbn, ) )
        bookDetails = cursorr.fetchall()[0]

        #set date of issue and return

        dateOfIssue = datetime.today().strftime("%d/%m/%Y")
        dateOfReturn = (datetime.today()+timedelta(allowedDays)).strftime("%d/%m/%Y")
        #create issue id in encrypted format
        issueId = md5(str(uuid4()).encode()).hexdigest().upper()[:7]

        while True :	#check if same issue id has not been previously generated
            cursorr.execute("SELECT * FROM CurrentlyIssuedBooks WHERE IssueId=%s", (issueId,))
            result = cursorr.fetchall()
            cursorr.execute("SELECT * FROM BooksIssuedInPast WHERE IssueId=%s", (issueId,))
            result_ = cursorr.fetchall()
            if ( not len(result) and not len(result_) ) :   break
            issueId = md5(str(uuid4()).encode()).hexdigest().upper()[:7]	#issue id in encrypted format
        
        #insert issued book details in CurrentlyissuedBooks tables
        sql = "INSERT INTO CurrentlyIssuedBooks VALUES (%s, %s, %s, %s, %s, 0)"
        val = (issueId, isbn, reserver[3], dateOfIssue, dateOfReturn)
        cursorr.execute(sql, val)
        db.commit()

       	#send message of succesful issue to reserver
        msg = """Dear Member,\nThe following book has been succesfully issued. Please return the book before the due date.\n\n\tISSUE ID        :   {}\n\tISBN            :   {}\n\tTITLE           :   {}\n\tAUTHOR          :   {}\n\tDATE OF RETURN  :   {}\n\nThank you.\nRegards.\nLIS.
              """.format(issueId, isbn, bookDetails[1], bookDetails[2], dateOfReturn)

        Clerk.NotifyMember("BOOK ISSUED SUCCESSFULLY", msg, reserver[3])
        #increase the count of books issued for user -
        if ( reserver[3][:2] != "FC" ) :	
            sql = "UPDATE NonFacultyMembers SET IssueCount=IssueCount+1 WHERE LMCN = %s"
            val = (reserver[3], )
            cursorAcc.execute(sql, val)
            dbAcc.commit()
        else :		
            sql = "UPDATE FacultyMembers SET IssueCount=IssueCount+1 WHERE LMCN = %s"
            val = (reserver[3], )
            cursorAcc.execute(sql, val)
            dbAcc.commit()
        #delete the request for reservation as issue was successful
        cursorr.execute("DELETE FROM ReservedBooks WHERE ReserveId = %s", (ApplicationState.CurrentWidgets[2].get().strip(),))
        db.commit()
        db.close()
        dbAcc.close()
        ApplicationState.CurrentWidgets[2].delete(0, END)
        ApplicationState.CurrentWidgets[4].delete(0, END)
        #pop up message for clerk of successful issue
        messagebox.showinfo("", "Book is successfully issued.\nMember will be able to see the necessary details in his/her account.")

    def ReserveBook ( self ) :		#GUI to reserve book
    	#unmap all previous widgets-
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        head = Label(ApplicationState.Root, text="  □  RESERVE AN ISSUED BOOK", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        #design of label and entry box for LMCN
        askLmcn = Label(ApplicationState.Root, text="RESERVER'S LMCN  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        lmcn = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of label and entry box for ISBN
        askIsbn = Label(ApplicationState.Root, text="ISBN  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        isbn = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design buttons
        reserve = Button(ApplicationState.Root, text="RESERVE BOOK", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.AddReservedBookToDatabase)
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Clerk.ShowFirstPage)
        
        span1 = 7
        span2 = 17
        gap = 25
        #placement of LMCN widgets
        ApplicationState.Root.grid_rowconfigure(5, minsize=gap)
        askLmcn.grid(row=6, column=3, columnspan=span1, sticky=W+E)
        lmcn.grid(row=6, column=13, columnspan=span2, sticky=W+E)
        #placement of ISBN widgets
        ApplicationState.Root.grid_rowconfigure(7, minsize=gap)
        askIsbn.grid(row=8, column=3, columnspan=span1, sticky=W+E)
        isbn.grid(row=8, column=13, columnspan=span2, sticky=W+E)
        #placement of buttons
        ApplicationState.Root.grid_rowconfigure(9, minsize=gap+15)
        goBack.grid(row=10, column=5, columnspan=8, sticky=W+E)
        reserve.grid(row=10, column=20, columnspan=8, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [ head , askLmcn, lmcn , askIsbn , isbn , reserve , goBack ]

    def AddReservedBookToDatabase ( self ) :		#backend implementation to reserve a book
    	#check if LMCN has been entered
        if ( len(ApplicationState.CurrentWidgets[2].get().strip()) == 0 ) :
            messagebox.showerror("", "Reserver's LMCN not specified!")
            return
        #check if ISBN has been entered
        if ( len(ApplicationState.CurrentWidgets[4].get().strip()) == 0 ) :
            messagebox.showerror("", "ISBN of the book not specified!")
            return

        isbn = ApplicationState.CurrentWidgets[4].get().strip()
        lmcn = ApplicationState.CurrentWidgets[2].get().strip()
        #connect to database Accounts
        dbAcc = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        cursorAcc = dbAcc.cursor(buffered=True)

        if ( lmcn[:2] != "FC" ) :	#if reserver is NonFacultyMember
            cursorAcc.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s", (lmcn, ))
            if ( len(cursorAcc.fetchall()) == 0 ) :		#if LMCN of userdoes not match show error
                messagebox.showerror("", "Specifed LMCN not found!")
                dbAcc.close()
                return
        else :		#if reserver is facultyMembers
            cursorAcc.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s", (lmcn, ))
            if ( len(cursorAcc.fetchall()) == 0 ) :		#if LMCN of user does not match show error
                messagebox.showerror("", "Specifed LMCN not found!")
                dbAcc.close()
                return
        #connect to database Library
        dbLib = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        cursorLib = dbLib.cursor(buffered=True)
        #find book to be reserved in catalogue
        cursorLib.execute("SELECT * FROM Catalogue WHERE ISBN=%s", (isbn, ))
        if ( len(cursorLib.fetchall()) == 0 ) :		#check if ISBN is correct
            messagebox.showerror("", "Specifed ISBN not found!")
            dbAcc.close()
            dbLib.close()
            return

        cursorLib.execute("SELECT * FROM CurrentlyIssuedBooks WHERE ISBN=%s AND IsReserved=0", (isbn, ))
        relevant = cursorLib.fetchall()
        if ( len(relevant) == 0 ) :		#the book is already availalbe , no need to reserve
            messagebox.showerror("", "No issued books with the specified ISBN were found to be open for reservation!\nYou may try issuing the book from the rack.")
            dbAcc.close()
            dbLib.close()
            return
        #make reservation for the book
        issueId = relevant[0][0]
        cursorLib.execute("UPDATE CurrentlyIssuedBooks SET IsReserved=1 WHERE IssueID=%s", (issueId, ))
        dbLib.commit()
        #details of reservation-
        rID = str(uuid4())[:10] + issueId
        rKey = str(uuid4())[:13]
        dateOfRes = datetime.today().strftime("%d/%m/%Y")
        #make reservation and update database Library
        cursorLib.execute("INSERT INTO ReservedBooks VALUES(%s, md5(%s), %s, %s, %s, 0, 'NA')", (rID, rKey, issueId, lmcn, dateOfRes))
        dbLib.commit()
        #send message(notification) to user with confirmation of reservation
        msg = """Dear Member,\nThe following book has been succesfully reserved. Please collect the book within 7 days of the return.Reservation will get cancelled if the book is not formally issued in 7 days after the book is returned.\n\n\tRESERVATION ID    :   {}\n\tRESERVATION KEY   :   {}\n\tISBN              :   {}\n\nYou are requested to not disclose the Reservation ID and Reservation Key to anyone. These details will have to be provided at the clerk's desk at the time of issuing the reserved book.\n\nThank you.\nRegards.\nLIS.
              """.format(rID, rKey, isbn)

        Clerk.NotifyMember("BOOK RESERVED SUCCESSFULLY", msg, lmcn)
        #pop up message to clerk if reservation was successful
        ApplicationState.CurrentWidgets[2].delete(0, END)
        ApplicationState.CurrentWidgets[4].delete(0, END)
        messagebox.showinfo("", "Book is successfully reserved.\nMember will be able to see the necessary details in his/her account.")
        
    def ReturnBook ( self ) :		#GUI for return book button
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        head = Label(ApplicationState.Root, text="  □  RETURN ISSUED BOOK", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        #design label and entry box for issue id
        askId = Label(ApplicationState.Root, text="ISSUE ID  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        idd = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #button design for return book and go back
        returnn = Button(ApplicationState.Root, text="RETURN BOOK", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.BookReturnedUpdateDatabase)
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Clerk.ShowFirstPage)
        
        span1 = 7
        span2 = 17
        gap = 25
        #placement of label and entry box for issue id
        ApplicationState.Root.grid_rowconfigure(7, minsize=gap)
        askId.grid(row=8, column=3, columnspan=span1, sticky=W+E)
        idd.grid(row=8, column=13, columnspan=span2, sticky=W+E)
        #placement of buttons
        ApplicationState.Root.grid_rowconfigure(9, minsize=gap+15)
        goBack.grid(row=10, column=4, columnspan=8, sticky=W+E)
        returnn.grid(row=10, column=21, columnspan=8, sticky=W+E)
        #widgets list
        ApplicationState.CurrentWidgets = [ head , askId , idd , returnn , goBack ]

    def BookReturnedUpdateDatabase ( self ) :	#backend of return operation
    	#check if issue id entered
        if ( ApplicationState.CurrentWidgets[2].get().strip() == "" ) :
            messagebox.showerror("", "Issue ID not specified!")
            return
        issueId = ApplicationState.CurrentWidgets[2].get().strip()
        #connect to database Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )

        cursorr = db.cursor(buffered=True)
        #fetch data matching to issue  id from table CurrentlyissuedBooks in database Library
        cursorr.execute("SELECT * FROM CurrentlyIssuedBooks WHERE IssueId=%s", (issueId, ))
        results = cursorr.fetchall()
        #if no such  book has been issued then do nothing
        if ( len(results) == 0 ) :
            messagebox.showerror("", "Specified Issue ID not found in the database!")
            db.close()
            return
        #if issue id  found then delete from CurrentlyissuedBooks and add to ShowBooksIssuedInPast
        result = results[0]
        dor = datetime.strptime(result[4], '%d/%m/%Y')	#date and time of return 
        delay = (datetime.now()-dor).days
        #check for delay in returning book
        delay = max(delay, 0)
        isFine = delay > 0
        penalty = delay * ApplicationDesign.Penalty 	#calculate penalty if delayed return
        dateOfIssue = result[3]
        lmcn = result[2]
        isbn = result[1]
        dateOfReturn = datetime.today().strftime("%d/%m/%Y")
        #enter log of book being issued and returned in BooksIssuedInPast
        cursorr.execute("INSERT INTO BooksIssuedInPast VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", 
                        (issueId, isbn, lmcn, dateOfIssue, dateOfReturn, int(delay), float(penalty), int(not isFine)) )
        db.commit()
        #delete log of book from CurrentlyissuedBooks
        cursorr.execute("DELETE FROM CurrentlyIssuedBooks WHERE IssueID=%s", (issueId,))
        db.commit()
        #update database Library
        #connect to database Accounts
        accdb = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        cursorrAcc = accdb.cursor(buffered=True)
        #check type of member and decrease currently issued books by 1
        if ( lmcn[:2] != "FC" ) :
            cursorrAcc.execute("UPDATE NonFacultyMembers SET IssueCount=IssueCount-1 WHERE LMCN=%s", (lmcn,))
        else :
            cursorrAcc.execute("UPDATE FacultyMembers SET IssueCount=IssueCount-1 WHERE LMCN=%s", (lmcn,))
        #update and close database
        accdb.commit()
        accdb.close()
        #if the returned book has been reserved then send the reserver a message 
        if ( result[5] == 1 ) :
            cursorr.execute("UPDATE ReservedBooks SET IsReturned=1, DateOfReturn=%s WHERE IssueID=%s", (dateOfReturn, issueId))	#update ReservedBooks table
            db.commit()
            cursorr.execute("SELECT * FROM ReservedBooks WHERE IssueID=%s", (issueId, ))
            rec = cursorr.fetchall()[0]
            msg = """Dear Member,\nThe book that you reserved a while back has been returned. It is waiting for you to be formally issued. The reservation will expire in 7 days from today. Please collect the book as soon as possible.\n\n\tRESERVATION ID      :   {}\n\nThank you.\nRegards.\nLIS.
                    """.format(rec[0])
            Clerk.NotifyMember("RESERVED BOOK RETURNED", msg, rec[3])
        else :			#if not reserved then just add it to the noraml status in the catalogue
            cursorr.execute("UPDATE Catalogue SET Available=Available+1 WHERE ISBN=%s", (isbn,))
            db.commit()

        if ( isFine ) :			#if there was a delay in returning a book then message mentioning the fine is sent to the user
            msg = """Dear Member,\nThe following book you issued a while back was returned successfully. You returned the book beyond the due date of return and hence you are penalized with some fine. Please clear the fine as soon as possible. Try to be more punctual from the next time.\n\n\tISSUE ID                :   {}\n\tISBN                    :   {}\n\tDATE OF ISSUE           :   {}\n\tDUE DATE OF RETURN      :   {}\n\tPENALTY                 :   Rs. {}\n\nThank you.\nRegards.\nLIS.
                  """.format(issueId, isbn, dateOfIssue, dor.strftime("%d/%m/%Y"), penalty)
        else :		#if the  book is returnef before time then a simple message metioning book return successul will be sent
            msg = """Dear Member,\nThe following book you issued a while back was returned successfully.\n\n\tISSUE ID                :   {}\n\tISBN                    :   {}\n\tDATE OF ISSUE           :   {}\n\tDUE DATE OF RETURN      :   {}\n\nThank you.\nRegards.\nLIS.
                    """.format(issueId, isbn, dateOfIssue, dor.strftime("%d/%m/%Y"))
        
        Clerk.NotifyMember("BOOK RETURNED SUCCESSFULLY", msg, lmcn)
        
        messagebox.showinfo("", "Book was returned successfully!")
        payFine = False
        if ( isFine ) :		#reminder of the fine to be paid
           payFine = messagebox.askyesno("", "The member returned the book {} days after the due date and hence is supposed to pay Rs. {} as penalty.\nDo you want to proceed to Pay Fine section?".format(delay, penalty), default='yes')
        if ( payFine ) :	#member pays fine immediately
            ApplicationState.CurrentUser.PayFine()
        else :		#return to clerk dashboard
            Clerk.ShowFirstPage()

    def AddNewBook ( self ) :		#GUI to Add new book 
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        head = Label(ApplicationState.Root, text="  □  ADD NEW BOOK INTO THE CATALOGUE", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=3, column=1, columnspan=32)
        #design of label and entry box for ISBN
        askIsbn = Label(ApplicationState.Root, text="ISBN  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        isbn = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of label and entry box for Title
        askTitle = Label(ApplicationState.Root, text="TITLE  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        title = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design and entry box for Authors
        askAuthors = Label(ApplicationState.Root, text="AUTHOR(s)  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        authors = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design and entry box for Language
        askLang = Label(ApplicationState.Root, text="LANGUAGE  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        lang = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design and entry box for Rack no.
        askRack = Label(ApplicationState.Root, text="RACK NO.  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        rack = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design and entry box for copies of book
        askCopies = Label(ApplicationState.Root, text="NO. OF COPIES  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        copies = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #button to confirm addition
        add = Button(ApplicationState.Root, text="ADD TO CATALOGUE", bg='white',  font=('',20,'bold'), command = self.AddBookToDatabase)
        #go back to clerk dashboard
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Clerk.ShowFirstPage)

        start = 4
        gap = 15
        span1 = 7
        span2 = 17
        shift = 2

        ApplicationState.Root.grid_rowconfigure(start, minsize=gap)
        #placement of label and entry box for ISBN
        askIsbn.grid(row=start+1, column=1+shift, columnspan=span1, sticky=W+E)
        isbn.grid(row=start+1, column=13+shift, columnspan=span2, sticky=W+E)
        #placement of label and entry box for Title
        ApplicationState.Root.grid_rowconfigure(start+2, minsize=gap)

        askTitle.grid(row=start+3, column=1+shift, columnspan=span1, sticky=W+E)
        title.grid(row=start+3, column=13+shift, columnspan=span2, sticky=W+E)
        #placement of label and entry box for Authors
        ApplicationState.Root.grid_rowconfigure(start+4, minsize=gap)
        
        askAuthors.grid(row=start+5, column=1+shift, columnspan=span1, sticky=W+E)
        authors.grid(row=start+5, column=13+shift, columnspan=span2, sticky=W+E)
        #placement of label and entry box for Language
        ApplicationState.Root.grid_rowconfigure(start+6, minsize=gap)

        askLang.grid(row=start+7, column=1+shift, columnspan=span1, sticky=W+E)
        lang.grid(row=start+7, column=13+shift, columnspan=span2, sticky=W+E)
        #placement of label and entry box for Rack no.
        ApplicationState.Root.grid_rowconfigure(start+8, minsize=gap)

        askRack.grid(row=start+9, column=1+shift, columnspan=span1, sticky=W+E)
        rack.grid(row=start+9, column=13+shift, columnspan=span2, sticky=W+E)
        #placement of label and entry box for Copies
        ApplicationState.Root.grid_rowconfigure(start+10, minsize=gap)

        askCopies.grid(row=start+11, column=1+shift, columnspan=span1, sticky=W+E)
        copies.grid(row=start+11, column=13+shift, columnspan=span2, sticky=W+E)
        #placement of butons
        ApplicationState.Root.grid_rowconfigure(start+12, minsize=gap)

        add.grid(row=start+13, column=22, columnspan=8, sticky=W+E)

        goBack.grid(row=start+13, column=5, columnspan=8, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [ head , askIsbn , isbn , askTitle, title, askAuthors, authors, askLang, lang, askRack, rack, askCopies, copies, add, goBack ]

    def AddBookToDatabase ( self ) :	#backend to add new book
    	#check if ISBN has been entered
        if ( ApplicationState.CurrentWidgets[2].get().strip() == "" ) :
            messagebox.showerror("", "ISBN not specified!")
            return
        #check if Title has been entered
        if ( ApplicationState.CurrentWidgets[4].get().strip() == "" ) :
            messagebox.showerror("", "Title not specified!")
            return
        #check if Authors has been entered
        if ( ApplicationState.CurrentWidgets[6].get().strip() == "" ) :
            messagebox.showerror("", "Author(s) not specified!")
            return
        #check if Language has been entered
        if ( ApplicationState.CurrentWidgets[8].get().strip() == "" ) :
            messagebox.showerror("", "Language not specified!")
            return
        #check if Rackno. has been entered
        if ( ApplicationState.CurrentWidgets[10].get().strip() == "" ) :
            messagebox.showerror("", "Rack Number not specified!")
            return
        #check if no. of copies has been entered
        if ( ApplicationState.CurrentWidgets[12].get().strip() == "" ) :
            messagebox.showerror("", "Number of copies not specified!")
            return
        #connect to databse library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )

        cursorr = db.cursor(buffered=True)
        #use table catalogue in database Library
        cursorr.execute("SELECT * FROM Catalogue WHERE ISBN=%s", (ApplicationState.CurrentWidgets[2].get(),))
        if ( len(cursorr.fetchall()) ) :		#check if the book is present already
            messagebox.showerror("", "Book with the specified ISBN is already present in the catalogue!")
            db.close()
            return

        num = ApplicationState.CurrentWidgets[12].get()	#no. of copies
        try :
            num = eval(num)
        except :
            messagebox.showerror("", "Invalid entry for number of copies!")
            db.close()
            return
        if ( num <= 0 ) :	#no of copies can only be positive
            messagebox.showerror("", "Invalid entry for number of copies!")
            db.close()
            return
        
        #add book to catalogue
        sql = "INSERT INTO Catalogue VALUES (%s, %s, %s, %s, %s, %s, %s, '00/00/0000', %s)"
        val = (ApplicationState.CurrentWidgets[2].get(), ApplicationState.CurrentWidgets[4].get(), ApplicationState.CurrentWidgets[6].get(),
                ApplicationState.CurrentWidgets[8].get(), ApplicationState.CurrentWidgets[10].get(), num, num, date.today().strftime("%d/%m/%Y") )
        cursorr.execute(sql, val)
        #update and close database Library
        db.commit()
        db.close()
        #print success message
        messagebox.showinfo("", "New book added to the catalogue successfully!")
        #return to clerk dashboard
        Clerk.ShowFirstPage()

    def RemoveExistingBook ( self ) :		#GUI of delete book page
    	#unmap previuous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        head = Label(ApplicationState.Root, text="  □  REMOVE BOOK FROM CATALOGUE", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        #design oflabel and entry box 
        askIsbn = Label(ApplicationState.Root, text="BOOK'S ISBN  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        isbn = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of buton to remove book or go back
        remove = Button(ApplicationState.Root, text="REMOVE BOOK", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.DeleteBookFromDatabase)
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Clerk.ShowFirstPage)
        
        span1 = 7
        span2 = 17
        gap = 25
        #placement of label and entry box
        ApplicationState.Root.grid_rowconfigure(7, minsize=gap)
        askIsbn.grid(row=8, column=3, columnspan=span1, sticky=W+E)
        isbn.grid(row=8, column=13, columnspan=span2, sticky=W+E)
        #placement of buttons
        ApplicationState.Root.grid_rowconfigure(9, minsize=gap+15)
        goBack.grid(row=10, column=4, columnspan=8, sticky=W+E)
        remove.grid(row=10, column=21, columnspan=8, sticky=W+E)
        #widgets list
        ApplicationState.CurrentWidgets = [ head , askIsbn , isbn , remove , goBack ]
    
    def DeleteBookFromDatabase ( self ) :		#backend to delete faulty book
    	#check if ISBN has been entered
        if ( ApplicationState.CurrentWidgets[2].get().strip() == "" ) :
            messagebox.showerror("", "ISBN not specified!")
            return
        isbn = ApplicationState.CurrentWidgets[2].get().strip()
        #connect to database Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )

        cursorr = db.cursor(buffered=True)
        #find book in catalogue 
        cursorr.execute("SELECT * FROM Catalogue WHERE ISBN=%s", (isbn, ))
        #validate ISBN
        if ( len(cursorr.fetchall()) == 0 ) :
            messagebox.showerror("", "Specified ISBN not found in the database!")
            db.close()
            return
        #fetch all books with the ISBN in catalogue
        cursorr.execute("SELECT * FROM Catalogue WHERE ISBN=%s AND Copies = Available", (isbn, ))
        if ( len(cursorr.fetchall()) == 0 ) :
            messagebox.showerror("", "All the copies of the book are not present on the rack!")
            db.close()
            return
        #final confirmation before proceeding to delete book
        confirm = messagebox.askyesno("FATAL WARNING", """If you proceed, the book will be permanently deleted from the catalogue.\nAre you sure you want to remove this book from the catalogue?""", icon='warning', default='no')
        #if not confirmed, do nothing
        if (not confirm):
            db.close()
            ApplicationState.CurrentWidgets[2].delete(0, END)
            return
        #if deletion confirmed, delete,update and close database
        cursorr.execute("DELETE FROM Catalogue WHERE ISBN=%s", (isbn, ))
        db.commit()
        db.close()
        #annotate successful deletion with message 
        messagebox.showinfo("", "Book is successfully removed from the catalogue!")
        #return to clerk dashboard
        Clerk.ShowFirstPage()

    def PayFine ( self ) :		#GUI to pay fine
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        head = Label(ApplicationState.Root, text="  □  PAY FINE", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        #labels and entry boxes for fillinf in issue id of book which was due and incurred a fine
        askId = Label(ApplicationState.Root, text="ISSUE ID  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        idd = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #pay fine and go back button design
        pay = Button(ApplicationState.Root, text="PAY FINE", bg='white',  font=('',20,'bold'), command = ApplicationState.CurrentUser.ClearFineFromDatabase)
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Clerk.ShowFirstPage)
        
        span1 = 7
        span2 = 17
        gap = 25
        #placement of label and entry box
        ApplicationState.Root.grid_rowconfigure(7, minsize=gap)
        askId.grid(row=8, column=3, columnspan=span1, sticky=W+E)
        idd.grid(row=8, column=13, columnspan=span2, sticky=W+E)
        #placement of buttons
        ApplicationState.Root.grid_rowconfigure(9, minsize=gap+15)
        goBack.grid(row=10, column=4, columnspan=8, sticky=W+E)
        pay.grid(row=10, column=21, columnspan=8, sticky=W+E)
        #widget list 
        ApplicationState.CurrentWidgets = [ head , askId , idd , pay , goBack ]
    
    def ClearFineFromDatabase ( self ) :		#backend of resetting fine of a member after it has been paid
    	#validate issue id of book generated at the time of book issue
        if ( ApplicationState.CurrentWidgets[2].get().strip() == "" ) :
            messagebox.showerror("", "Issue ID not specified!")
            return
        idd = ApplicationState.CurrentWidgets[2].get().strip()
        #connect to database Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )

        cursorr = db.cursor(buffered=True)
        #find the book using the issue id from the table BooksIssuedInPast from Library database
        cursorr.execute("SELECT * FROM BooksIssuedInPast WHERE IssueID=%s", (idd, ))
        results = cursorr.fetchall()
        #validate issue Id 
        if ( len(results) == 0 ) :
            messagebox.showerror("", "Specified Issue ID not found in the database!")
            db.close()
            return
        #if valid issue id then check for pending fines
        cursorr.execute("SELECT * FROM BooksIssuedInPast WHERE IssueID=%s AND FinePaid = 0", (idd, ))
        if ( len(cursorr.fetchall()) == 0 ) :
            messagebox.showerror("", "No fine is pending for the specified Issue ID!")
            db.close()
            return
        #if fines were due then clear dues if fine has benn collected from member
        cursorr.execute("UPDATE BooksIssuedInPast SET FinePaid=1 WHERE IssueId=%s", (idd, ))
        #update and close database
        db.commit()
        db.close()
        #send member the notification of clearing of dues
        messagebox.showinfo("", "Fine successfully cleared! The member will now be able to see the necessary details in his/her account.")

        msg = """Dear Member,\nThe fine for the following book was paid successfully. We strongly urge you to be more punctual in returning the issued books from the next time.\n\n\tISSUE ID        :   {}\n\tAMOUNT PAID  :   Rs. {}\n\nThank you.\nRegards.\nLIS.
              """.format(idd, results[0][6])

        Clerk.NotifyMember("FINE SUCCESSFULLY PAID", msg, results[0][2])
        #return to clerk dashboard
        Clerk.ShowFirstPage()

    def ChangePassword ( self ) :		#change password of clerk
        if ( ApplicationState.OldPasswordField.get() == "" ) :
            messagebox.showerror("", "Old password not specified!")
            return
        if ( ApplicationState.NewPasswordField.get() == "" ) :
            messagebox.showerror("", "New password not specified!")
            return
        if ( ApplicationState.ConfirmPasswordField.get() == "" ) :
            messagebox.showerror("", "Confirmation password not specified!")
            return

    	#connect to databse Accounts
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #select for loggrd in clerk in the Administrators table in Account Database
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM Administrators WHERE ID=%s", (ApplicationState.CurrentUser._Individual__id,))
        pw = cursorr.fetchall()[0][4]

        #validate old password for setting new paasword
        if ( md5(ApplicationState.OldPasswordField.get().encode()).hexdigest() != pw ) :
            messagebox.showerror('ERROR', 'Incorrect Old Password !')
            db.close()
            return

        if ( ApplicationState.NewPasswordField.get().strip() == "" ) :
            messagebox.showerror('ERROR', 'New password has no characters !')
            db.close()
            return
        
        if ( len(ApplicationState.NewPasswordField.get()) < 7 ) :
            messagebox.showerror('ERROR', 'Password must be atleast 7 characters long')
            db.close()
            return

        #check if passwords typed in new password and confirm passwords are the same 
        if ( ApplicationState.NewPasswordField.get() != ApplicationState.ConfirmPasswordField.get() ) :
            messagebox.showerror('ERROR', 'Incorrect "New" and "Confirm" Passwords do not match !')
            db.close()
            return
        #save new password in md5 encryption
        sql = "UPDATE Administrators SET password = md5(%s) WHERE ID = %s"
        cursorr.execute(sql, (ApplicationState.NewPasswordField.get(), ApplicationState.CurrentUser._Individual__id))
        #update and close database
        db.commit()
        db.close()
       	#reset variables to null as they might conflict in similar functionality of other user
        ApplicationState.OldPasswordField.set("")
        ApplicationState.NewPasswordField.set("")
        ApplicationState.ConfirmPasswordField.set("")
        #return to clerk dashboard
        Clerk.ShowFirstPage()


class Librarian ( Individual ) :		#class Librarian is specialization of Individual
    
    def __init__ ( self , idd , name , dob , regDate ) :	#constructor
        self.__status = 'LI'
        Individual.__init__( self, idd, name, dob, regDate )

    @staticmethod
    def IsValidLibrarian ( loginId , password ) :		#validate librarian login
    	#check account type
        if ( loginId[:2] != 'LI' ) :
            messagebox.showerror('ERROR', 'Incorrect LOGIN ID entered !')
            return
        #connect to Accounts database
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #fetch all accounts with matching userid from Administrators table in Accounts Database
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM Administrators WHERE ID=%s", (loginId,))
        results = cursorr.fetchall()
        db.close()
        #no matching account found-
        if ( not len(results) ) :
            messagebox.showerror('ERROR', 'Incorrect LOGIN ID entered !')
            return
        #userid mached but password did not
        if ( results[0][4] != md5(password.encode()).hexdigest() ) :
            messagebox.showerror('ERROR', 'Incorrect password entered !')
            return
        #if both match then enter the librarian dashboard 
        ApplicationState.CurrentUser = Librarian(loginId, results[0][1], results[0][2], results[0][3])
        Librarian.ShowFirstPage()
    
    @staticmethod
    def ShowFirstPage ( ) :		#GUI Design of Librarian dashboard
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design of various buttons
        register = Button(ApplicationState.Root, text='REGISTER NEW MEMBER', bg='white',  font=('',20,'bold'), command = Librarian.ShowRegistrationPage)
        deregister = Button(ApplicationState.Root, text='DE-REGISTER MEMBER', bg='white',  font=('',20,'bold'), command = Librarian.ShowDeRegistrationPage)
        showMembers = Button(ApplicationState.Root, text='SHOW ALL MEMBERS', bg='white',  font=('',20,'bold'), command = Librarian.ShowMembersPage)
        showCat = Button(ApplicationState.Root, text='SHOW CATALOGUE', bg='white',  font=('',20,'bold'), command = Librarian.ShowCatalogue)
        issuedBooks = Button(ApplicationState.Root, text='SHOW CURRENTLY ISSUED BOOKS', bg='white',  font=('',20,'bold'), command = Librarian.ShowCurrentlyIssuedBooks)
        overdueBooks = Button(ApplicationState.Root, text='SHOW OVER-DUE BOOKS', bg='white',  font=('',20,'bold'), command = Librarian.ShowOverDueBooks)
        pastIssued = Button(ApplicationState.Root, text='SHOW BOOKS ISSUED IN PAST', bg='white',  font=('',20,'bold'), command = Librarian.ShowBooksIssuedInPast)
        popularityAnal = Button(ApplicationState.Root, text='ANALYZE POPULARITY OF BOOKS', bg='white',  font=('',20,'bold'), command = Librarian.ShowPopularityAnalysisPage)
        resetPassword = Button(ApplicationState.Root, text='RESET PASSWORD', bg='white',  font=('',20,'bold'), command = Librarian.ResetPassword)
        
        span = 12
        start = 4
        gap = 35

        shift = 2
        #placement of the buttons
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)

        register.grid(row=start, column=2+shift, columnspan=span, sticky=W+E)
        deregister.grid(row=start, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+1, minsize=gap)

        showMembers.grid(row=start+2, column=2+shift, columnspan=span, sticky=W+E)
        showCat.grid(row=start+2, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+3, minsize=gap)
        
        issuedBooks.grid(row=start+4, column=2+shift, columnspan=span, sticky=W+E)
        overdueBooks.grid(row=start+4, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+5, minsize=gap)
        
        pastIssued.grid(row=start+6, column=2+shift, columnspan=span, sticky=W+E)
        popularityAnal.grid(row=start+6, column=17+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+7, minsize=gap)
        
        resetPassword.grid(row=start+8, column=9+shift, columnspan=span, sticky=W+E)
        ApplicationState.Root.grid_rowconfigure(start+9, minsize=gap+5)
        
        logOut = Button(ApplicationState.Root, text='LOG OUT', bg='white',  font=('',20,'bold'), command = ApplicationState.ShowHomePage)
        logOut.grid(row=start+10, column=14, columnspan=7, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [register, deregister, showMembers, showCat, issuedBooks, overdueBooks, pastIssued, popularityAnal, resetPassword, logOut]

    @staticmethod
    def ShowRegistrationPage ( ) :		#GUI design to add new member to library
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        head = Label(ApplicationState.Root, text="  □  REGISTER NEW MEMBER", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=3, column=1, columnspan=32)
        #design of drop down menu to select member account type
        typeMem = [ "Faculty Member" , "Under-Graduate" , "Post-Graduate" , "Research Scholar" ]
        ApplicationState.ChooseMemberField = StringVar() 
        ApplicationState.ChooseMemberField.set( "CHOOSE MEMBER TYPE" ) 
        drop = OptionMenu( ApplicationState.Root , ApplicationState.ChooseMemberField , *typeMem )

        helv36 = tkFont.Font(family='', size=22, weight="bold")
        drop.config(font=helv36)

        helv20 = tkFont.Font(family='', size=20)
        menu = ApplicationState.Root.nametowidget(drop.menuname)
        menu.config(font=helv20)
        #design of entry box and label for institute id
        askId = Label(ApplicationState.Root, text="INSTITUTE ID  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        iD = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of entry box and label for name
        askName = Label(ApplicationState.Root, text="NAME  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        name = Entry(ApplicationState.Root, width=50, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #calender to select date of birth of member
        cal = DateEntry(ApplicationState.Root, dateformat=3, width=12, background='darkblue',
                    foreground='white', borderwidth=4, Calendar =2018, maxdate=date.today())
        #calender accepts date till present day
        cal = Calendar(ApplicationState.Root, selectmode="day",year=2002, month=1, day=1, maxdate=date.today(), width=500, height=500)

        askDob = Label(ApplicationState.Root, text="DATE OF BIRTH  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        #register button to add new member
        register = Button(ApplicationState.Root, text="CREATE ACCOUNT", bg='white',  font=('',20,'bold'), command = Librarian.Register)
        #go back button to return  to librarian dashboard
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        
        start = 4
        gap = 25
        span1 = 7
        span2 = 17
        #palcement of various widgets
        ApplicationState.Root.grid_rowconfigure(start, minsize=gap)
        drop.grid(row=start+1, column=13, columnspan=10, sticky=W+E)
        #palcement of institute id
        ApplicationState.Root.grid_rowconfigure(start+2, minsize=gap)
        askId.grid(row=start+3, column=1, columnspan=span1, sticky=W+E)
        iD.grid(row=start+3, column=13, columnspan=span2, sticky=W+E)
        #palcement of name
        ApplicationState.Root.grid_rowconfigure(start+4, minsize=gap)
        askName.grid(row=start+5, column=1, columnspan=span1, sticky=W+E)
        name.grid(row=start+5, column=13, columnspan=span2, sticky=W+E)
        #palcement of date of birth
        ApplicationState.Root.grid_rowconfigure(start+6, minsize=gap)
        askDob.grid(row=start+7, column=1, columnspan=span1, sticky=W+E)
        cal.grid(row=start+7, column=13, columnspan=7, rowspan=6, sticky=W+E+N+S)
        #palcement of buttons
        ApplicationState.Root.grid_rowconfigure(start+8, minsize=gap)
        register.grid(row=start+8, column=22, columnspan=8, sticky=W+E)
        goBack.grid(row=start+10, column=22, columnspan=8, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [ head , drop , askId, iD , askName , name , askDob , cal , register , goBack ]

    @staticmethod
    def Register ( ) :	#backend to register a member  and add to database
    	#check if member type has been selected
        if ( ApplicationState.ChooseMemberField.get() == "CHOOSE MEMBER TYPE" ) :
            messagebox.showerror('ERROR', 'Member Type not specified!')
            return
        #check if institue id  has been entered
        if ( len(ApplicationState.CurrentWidgets[3].get().strip()) == 0 ) :
            messagebox.showerror('ERROR', 'Institute ID not specified!')
            return
        #check if name has  been entered
        if ( len(ApplicationState.CurrentWidgets[5].get().strip()) == 0 ) :
            messagebox.showerror('ERROR', 'Name not specified!')
            return
        #connect to Accounts database
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )

        cursorr = db.cursor(buffered=True)

        LMCN = ""
        #if the user to be register is of type NonFaculty then-
        if ( ApplicationState.ChooseMemberField.get() != "Faculty Member" ) :
        	#chek if account of nonfaculty member with same institute id does not already exist
            cursorr.execute("SELECT * FROM NonFacultyMembers WHERE RollNo=%s", (ApplicationState.CurrentWidgets[3].get(),))
            if ( len(cursorr.fetchall()) ) :
                messagebox.showerror('ERROR', 'Account already exists for the specifed Intitute ID!')
                db.close()
                return
            #chek if account of faculty member with same institute id does not already exist
            cursorr.execute("SELECT * FROM FacultyMembers WHERE InstituteID=%s", (ApplicationState.CurrentWidgets[3].get(),))
            if ( len(cursorr.fetchall()) ) :
                messagebox.showerror('ERROR', 'Account already exists for the specifed Intitute ID!')
                db.close()
                return
            
            dob = ApplicationState.CurrentWidgets[7].get_date()
            dob = datetime.strptime(dob, '%d/%m/%y')
            #check that age is more than 16 years
            if ( ( (datetime.today()-dob).days ) / 365 < 16 ) :
                messagebox.showerror('ERROR', 'Non-Faculty Member should be at least 16 years old!')
                db.close()
                return
            #create LMCN for new user-
            pre = None
            if ' ' in ApplicationState.ChooseMemberField.get() :
                parts = ApplicationState.ChooseMemberField.get().split(' ')
                pre = parts[0][0] + parts[1][0]
            if '-' in ApplicationState.ChooseMemberField.get() :
                parts = ApplicationState.ChooseMemberField.get().split('-')
                pre = parts[0][0] + parts[1][0]
            year = ApplicationState.CurrentWidgets[3].get()[:2]
            initials = ""
            parts = ApplicationState.CurrentWidgets[5].get().split(' ')
            if (len(parts) == 1) :
                initials += parts[0][:2].upper()
            else :
                initials += parts[0][0].upper() + parts[1][0].upper()
            #dob stored in dd/mm/yyyy format
            dob = ApplicationState.CurrentWidgets[7].get_date()
            dob = datetime.strptime(dob, '%d/%m/%y').strftime("%d/%m/%Y")
            
            LMCN = pre + year + initials + str(randint(1000,9999))
            #check if the LMCN to be assigned does not already exist
            while True :
                cursorr.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s", (LMCN,))
                if ( not len(cursorr.fetchall()) ) :    break
                LMCN = pre + year + initials + str(randint(1000,9999))
            #default password is-
            password = LMCN + "_" + dob
            #add new user in NonFacultyMembers table 
            sql = "INSERT INTO NonFacultyMembers VALUES (%s, %s, %s, %s, %s, 0, md5(%s))"
            val = (LMCN, ApplicationState.CurrentWidgets[3].get().strip(), ApplicationState.CurrentWidgets[5].get().strip(), 
                    dob, date.today().strftime("%d/%m/%Y") ,password)
            cursorr.execute(sql, val)
            #update database Accounts
            db.commit()
        #if member to be registered is of type Faculty
        elif ( ApplicationState.ChooseMemberField.get() == "Faculty Member" ) :
            
            dob = ApplicationState.CurrentWidgets[7].get_date()
            dob = datetime.strptime(dob, '%d/%m/%y')
            #check if institue id does not match wtih some otherFaculty member
            cursorr.execute("SELECT * FROM FacultyMembers WHERE InstituteID=%s", (ApplicationState.CurrentWidgets[3].get(),))
            if ( len(cursorr.fetchall()) ) :
                messagebox.showerror('ERROR', 'Account already exists for the specifed Intitute ID!')
                db.close()
                return
            #check if institue id does not match wtih some other Non Faculty member
            cursorr.execute("SELECT * FROM NonFacultyMembers WHERE RollNo=%s", (ApplicationState.CurrentWidgets[3].get(),))
            if ( len(cursorr.fetchall()) ) :
                messagebox.showerror('ERROR', 'Account already exists for the specifed Intitute ID!')
                db.close()
                return
            #verify that age of faculty is more than 25 years
            if ( ( (datetime.today()-dob).days ) / 365 < 25 ) :
                messagebox.showerror('ERROR', 'Faculty Member should be at least 25 years old!')
                db.close()
                return
            #create LMCN-
            pre = "FC"
           
            initials = ""
            parts = ApplicationState.CurrentWidgets[5].get().split(' ')
            if (len(parts) == 1) :
                initials += parts[0][:2].upper()
            else :
                initials += parts[0][0].upper() + parts[1][0].upper()
            
            dob = ApplicationState.CurrentWidgets[7].get_date()
            dob = datetime.strptime(dob, '%d/%m/%y').strftime("%d/%m/%Y")
            
            LMCN = pre + str(randint(1,99)).zfill(2) + initials + str(randint(1000,9999))
            #check if the LMCN is unique or not
            while True :
                cursorr.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s", (LMCN,))
                if ( not len(cursorr.fetchall()) ) :    break
                LMCN = pre + str(randint(1,99)).zfill(2) + initials + str(randint(1000,9999))
            #set default  password
            password = LMCN + "_" + dob
            print(password)
            #enter user in datbase table FacultyMembers
            sql = "INSERT INTO FacultyMembers VALUES (%s, %s, %s, %s, 0, md5(%s), %s)"
            val = (LMCN, ApplicationState.CurrentWidgets[5].get(), 
                    dob, date.today().strftime("%d/%m/%Y") ,password, ApplicationState.CurrentWidgets[3].get())
            cursorr.execute(sql, val)
            db.commit()	#update database
         
        db.close()
         #confirm registration
        messagebox.showinfo("REGISTERATION SUCCESSFUL", "Member is successfully registered!\nLMCN: "+LMCN)
        #return to dashboard
        Librarian.ShowFirstPage()	
        return

    @staticmethod
    def ShowDeRegistrationPage ( ) :		#GUI design to deregister member
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        head = Label(ApplicationState.Root, text="  □  DE-REGISTER EXISTING MEMBER", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        #design of label and entry box for LMCN
        askId = Label(ApplicationState.Root, text="LMCN  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        iD = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of label and entry box for Name
        askName = Label(ApplicationState.Root, text="NAME  ", bg=ApplicationDesign.BackgroundColor, font=('',22,'bold'), width=15, anchor=CENTER)
        name = Entry(ApplicationState.Root, width=40, bg='white', font=('',20,''), highlightthickness=ApplicationDesign.HighlightThickness, highlightcolor=ApplicationDesign.Theme)
        #design of buttons for deregister and goback
        deregister = Button(ApplicationState.Root, text="DELETE ACCOUNT", bg='white',  font=('',20,'bold'), command = Librarian.DeRegister)
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        
        span1 = 7
        span2 = 17
        gap = 25
        #placement of LMCN
        ApplicationState.Root.grid_rowconfigure(5, minsize=gap)
        askId.grid(row=6, column=3, columnspan=span1, sticky=W+E)
        iD.grid(row=6, column=13, columnspan=span2, sticky=W+E)
        #placement of name
        ApplicationState.Root.grid_rowconfigure(7, minsize=gap)
        askName.grid(row=8, column=3, columnspan=span1, sticky=W+E)
        name.grid(row=8, column=13, columnspan=span2, sticky=W+E)
        #placement of buttons
        ApplicationState.Root.grid_rowconfigure(9, minsize=gap+15)
        deregister.grid(row=10, column=22, columnspan=8, sticky=W+E)
        goBack.grid(row=10, column=3, columnspan=8, sticky=W+E)
        #widgets list
        ApplicationState.CurrentWidgets = [ head , askId, iD , askName , name , deregister , goBack ]
    
    @staticmethod
    def DeRegister ( ) :		#backend to de register a member 
    	#check if LMCN has been entered
        if ( len(ApplicationState.CurrentWidgets[2].get().strip()) == 0 ) :
            messagebox.showerror("", "Library Membership Code Number not specified!")
            return
        #check if Name has been entered
        if ( len(ApplicationState.CurrentWidgets[4].get().strip()) == 0 ) :
            messagebox.showerror("", "Name not specified!")
            return
        #connect to database Accounts
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #connect to database Library
        dbLib = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )

        cursorr = db.cursor(buffered=True)
        cursorLib = dbLib.cursor(buffered=True)
        #if  account is of non faculty member
        if ( ApplicationState.CurrentWidgets[2].get().strip()[:2] != "FC" ) :
            cursorr.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            #if no non faculty member with the specified LMCN exits-
            if (len(cursorr.fetchall()) == 0) :
                messagebox.showerror("", "Specified LMCN not found!")
                db.close()
                dbLib.close()
                return
            #if LMCN matches but name does not-
            cursorr.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s AND Name=%s", 
                (ApplicationState.CurrentWidgets[2].get().strip(),ApplicationState.CurrentWidgets[4].get().strip()))
            if (len(cursorr.fetchall()) == 0) :
                messagebox.showerror("", "Incorrect name for the specified LMCN!")
                db.close()
                dbLib.close()
                return
            #if name and LMCN match but the member has presently issued books we cannot deregister as then books will be lost
            cursorr.execute("SELECT * FROM NonFacultyMembers WHERE LMCN=%s AND IssueCount=0", (ApplicationState.CurrentWidgets[2].get().strip(),))
            if (len(cursorr.fetchall()) == 0) :
                messagebox.showerror("", "Specified member has not yet returned some books!")
                db.close()
                dbLib.close()
                return
            #if the member has matching name,LMCN and has returned all books but hasnt paid fine we cannot deregister
            cursorLib.execute("SELECT * FROM BooksIssuedInPast WHERE IssuerLMCN=%s AND FinePaid=0", (ApplicationState.CurrentWidgets[2].get().strip(),))
            if (len(cursorLib.fetchall()) != 0) :
                messagebox.showerror("", "Specified member has not yet cleared some penalties!")
                db.close()
                dbLib.close()
                return
            #if all is ok for deregistration we ask for final confirmation before proceeding to deregistration
            confirm = messagebox.askyesno("FATAL WARNING", """Deleting an account will permanently erase the history of all books issued in the past by that member, cancel all his/her reservations and forget all activity tracked by the notifications.\nAre you sure you want to de-register this member?""", icon='warning', default='no')
            if (not confirm) :
                db.close()
                dbLib.close()
                return
            #delete the member from the database-
            #delete messages/notifications
            cursorr.execute("DELETE FROM Messages WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            db.commit()
            #delete book issue history
            cursorLib.execute("DELETE FROM BooksIssuedInPast WHERE IssuerLMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            dbLib.commit()
            #delete reservations of book the user might have made
            cursorLib.execute("SELECT * FROM ReservedBooks WHERE ReserverLMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            results = cursorLib.fetchall()

            for rec in results :
                if ( rec[5] == 1 ) :	#if the reserved book has been returned
                	#delete log of books issue to the specified user
                    cursorLib.execute("SELECT * FROM BooksIssuedInPast WHERE IssueId=%s", (rec[2],))
                    t = cursorLib.fetchall()[0][1]
                    #update the catalogue to allow issue as reserver has been de registered
                    cursorLib.execute("UPDATE Catalogue SET Available = Available + 1  WHERE ISBN=%s", (t,))
                    dbLib.commit()
                else :		#if not returned then change reservation status to not reserved
                    cursorLib.execute("UPDATE CurrentlyIssuedBooks SET IsReserved = 0  WHERE IssueId=%s", (rec[2],))
                    dbLib.commit()
            #delete the reservation of books made by user to be de registered
            cursorLib.execute("DELETE FROM ReservedBooks WHERE ReserverLMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            dbLib.commit()
            #delete account of user 
            cursorr.execute("DELETE FROM NonFacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            db.commit()
            #update database and pop up message for successful de registration
            db.close()
            dbLib.close()
            messagebox.showinfo("DE-REGISTERATION SUCCESSFUL", "Member is successfully de-registered!")
            Librarian.ShowFirstPage()

        else :	#user is faculty member
            cursorr.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            if (len(cursorr.fetchall()) == 0) :		#LMCN entered is incorrect
                messagebox.showerror("", "Specified LMCN not found!")
                db.close()
                dbLib.close()
                return
            cursorr.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s AND Name=%s", 
                (ApplicationState.CurrentWidgets[2].get().strip(),ApplicationState.CurrentWidgets[4].get().strip()))
            if (len(cursorr.fetchall()) == 0) :		#account holder name of specified LMCN does not match with name entered
                messagebox.showerror("", "Incorrect name for the specified LMCN!")
                db.close()
                dbLib.close()
                return

            cursorr.execute("SELECT * FROM FacultyMembers WHERE LMCN=%s AND IssueCount=0", (ApplicationState.CurrentWidgets[2].get().strip(),))
            if (len(cursorr.fetchall()) == 0) :		#cannot  de register member who has not returned books
                messagebox.showerror("", "Specified member has not yet returned some books!")
                db.close()
                dbLib.close()
                return
            
            cursorLib.execute("SELECT * FROM BooksIssuedInPast WHERE IssuerLMCN=%s AND FinePaid=0", (ApplicationState.CurrentWidgets[2].get().strip(),))
            if (len(cursorLib.fetchall()) != 0) :		#cannot deregister member who has uncleared dues
                messagebox.showerror("", "Specified member has not yet cleared some penalties!")
                db.close()
                dbLib.close()
                return
            
            confirm = messagebox.askyesno("FATAL WARNING", """Deleting an account will permanently erase the history of all books issued in the past by that member, cancel all his/her reservations and forget all activity tracked by the notifications.\nAre you sure you want to de-register this member?""", icon='warning', default='no')
            if (not confirm) :		#ask for confirmation again before deleting account
                db.close()
                dbLib.close()
                ApplicationState.CurrentWidgets[2].delete(0, END)
                ApplicationState.CurrentWidgets[4].delete(0, END)
                return
            #delete messages to specified user
            cursorr.execute("DELETE FROM Messages WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            db.commit()
            #delete log of books issued by user
            cursorLib.execute("DELETE FROM BooksIssuedInPast WHERE IssuerLMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            dbLib.commit()
            #delete reservations made by  user
            cursorLib.execute("SELECT * FROM ReservedBooks WHERE ReserverLMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            results = cursorLib.fetchall()

            for rec in results :
                if ( rec[5] == 1 ) :	##if the reserved book has been returned
                	#delete log of books issue to the specified user
                    cursorLib.execute("SELECT * FROM BooksIssuedInPast WHERE IssueId=%s", (rec[2],))
                    t = cursorLib.fetchall()[0][1]
                    #update the catalogue to allow issue as reserver has been de registered
                    cursorLib.execute("UPDATE Catalogue SET Available = Available + 1  WHERE ISBN=%s", (t,))
                    dbLib.commit()
                else :		#if not returned then change reservation status to not reserved
                    cursorLib.execute("UPDATE CurrentlyIssuedBooks SET IsReserved = 0  WHERE IssueId=%s", (rec[2],))
                    dbLib.commit()
            #delete the reservation of books made by user to be de registered
            cursorLib.execute("DELETE FROM ReservedBooks WHERE ReserverLMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            dbLib.commit()
            #delete account of user
            cursorr.execute("DELETE FROM FacultyMembers WHERE LMCN=%s", (ApplicationState.CurrentWidgets[2].get().strip(),))
            db.commit()
            #update database and pop up message for successful de registration
            db.close()
            dbLib.close()
            messagebox.showinfo("DE-REGISTERATION SUCCESSFUL", "Member is successfully de-registered!")
            Librarian.ShowFirstPage()
            
    @staticmethod
    def ShowPopularityAnalysisPage ( ) :		#GUI to show popularity of  books
    	#unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading 
        head = Label(ApplicationState.Root, text="  □  BOOKS NOT ISSUED IN THE PAST YEARS", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=3, column=1, columnspan=32)
        #choice of analysis duration-
        typeMem = [ "1 Year" , "3 Years" , "5 Years" ]
        ApplicationState.ChooseMemberField = StringVar() 
        ApplicationState.ChooseMemberField.set( "CHOOSE TIME SPAN" ) 
        drop = OptionMenu( ApplicationState.Root , ApplicationState.ChooseMemberField , *typeMem )
        #drop down menu to chose time span
        helv36 = tkFont.Font(family='', size=22, weight="bold")
        drop.config(font=helv36)

        helv20 = tkFont.Font(family='', size=20)
        menu = ApplicationState.Root.nametowidget(drop.menuname)
        menu.config(font=helv20)


        initRow = 6
        height = 13

        #crete table to display popularity analysis
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=32, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #scroll bar to navigate the analysis table
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=34, rowspan=height, sticky=N+S+W)
        #columns of table showing analysis
        table['columns'] = ('ISBN', 'TITLE', 'AUTHOR', 'LANGUAGE', 'RACK NO.', 'TOTAL COPIES', 'LAST ISSUED ON', 'DATE OF ENTRY')
        table.column('#0', width=0, stretch=NO)
        table.column('ISBN', width=150, minwidth=25)
        table.column('TITLE', width=310, minwidth=25)
        table.column('AUTHOR', width=315, minwidth=25)
        table.column('LANGUAGE', width=125, minwidth=25)
        table.column('RACK NO.', width=95, minwidth=25)
        table.column('TOTAL COPIES', width=87, minwidth=25)
        table.column('LAST ISSUED ON', width=170, minwidth=25)
        table.column('DATE OF ENTRY', width=170, minwidth=25)
        #column headings of the table
        table.heading('#0', text='')
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('TITLE', text='TITLE', anchor=CENTER)
        table.heading('AUTHOR', text='AUTHOR(s)', anchor=CENTER)
        table.heading('LANGUAGE', text='LANGUAGE', anchor=CENTER)
        table.heading('RACK NO.', text='RACK NO.', anchor=CENTER)
        table.heading('TOTAL COPIES', text='TOTAL', anchor=CENTER)
        table.heading('LAST ISSUED ON', text='LAST ISSUED ON', anchor=CENTER)
        table.heading('DATE OF ENTRY', text='DATE OF ENTRY', anchor=CENTER)
        #placement of table
        ApplicationState.Root.grid_rowconfigure(initRow, minsize=4)
        table.grid(row=initRow+1, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)

        #show button to run analysis
        show = Button(ApplicationState.Root, text="SHOW RECORDS", bg='white',  font=('',20,'bold'), command = Librarian.ShowStatistics)
        #go back button to return ot  Librarian Dash board
        goBack = Button(ApplicationState.Root, text="GO BACK", bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        #placement of buttons
        ApplicationState.Root.grid_rowconfigure(4, minsize=10)
        drop.grid(row=5, column=12, columnspan=10, sticky=W+E)
        goBack.grid(row=17, column=4, columnspan=10, sticky=W+E)
        show.grid(row=17, column=21, columnspan=10, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [ treeFrame , scrollbar , head , drop , show , goBack , table ]

    @staticmethod
    def ShowStatistics ( ) :		#backend to analyse book popularity
    	#check if time span of analysis entered
        if ( ApplicationState.ChooseMemberField.get() == "CHOOSE TIME SPAN" ) :
            messagebox.showerror('ERROR', 'Time Span not specified!')
            return

        span = eval(ApplicationState.ChooseMemberField.get()[0])
        #connnect  to database Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #unmap previous widgets
        for rec in ApplicationState.CurrentWidgets[-1].get_children() :
            ApplicationState.CurrentWidgets[-1].delete(rec)
        #do analysis of all books from catalogue -
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM Catalogue")
        results = cursorr.fetchall()

        i = 1

        for rec in results :
            last = None
            #rec[7] is LatIssueDate attribute
            if ( rec[7] == "00/00/0000" ) :	#if book has not been issued yet	
                last = datetime.strptime(rec[8], '%d/%m/%Y')	#check entryDate of book in the library
            else: last = datetime.strptime(rec[7], '%d/%m/%Y')	#else use the LasrIssueDate itself
            try :
                delay = (datetime.now()-last).days / 365	 
            except :
                continue
            if ( delay < span ) :	#analyse for time period specified
                continue
            if ( rec[7] != "00/00/0000" ) :	#if book has been issued before mention last issue date otherwise leave section as NA
                ApplicationState.CurrentWidgets[-1].insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[7], rec[8]))
            else :
                ApplicationState.CurrentWidgets[-1].insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], "N.A.", rec[8]))
            
            i += 1
        
        db.close()
        if ( i == 1 ) :	#if no relevant books to be analysed was found -
            messagebox.showinfo("", "No relevant records discovered!")

    @staticmethod
    def ShowCatalogue ( ) :		#GUI to display catalogue
    	#connect ot Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #fetch data from catalogue table in database Library
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM Catalogue")
        results = cursorr.fetchall()
        #unmap all previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  CATALOGUE", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)

        initRow = 6

        height = 13
        #create table to display catalogue
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        #implement scroll bar for navigating catalogue table
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=32, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #placement of scroll bar
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #make relevant columns in table
        table['columns'] = ('ISBN', 'TITLE', 'AUTHOR', 'LANGUAGE', 'RACK NO.', 'TOTAL COPIES', 'AVAILABLE COPIES')
        table.column('#0', width=0, stretch=NO)
        table.column('ISBN', width=155, minwidth=25)
        table.column('TITLE', width=370, minwidth=25)
        table.column('AUTHOR', width=360, minwidth=25)
        table.column('LANGUAGE', width=125, minwidth=25)
        table.column('RACK NO.', width=95, minwidth=25)
        table.column('TOTAL COPIES', width=130, minwidth=25)
        table.column('AVAILABLE COPIES', width=130, minwidth=25)
        #column headings-
        table.heading('#0', text='')
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('TITLE', text='TITLE', anchor=CENTER)
        table.heading('AUTHOR', text='AUTHOR(s)', anchor=CENTER)
        table.heading('LANGUAGE', text='LANGUAGE', anchor=CENTER)
        table.heading('RACK NO.', text='RACK NO.', anchor=CENTER)
        table.heading('TOTAL COPIES', text='TOTAL', anchor=CENTER)
        table.heading('AVAILABLE COPIES', text='AVAILABLE', anchor=CENTER)
        #the catalogue sorted according to title
        results = sorted(results, key=lambda x: x[1])
        #insert books in rows of GUI Catalogue table
        i = 0
        for rec in results :
            table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6]))
            i += 1
        #close database
        db.close()
        #placement of table centrally
        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)
        #design and placement of go back buttton to return to Librarian dashboard
        ApplicationState.Root.grid_rowconfigure(17, minsize=35)
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        goBack.grid(row=17, column=14, columnspan=7, sticky=W+E)
        #widget List
        ApplicationState.CurrentWidgets = [head, treeFrame, table, goBack, scrollbar]

    @staticmethod
    def ShowCurrentlyIssuedBooks ( ) :		#GUI to display currently issued books
    	#connect to Library database
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #import data of currently  issued books
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM CurrentlyIssuedBooks")
        results = cursorr.fetchall()
        #if no books are currently issued show messge 
        if ( len(results) == 0 ) :
            messagebox.showinfo("", "No currently issued books found!")
            db.close()
            return
        #unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  CURRENTLY ISSUED BOOKS", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)

        initRow = 6

        height = 13
        #create table to display CurrentlyIssuedBooks
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=32, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #scrollbar design and placement to navigate
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #relevant  columns of table-
        table['columns'] = ('ISSUE ID', 'ISBN', 'ISSUER\'S LMCN', 'DATE OF ISSUE', 'DUE DATE OF RETURN', 'IS RESERVED?')
        table.column('#0', width=0, stretch=NO)
        table.column('ISSUE ID', width=155, minwidth=25)
        table.column('ISBN', width=250, minwidth=25)
        table.column('ISSUER\'S LMCN', width=240, minwidth=25)
        table.column('DATE OF ISSUE', width=170, minwidth=25)
        table.column('DUE DATE OF RETURN', width=210, minwidth=25)
        table.column('IS RESERVED?', width=170, minwidth=25)
        #heading of column
        table.heading('#0', text='')
        table.heading('ISSUE ID', text='ISSUE ID', anchor=CENTER)
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('ISSUER\'S LMCN', text='ISSUER\'S LMCN', anchor=CENTER)
        table.heading('DATE OF ISSUE', text='DATE OF ISSUE', anchor=CENTER)
        table.heading('DUE DATE OF RETURN', text='DUE DATE OF RETURN', anchor=CENTER)
        table.heading('IS RESERVED?', text='IS RESERVED?', anchor=CENTER)

        i = 0
        for rec in results :
            if ( rec[5] == 0 ) :	#check if book has been reserved
                table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], "NO"))
            else :
                table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], "YES"))
            i += 1
        
        db.close()
        #placement of GUI table
        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)
        #design and placement of go back button to return to Librarians dashboard
        ApplicationState.Root.grid_rowconfigure(17, minsize=35)
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        goBack.grid(row=17, column=14, columnspan=7, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [head, treeFrame, table, goBack, scrollbar]

    @staticmethod
    def ShowBooksIssuedInPast ( ) :		#GUI to show book issue history
    	#connect to datbase Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #import date from BooksIssuedInPast table
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM BooksIssuedInPast")
        results = cursorr.fetchall()
        #if no such books found show message-
        if ( len(results) == 0 ) :
            messagebox.showinfo("", "No books were issued in past!")
            db.close()
            return
        #unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  BOOKS ISSUED IN PAST", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)

        initRow = 6

        height = 13
        #create table to display BooksIssuedInPast
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=32, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #design and implement  scrollbar for navigation
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #create table columns
        table['columns'] = ('ISSUE ID', 'ISBN', 'ISSUER\'S LMCN', 'DATE OF ISSUE', 'DATE OF RETURN', 'OVERDUE DAYS', 'PENALTY', 'IS FINE PAID?')
        table.column('#0', width=0, stretch=NO)
        table.column('ISSUE ID', width=150, minwidth=25)
        table.column('ISBN', width=155, minwidth=25)
        table.column('ISSUER\'S LMCN', width=220, minwidth=25)
        table.column('DATE OF ISSUE', width=170, minwidth=25)
        table.column('DATE OF RETURN', width=210, minwidth=25)
        table.column('OVERDUE DAYS', width=170, minwidth=25)
        table.column('PENALTY', width=170, minwidth=25)
        table.column('IS FINE PAID?', width=165, minwidth=25)
        #give headings to columns
        table.heading('#0', text='')
        table.heading('ISSUE ID', text='ISSUE ID', anchor=CENTER)
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('ISSUER\'S LMCN', text='ISSUER\'S LMCN', anchor=CENTER)
        table.heading('DATE OF ISSUE', text='DATE OF ISSUE', anchor=CENTER)
        table.heading('DATE OF RETURN', text='DATE OF RETURN', anchor=CENTER)
        table.heading('OVERDUE DAYS', text='OVERDUE DAYS', anchor=CENTER)
        table.heading('PENALTY', text='PENALTY', anchor=CENTER)
        table.heading('IS FINE PAID?', text='IS FINE PAID?', anchor=CENTER)
        #enter data into rows
        i = 0
        for rec in results :
            if ( rec[7] == 0 ) :		#check reservation status
                table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6], "NO"))
            else :
                table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6], "YES"))
            i += 1
        
        db.close()
        #placement of table
        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)
        #design and implementation of go back button
        ApplicationState.Root.grid_rowconfigure(17, minsize=35)
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        goBack.grid(row=17, column=14, columnspan=7, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [head, treeFrame, table, goBack, scrollbar]

    @staticmethod
    def ShowOverDueBooks ( ) :		##GUI to show books which are overdue
    	#connect to database Library
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Library"
        )
        #import data from CurrentlyissuedBooks
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM CurrentlyIssuedBooks")
        results = cursorr.fetchall()
        #if no issued books then there are no overdue books
        if ( len(results) == 0 ) :
            messagebox.showinfo("", "No over-due books found!")
            db.close()
            return
        #unmap previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  OVER-DUE ISSUED BOOKS", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=4, column=1, columnspan=32)
        ApplicationState.Root.grid_rowconfigure(5, minsize=35)

        initRow = 6

        height = 13
        #create table
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=32, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #implement scroll bar for navigation
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #form columns in table
        table['columns'] = ('ISSUE ID', 'ISBN', 'ISSUER\'S LMCN', 'DATE OF ISSUE', 'DUE DATE OF RETURN', 'PENALTY')
        table.column('#0', width=0, stretch=NO)
        table.column('ISSUE ID', width=155, minwidth=25)
        table.column('ISBN', width=240, minwidth=25)
        table.column('ISSUER\'S LMCN', width=240, minwidth=25)
        table.column('DATE OF ISSUE', width=170, minwidth=25)
        table.column('DUE DATE OF RETURN', width=220, minwidth=25)
        table.column('PENALTY', width=170, minwidth=25)
        #give names to columns
        table.heading('#0', text='')
        table.heading('ISSUE ID', text='ISSUE ID', anchor=CENTER)
        table.heading('ISBN', text='ISBN', anchor=CENTER)
        table.heading('ISSUER\'S LMCN', text='ISSUER\'S LMCN', anchor=CENTER)
        table.heading('DATE OF ISSUE', text='DATE OF ISSUE', anchor=CENTER)
        table.heading('DUE DATE OF RETURN', text='DUE DATE OF RETURN', anchor=CENTER)
        table.heading('PENALTY', text='PENALTY', anchor=CENTER)
        #list all overdue books
        i = 0
        for rec in results :
            dor = datetime.strptime(rec[4], '%d/%m/%Y')
            delay = (datetime.now()-dor).days
            if ( delay <= 0 ) :	#check if book is overdue
                continue
            table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], delay*ApplicationDesign.Penalty))
            i += 1
        
        db.close()
        #placement of table
        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)
        #design and placement for go back button to return to dashboard
        ApplicationState.Root.grid_rowconfigure(17, minsize=35)
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        goBack.grid(row=17, column=14, columnspan=7, sticky=W+E)
        #widgets list
        ApplicationState.CurrentWidgets = [head, treeFrame, table, goBack, scrollbar]

    @staticmethod
    def ShowMembersPage ( ) :		#GUI to list all members-
    	#connect to database Accounts
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #import data of both faculty and nonfaculty members
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM NonFacultyMembers")
        results1 = cursorr.fetchall()
        cursorr.execute("SELECT * FROM FacultyMembers")
        results2 = cursorr.fetchall()
        #unmap all previous widgets
        for w in ApplicationState.CurrentWidgets :
            w.grid_forget()
        #design and placement of heading
        gap = 35
        ApplicationState.Root.grid_rowconfigure(2, minsize=gap)
        ApplicationState.Root.grid_rowconfigure(3, minsize=gap)
        head = Label(ApplicationState.Root, text="  □  LIBRARY MEMBERS", fg="#FF8C00", bg="white", width=60, font=('',29,'bold'))
        head.grid(row=3, column=1, columnspan=32)
        ApplicationState.Root.grid_rowconfigure(4, minsize=25)

        initRow = 5

        height = 13
        #create table
        style = ttk.Style()
        style.configure('Treeview', rowheight=25, font=('Calibri', 14), relief=RAISED)
        style.configure("Treeview.Heading", font=('Calibri', 16,'bold'))
        
        treeFrame = Frame(ApplicationState.Root)
        treeFrame.grid(row=initRow, column=1, columnspan=32, rowspan=height, sticky=N)
        scrollbar = Scrollbar(treeFrame, orient = VERTICAL)
        table = ttk.Treeview(treeFrame, yscrollcommand = scrollbar.set, height=height)
        #design and placement of scroll bar to navigate
        scrollbar.config(command=table.yview)
        scrollbar.grid(row=initRow, column=35, rowspan=height, sticky=N+S+W)
        #form relevant columns
        table['columns'] = ('LMCN', 'INSTITUTE ID', 'NAME', 'DATE OF BIRTH', 'DATE OF REGISTRATION', 'ISSUE COUNT')
        table.column('#0', width=0, stretch=NO)
        table.column('LMCN', width=150, minwidth=25)
        table.column('INSTITUTE ID', width=155, minwidth=25)
        table.column('NAME', width=270, minwidth=25)
        table.column('DATE OF BIRTH', width=170, minwidth=25)
        table.column('DATE OF REGISTRATION', width=235, minwidth=25)
        table.column('ISSUE COUNT', width=150, minwidth=25)
        #give headings to columns
        table.heading('#0', text='')
        table.heading('LMCN', text='LMCN', anchor=CENTER)
        table.heading('INSTITUTE ID', text='INSTITUTE ID', anchor=CENTER)
        table.heading('NAME', text='NAME', anchor=CENTER)
        table.heading('DATE OF BIRTH', text='DATE OF BIRTH', anchor=CENTER)
        table.heading('DATE OF REGISTRATION', text='DATE OF REGISTRATION', anchor=CENTER)
        table.heading('ISSUE COUNT', text='ISSUE COUNT', anchor=CENTER)
        #enter data in rows of table
        i = 0
        for rec in results1 :	#list of NonFacultyMembers
            table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5]))
            i += 1
        for rec in results2 :	#list of FacultyMembers
            table.insert(parent='', index='end', iid=i, text="0", values=(rec[0], rec[6], rec[1], rec[2], rec[3], rec[4]))
            i += 1
        
        db.close()
        #placement of table on frame
        table.grid(row=initRow, column=1, columnspan=34, rowspan=height, padx=5, pady=5, sticky=N+S)
        #design and placement of go back button to return to Librarian dashboard
        ApplicationState.Root.grid_rowconfigure(17, minsize=35)
        goBack = Button(ApplicationState.Root, text='GO BACK', bg='white',  font=('',20,'bold'), command = Librarian.ShowFirstPage)
        goBack.grid(row=17, column=14, columnspan=7, sticky=W+E)
        #widget list
        ApplicationState.CurrentWidgets = [head, treeFrame, table, goBack, scrollbar]

    @staticmethod
    def ChangePassword ( ) :		#frame to change password
        if ( ApplicationState.OldPasswordField.get() == "" ) :
            messagebox.showerror("", "Old password not specified!")
            return
        if ( ApplicationState.NewPasswordField.get() == "" ) :
            messagebox.showerror("", "New password not specified!")
            return
        if ( ApplicationState.ConfirmPasswordField.get() == "" ) :
            messagebox.showerror("", "Confirmation password not specified!")
            return
        
    	#connet to database Accounts
        db = mysql.connector.connect(
            host="localhost",
            user=ApplicationDesign.DatabaseUser,
            password=ApplicationDesign.Password,
            database="Accounts"
        )
        #enter into database element matching credentials to presently logged in Librarian
        cursorr = db.cursor(buffered=True)
        cursorr.execute("SELECT * FROM Administrators WHERE ID=%s", (ApplicationState.CurrentUser._Individual__id,))
        pw = cursorr.fetchall()[0][4]

        #check if old password matches 
        if ( md5(ApplicationState.OldPasswordField.get().encode()).hexdigest() != pw ) :
            messagebox.showerror('ERROR', 'Incorrect Old Password!')
            db.close()
            return

        if ( ApplicationState.NewPasswordField.get().strip() == "" ) :
            messagebox.showerror('ERROR', 'New password has no characters !')
            db.close()
            return
        
        if ( len(ApplicationState.NewPasswordField.get()) < 7 ) :
            messagebox.showerror('ERROR', 'Password must be atleast 7 characters long')
            db.close()
            return

        #check if the new password entered twice match
        if ( ApplicationState.NewPasswordField.get() != ApplicationState.ConfirmPasswordField.get() ) :
            messagebox.showerror('ERROR', 'New and Confirm Passwords do not match !')
            db.close()
            return
        #set new password in md5 encryption
        sql = "UPDATE Administrators SET password = md5(%s) WHERE ID = %s"
        cursorr.execute(sql, (ApplicationState.NewPasswordField.get(), ApplicationState.CurrentUser._Individual__id))
        #upadte and close database
        db.commit()
        db.close()
        ApplicationState.OldPasswordField.set("")
        ApplicationState.NewPasswordField.set("")
        ApplicationState.ConfirmPasswordField.set("")
        Librarian.ShowFirstPage()	#return to login page


ApplicationState.Root = Tk()	#Application  Page
ApplicationState.Root.title('developed by CODING CONNOISSEURS')
ApplicationState.Root.configure( bg = ApplicationDesign.BackgroundColor )

ApplicationState.CheckExpiredReservations()		#ckeck reservations not issued for more than 7 days

bg = PhotoImage(file='')	#background picture
scale_w = 6
scale_h = 3
bg.zoom(scale_w, scale_h)
canvas = Canvas(ApplicationState.Root, width=1530, height=749, bg=ApplicationDesign.Theme)
canvas.grid(row=1, column=0, rowspan=20, columnspan=34, sticky=N+S+W)
canvas.create_image(0,0, image=bg, anchor="nw")

ApplicationState.OldPasswordField = StringVar()
ApplicationState.NewPasswordField = StringVar()
ApplicationState.ConfirmPasswordField = StringVar()
ApplicationState.ChooseMemberField = StringVar()

ApplicationState.ShowHomePage()
ApplicationState.Root.mainloop()

