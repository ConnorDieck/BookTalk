# BookTalk
## First Capstone for Springboard: Software Engineering Track

### App Description

BookTalk enables users to join and create book clubs in order to organize meetings for discussion. Admins and moderators for clubs have the ability add books to the club's "shelf" as well as to organize meetings. Once a meeting is created, any member may visit the meeting page to add notes they'd like to discuss during the meeting.

### Associated Links:

* Link to site: [https://connor-booktalk.herokuapp.com/](https://connor-booktalk.herokuapp.com/)
* API Link: [https://www.goodreads.com/api](https://connor-booktalk.herokuapp.com/)

### Standard User Flow

After registering an account, users will see the main navbar, which contains links to the list of existing clubs, the books in BookTalk's library, the user's profile, and a link to log out of the site. 

Upon visiting the "Clubs" page, users can choose to join an existing club or create a new one. Once a user is a member of a club, they will be given access to see books the club is currently reading. If the user is an admin or moderator (admin privileges are automatically granted to the creator of a club, and any admin or moderator may promote other members up to the level of clearance the admin/moderator possesses), they may also add books to the club and create meetings. 

When adding a book to a club, users may select from BookTalk's internal library. If BookTalk doesn't have the desired book, the user may add a book to BookTalk's library through the search page. On this page, users may search a book by its title or author and BookTalk will connect to OpenLibrary's API and present a list of best matches. If the selected match has an associated ISBN, the user will be taken to a details page for the book where they may add it to BookTalk's library.

If a user no longer wishes to be a member of a club, they may cancel their membership by selecting the "Leave Club" button located on the bottom of the club page. If an admin wishes to leave a club that they are the only admin for, they will be prevented from doing so until they promote another member to admin. 


### App Features
* **Users**
	* Users of BookTalk can add personal details in their bio, mark their favorite books, and create and join clubs.
* **Clubs**
	* Clubs are the main vehicle for users to connect on BookTalk. Each club has its own members, books, and meetings. Clubs are monitored by Admins and Moderators – each have permissions to add books to the club, promote other users, and create meetings.
* **Books**
	* Books are added to BookTalk from the OpenLibrary API. Each book will include information about its title, author, publishing date, and number of pages (if said information is available from the API). Books can be added to a club, where they can be marked as unread, currently reading, or finished. 
* **Meetings**
	* Admins and moderators of any club may schedule a meeting to discuss a book the club has in its shelves. If included, meetings can link users to meeting links created by third-party apps, such as Google Meets or Zoom. Users may also add notes that they would like to discuss in a given meeting.
* **Notes**
	* Members of a club can add notes to call out items they would like to discuss in an upcoming meeting. Notes are associated with the given meeting and creating user. 

###Technology Stack

The backend for BookTalk was written in Python using a Flask framework. BookTalk's database was created using SQLAlchemy. HTML pages use Jinja templating and are styled using BootStrap and in-house CSS. Forms were created using WTForms.



