This was the code for my first Flask app, which was a website for my resume.
It was deployed on heroku.
However, it's not active anymore because I didn't want to pay for Amazon S3's storage,
after the end of the free trial.

Main features
- Uses SQL database to dynamically add and remove pages (don't need to change the code)
- Stores images on Amazon S3 (including letting me upload and download).
- Has a login system so only I am able to make changes.

------------------------------------------------------------------------------------

Setup instructions
To set it up do the following

Setting up database
1) navigate inside 'Sarahs_webpage' using command line
2) 'flask db init' to create migrations directory
3) 'flask db migrate -m "message here"'to create the db migrations.
4a) At this stage you can just push to heroku, and then do 'heroku run flask db upgrade' assuming you set up the git remote.
4b) If you are setting it up locally then do 'flask db upgrade'

5) don't forget to set the environment variables for:
	S3_BUCKET = the bucket that the pictures will be uploaded to.
	S3_KEY = the key that you got from AWS S3
	S3_SECRET = the secret you got from AWS S3
	APP_SECRET_KEY = the secret key for the app. Literally just put anything you want but you can also do os.urandom(32) and paste the result in.
	
	really important note: you need to set the bucket so that
	"Block public access to buckets and objects granted through new ACLs" is OFF
	"Block public access to buckets and objects granted through any ACLs" is OFF
	this is so the files you upload to the bucket will be public-readable.
	If you don't turn this off and try to upload a publicly visible file it will give you an access denied error.

6) To create an account on the heroku app you need to do the following:
	Set up the environmenet vars on Heroku:
		CREATE_ACC_ID = basically a username kind of thing
		CREATE_ACC_PW_HASH = hashed password (use werkzeug.security to hash it. There's a script in the main folder that does it for you)
		
	Only once these are set can you create an account on the site. This is to stop random people from making accounts.
	Also you can delete these 2 environment variables afterwards. It's just for making an account.

7) I may have hard-coded the source for the background image, stylesheet, and the black rectangle on the home page (when no image is uploaded).
	At some point just change this to use environment variables, or at least the config file.
