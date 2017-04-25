# grabagram
Non-API Image and metadata archiving tools for well known user generated content
site. Images are selected using a tag, but the code can be easily adapted
to do profiles or locations.
## requirements
Tested with
* selenium 3.4
* geckodriver 0.16
* firefox 53.0
## instructions
Edit tag variable on line 36 to target a tag. Changing base URL on line 39 will
allow you to archive locations or profiles as the page layout is the same.
Images will be stored in a folder in the CWD that will be created with the tag name.
A CSV file will be created in the same directory with some of the meta data. NB
This code relies on CSS selectors so will get broken by some future update of the
target site. To run the code just type 'python grabagram.py' from the terminal.
