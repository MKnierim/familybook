kniebook.de
=========================

Description
-------------------------
My personal facebook clone just for my family to communicate news and document family events without publishing information to the general public.

Feature List
-------------------------

### Critical functionality
* User database with functionality for each user to personalize change password, email and design
* Calendar database and event construction/editing for users

### Additional functionality
* Error handling (401, 404, 500)
* New user registration in admin area
* Seasonal color schemes

To Do
-------------------------
* Implement independent blogging function
* Implement general error handling function, not just specific to 401,404, 500. [See Documentation](http://webapp-improved.appspot.com/guide/exceptions.html#guide-exceptions)
* Refactor Code in smaller modules to facilitate reuse in later projects

Known Bugs
-------------------------
* Editing an event creates a new copy of the event rather than updating the observed event. Other than that, the algorithm edit_date() should work just fine for creating as well as editing an event.
