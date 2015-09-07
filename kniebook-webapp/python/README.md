kniebook.de
=========================

Description
-------------------------
My personal facebook clone just for my family to communicate news and document family events without publishing information to the general public.

Feature List
-------------------------

### Main features
* Date-List (responsive display of upcoming dates)

### Critical functionality
* User database with functionality for each user to personalize change password, email and design
* Calendar database and event construction/editing for users

### Additional functionality
* Error handling (401, 404, 500)
* New user registration in admin area
* Seasonal color schemes

To Do
-------------------------
* Implement commenting function on events
* Implement independent blogging function
* Implement general error handling function, not just specific to 401,404, 500. [See Documentation](http://webapp-improved.appspot.com/guide/exceptions.html#guide-exceptions)
* Refactor Code in smaller modules to facilitate reuse in later projects
* Set locale on date-list to correctly display german month names
* Fix display problem with date-list when a user can see the editing buttons (disrupted layout because space is not reserved in cases when the user can edit and when he cannot)
* Fix display of month on top of dates for different pages (i.e. termine.html/termine_archiv.html/main.html)

Known Bugs
-------------------------

