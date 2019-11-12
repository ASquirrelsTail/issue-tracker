# Issue Tracker

Full Stack Frameworks With Django Milestone Project - Code Institute

Wish Machine - *Where Dreams Come True!*

Wish machine is an issue tracker for the fictional free to play video game Unicorn Attractor. It allows users to submit feature requests and bug reports for the developers to address.

Users can purchase credits for real money, which can be spent on feature requests to guide and help fund the development of the game.

[![Build Status](https://travis-ci.org/ASquirrelsTail/issue-tracker.svg?branch=master)](https://travis-ci.org/ASquirrelsTail/issue-tracker)

## [UX Process](https://github.com/ASquirrelsTail/issue-tracker/blob/master/preprod/ux.md)

A full breakdown of the UX process can be found [here](https://github.com/ASquirrelsTail/issue-tracker/blob/master/preprod/ux.md).

## Features

### Existing Features

#### All Users

- Anonymous users have access to the home page, which shows general stats on Unicorn Attractor and links to popular tickets.
- All users can view approved tickets, and using the ticket list filter and sort them based on type, tags and popularity.
- A roadmap, showing what features have been implemented, and bugs fixed, as well as what's coming soon is available to all users.

#### Registered Users

- All registered users can submit bug reports and feature requests, and are able to attach a picture to help illustrate them.
- Registered users can comment on tickets, and reply to the comments of other users.
- Users can vote once for bug reports.
- Users can purchase credits for real money, which can be spent on voting as many times as they like for feature requests.
- Users can request refunds for recent credit purchases, if they are within 90 days, and have yet to spend them.

#### Admin Features

- A staff or super user with access to the Admin backend can assign permissions to users, or add them to groups to delegate responsibilites. For example Moderators can be given powers to edit and delete the comments of other users, while Producers can be given access to stats about bug reports and feature requests to help them make the right decisions.
- Admin users with the appropriate permissions can edit and delete the tickets and comments of other users.
- Users with the required permissions can approve new bug reports and feature requests, and subsequently mark them as "Doing" and "Done"
- A stats dashboard accessible to users with required permissions shows a breakdown of recent engagement with the site, whichc an be filtered by date.
- The stats dashboard also updates admin users of tickets awaiting approval, and shows the most popular bugs and features.
- A transactions stats page for admins with the required permissions shows sales and refunds, filterable by date.

### Features Left to Implement

- A blog for developers to keep users up to date on the latest changes.
- Text search, to find a particular bug or feature.
- Duplication checking, to help users and admins prevent multiple requests for the same things, and the ability to merge tickets when they do.
- A notifications system, to let user know when reports or requests they've made or voted on are being actioned.

## Technologies Used

- HTML5
- CSS3
- JavaScript
- Python3
- [Bootstrap v4.1.3](https://getbootstrap.com/)
    -  Bootstrap was used as a base for styling the site, providing responsive layout, nav-bar, collapsing elements and buttons. Additional CSS was used to further customise the look and feel of the site.
- [Google Fonts](https://fonts.google.com/)
    -  Google Fonts was used to make sure users could access required fonts, Nunito and Montserrat.
- [Fontawesome v5.5.0](https://fontawesome.com/)
    -  The free version of Fontawesome webfonts was used to provide icons for the site.
- [JQuery v3.3.1](https://jquery.com/)
    - JQuery is used for DOM manipulation, some AJAX functions and general simplification of code.
- [JQuery UI v1.12.1](https://jqueryui.com/) 
	- A custom build of JQuery UI is used to create a datepicker for selecting date ranges on the stats pages.
- [dc.js v2.1.8](http://dc-js.github.io/dc.js/)
    - dc.js creates the charts used in the dashboard, it uses [Crossfilter v1.3.12](http://square.github.io/crossfilter/) for sorting and filtering data, and [D3.js v3.15.17](https://d3js.org/) to plot them.
- [Django 1.11.21](https://www.djangoproject.com/)
	- The Django framework serves the site over HTTP as well as handling user authentication and providing a powerful ORM for data storage and access.
- [Django Bootstrap4 0.0.8](https://pypi.org/project/django-bootstrap4/)
	- Django Bootstrap 4 provides Bootstrap 4 integration for Django forms in templates.
- [Django Database URL 0.5.0](https://pypi.org/project/dj-database-url/)
	- This utility is used to connect a provisioned database to the Django project using a database url.
- [PostgreSQL](https://www.postgresql.org/)
	- A PostgreSQL database provides data storage for the project. The one used in the deployed version of the site is provisioned through Heroku.
- [Pillow](https://pillow.readthedocs.io/en/stable/)
	- The updated version of the Python Imaging Library is used by Django as part of the image upload process.
- [AWS S3](https://aws.amazon.com/s3/)
	- Amazon AWS S3 storage was used to provide persistent storage for static files and user images.
	- [Django Storages 1.7.1](https://pypi.org/project/django-storages/) provides the storages backend using [Boto3 python API](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) to interface with the S3 service.
- [Gunicorn](https://gunicorn.org/)
	- Gunicorn is a WSGI Server that serves the app over HTTP and is used for the deployment to Heroku.

### Tools

- [Sublime Text 3.2.1](https://www.sublimetext.com/)
	- Sublime text was used to write the code for the site.
	- [Emmet](https://emmet.io/) package was used to speed up davelopment.
	- [HTML-CSS-JS Prettify](https://packagecontrol.io/packages/HTML-CSS-JS%20Prettify) package was used to prettify code layout.
	- [Anaconda](http://damnwidget.github.io/anaconda/) package was used as a PEP8 linter to write neater error free code.
	- [ESLint](https://eslint.org/) was used via the [ESLint package](https://packagecontrol.io/packages/ESLint) as a javascript linter.
- [GitHub](https://github.com/)
	- Git was used for version control, and GitHub was used for remote storage of repositories.
- [Travis CI](https://travis-ci.org/)
	- Continuous integration testing is carried out by Travis CI whenever a new commit is pushed to the GitHub repo.
-[Heroku](https://www.heroku.com/)
	- The site has been deployed through Heroku.
- [GIMP 2.10.8](https://www.gimp.org/)
	- GIMP 2 was used for image editing.
- [Inkscape](https://inkscape.org/)
	- Inkscape was used to create the logo.
- [CSS Gradient](https://cssgradient.io/)
	- The CSS Gradient Generator was used to quickly test and build css gradients to use on the site for backgrounds and buttons.

## Deployment

Code snippets that accompany the following instructions are for Linux systems, but commands are similar on other operating systems. Commands are run from the base directory, the one containing the manage.py file.

To deploy the project you will require the project files, create a directory and download or clone the project's GitHub Repository by running the following command:
```
$ git clone https://github.com/ASquirrelsTail/cookbook.git
```

Before completing deployment of the project the PostgreSQL database, Amazon AWS S3 and Stripe need setting up.

### Database Setup

While the site will work with an SQLite3 database, some features will be missing as SQLite doesn't support some operations used in the project. For deployment you will want to connect a database such as PostgeSQL to the project, and will require a database URL to do so. The database URL needs to be saved as an environment variable called DATABASE_URL. If you don't declare the variable the default SQLite3 database will be used.

For the deployment of this project I provisioned a PostgreSQL database through Heroku.

### Amazon AWS S3

To safely store user uploads, and speed up the loading of static files the project utilises the Amazon AWS S3 cloud storage service. The project will run without it, and simply not declaring the AWS_ACCESS_KEY_ID environment variable means that uploads and static files will be stored locally in the project directory. However, this is an additional load on the Django server to serve numerous large images and files, and where the project is deployed to a service like Heroku uploaded files will be lost when the file systems are replaced due to its [ephemeral file system](https://devcenter.heroku.com/articles/dynos#ephemeral-filesystem).

If you don't already have one, you can create a [free account on Amazon AWS](https://aws.amazon.com/). Log in to your AWS account, and select S3 from the list of services. If you don't already have S3 set up follow the instructions, you will be informed by email when the service is ready to go.

Create a new bucket, give it a unique name, and select a region. Using the same region your server will speed things up slightly. The name of this bucket will be used later as an environment variable.

You'll need to set permissions so anonymous users can have read access to your newly created bucket. Select your new bucket, click the permissions tab and select bucket policy. Set the following policy as per [Amazon's example](https://docs.aws.amazon.com/AmazonS3/latest/dev/example-bucket-policies.html#example-bucket-policies-use-case-2). Granting public access will come with a warning, but as it's only read access and these are only static files and user uploads you don't need to worry.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::example-bucket/*"
        }
    ]
}
```

You can test this by returning to the bucket's overview tab, uploading a file and selecting the file and following its Object URL. If everything has worked it should take you to the uploaded file. If not you will get permission denied notice.

With the bucket set up all that is left is to set up a user for the app to access S3. Select IAM from the list of services in AWS and navigate to the users section and select + New User.

Give the user a name, and select Programatic Access. On the next screen select create group, give the group a name, search the policy list for S3 and select AmazonS3FullAccess and click create group. Follow the remaining steps until the process is complete and you will be given an Access ID Key and a Secret Access Key, make a note of these as you will need them later to use as environment variables for setting up the app. If you lose your secret key you can create a new one at a later time by selecting the user in the IAM Service and clicking the Security Credentials tab.

To get S3 working with the project requries the AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables to be set. Finally, to upload the static files to S3 run the collect static command:
```
$ python3 manage.py collectstatic
```

#### Stripe Set Up

Payments for the project are handled by Stripe, which takes care of PCI compliance, and implements strong customer authentication to meet EU regulations. In order to take payments we require a Stripe API key, which you can get by signing up on their [site](https://stripe.com/). To actually take payments, there are some further hoops to jump through to activate the account, but we only need a test API key which you'll be shown when you log in.

Use the publishable API key as environment variable STRIPE_PUBLISHABLE, and the secret key as STRIPE_SECRET.

Next we need to set up a webhook, to inform us when a payment intent has succeeded so we can credit the user's account and let them know. On the stripe dashboard select developers, then webhooks, and click add endpoint. Direct the webhook to the url of your deployment followed by "/credits/webhook/" and select the payment_intent.succeeded event.

On this page you'll be given a webhook signing secret key, to verify it is Stripe calling the webhook. Set this as the STRIPE_WEBHOOK_SECRET environment variable, and you're ready to go.

### Local Deployment

After downloading the project, set up the database, S3 and Stripe and setting the associated environment variables by following the instructions above. Ommiting them will not stop the site from working, but some functionality will be missing. You'll also need to set a secret key environment variable called SECRET_KEY.

Next install the required python modules from the requirements.txt file using pip3.
```
$ sudo pip3 install -r requirements.txt
```

Next complete the database setup by running a migration:
```
$ python3 manage.py migrate
```

You will want to set up a superuser to access the Admin panel, do that with the following command and enter your desired credentials:
```
$ python3 manage.py createsuperuser
```

Finally, launch the server by running:
```
$ python3 manage.py runserver
```

You can now access the site at http://localhost:8000/. To specify a different port if 8000 is already in use you can append the port number to the command.

### Remote Deployment

The site is deployed remotely on Heroku via GitHub. The repository already contains the necessary requirement.txt and Procfile files for Heroku deployment, the following steps were required to complete the process.

The project was pushed to GitHub, you can fork this repository to connect your own copy to Heroku.

Create a new app on Heroku, and connect it to the GitHub repo. Next go to settings and add the Python buildpack under the buildpacks options.

Provision a new PostgreSQL database through heroku and follow the instructions to set up the database in the Database Setup section. Set up Stripe and Amazon AWS S3 by following the instructions in the Stripe and AWS S3 Setup sections. If you don't set up AWS S3 for your Heroku deployment then user uploads will not persist when the dyno is restarted (which happens approximately once a day), which will lead to missing image files on ticket pages.

You will need to set the following config vars in the Heroku settings.
- DATABASE_URL: <The database url from the newly provisioned PostgreSQL database will already be filled in>
- SECRET_KEY: <Random string to use as Flasks Secret Key>
- AWS_ACCESS_KEY_ID: <AWS access key ID for the user with AmazonS3FullAccess permissions>
- AWS_SECRET_ACCESS_KEY: <AWS secret access key for the user with AmazonS3FullAccess permissions>
- AWS_STORAGE_BUCKET_NAME: <Name of the S3 bucket you will be using>
- STRIPE_PUBLISHABLE: <Stripe publishable API test key>
- STRIPE_SECRET: <Stripe secret key>
- STRIPE_WEBHOOK_SECRET: <Stripe webhook secret key>

Next, on Heroku under the deploy tab either enable automatic deploys from the master branch, or select the master branch and deploy it manually. Open the console and run the following commands to finish setting up the server.

```
$ python3 manage.py collectstatic
$ python3 manage.py migrate
$ python3 manage.py createsuperuser
```

The requirements will already be installed from the build process, and the server will be started by Gunicorn. If all goes to plan you should be able to select Open App and launch the site.

## Testing

The site has been tested on a variety of devices, using different browsers and resolutions to ensure compatability and responsiveness.

HTML code was validated by the [WC3 Markup Validator](https://validator.w3.org/), as Django templates tend to cause confusion, the rendered templates of a each page were fed into the validator instead. No errors were raised, although there was a warning for the Google Fonts stylesheet link containing a pipe character.

CSS code was validated using the [WC3 CSS Validator](http://jigsaw.w3.org/css-validator/), and passed with no errors or warnings.

Javascript was checked using [ESLint](https://eslint.org/), ignoring no-undef and no-unused-vars warnings where variables were declared/used elsewhere, code was found to be error free. During manual testing of the site no javascript errors were raised in the console.

Python code was checked by [Anaconnda's](http://damnwidget.github.io/anaconda/) built in PEP8 linter, and is fully compliant, ignoring E501 (line length).

An incremental test after approach was taken for automated testing of the python code, which was repeated using a continuous integration of regression testing following updates in order to check for breaking changes.

Due to the use of certain APIs and functions some parts of the site are more difficult to test using automated testing than others, and these were tested manually. For instance certain database operations used to populate the home page aren't available in SQLite3, and can't be tested when running the tests utilises SQLite as a test database. The use of the Stripe payment intents API also requires the use of a live webhook, which makes automated testing difficult.

### Automated Testing

Automated testing is carried out using the Django test-execution framework, which is based on the unittest module. Continuous integration testing was used by linking the project's GitHub repository to [Travis CI](https://travis-ci.org/), so tests are run automatically whenever commits are pushed.

#### Running Automated Tests Locally

To run the tests locally install the dependencies from requirements.txt as described in the local deployment section, and set the SECRET_KEY environment variable be to something (literally anything).

Tests for each app are broken up into individual files for each coresponding module to be tested, each app in the project has a series of test files, test_*.py which can be run as part of a full set of tests, or individually. To run the tests use the following command:
```
$ python3 manage.py test
```

Appending the name of the app to test eg 'tickets' will run the tests for just the tickets app, or the path of the test file you wish to run eg 'tickets.test_models' will run just those tests.

### Manual Testing

The front end of the site was tested manually, by visiting pages of the site and carring out actions and ensuring they gave the expected result. The manual testing covered they layout and responsiveness of the site, as well as the javascript functionallity. Occasionally manual testing revealed a bug in the python code, which could be fixed, and then tests added to the test suite to ensure it couldn't happen again.

Django's input validation is very good, and I double checked this by inputting unexpected values, or altering query strings, before checking the feedback on the forms was as expected.

The javascript elements of the site were tested by using inputs with an expected result then checking the response of the page itself, inspecting the DOM using developer tools, or inspecting variables using the console.

For instance the chips list which is used to filter results was tested by inspecting the DOM for the hidden multi select it replaces to ensure that changes were accurately reflected in what the form would submit, and that the chips were updated correctly when the page loaded.

The graphs generated for the stats pages were tested using known datasets, and checking they were reproduced as expected on the charts.

#### Testing User Stories

To test that the project fulfilled the needs of its anticipated users, I walked through each of their [user stories](https://github.com/ASquirrelsTail/issue-tracker/blob/master/preprod/ux.md#user-stories) to check their goals were simple to achieve. In order to do this I created a number of users, and using the admin panel assigned them to groups with corresponding permissions, such as the moderator group, which has permissions to edit comments and tickets, or the producers group, which can view stats for all tickets.

I then completed the actions laid out in their user story to make sure it was possible, and the actions required made sense.

For example, user MartinDirector (password c0de1nstitute, feel free to use this login to view the stats pages) has permissions to view stats for all tickets, and transaction stats. Using these stats pages, it's easy to see how much income is being generated, and assess the impact of the platform, which Martin could feed back to shareholders.

#### Testing Stripe

Using the new payments intent API (as required to comply with European regulations regarding [Strong Customer Authentication](https://stripe.com/docs/strong-customer-authentication)) makes testing the Stripe integration with automatic testing more complicated, as it requires the use of webhooks and additional queries to the Stripe API.

Instead it was simpler to manually test payments and refunds by performing the required actions on a deployed version of the site using a test API key, and checking they were completed appropriately on the Stripe Dashboard by comparing payment intents, charges and refunds. Test card numbers are provided for convenience on the payment page, which also allows testing for failed authentication, and insufficient funds.

## Known Issues

Navigating back after completing the payment process will return the user to the payment page for the completed transaction, however attempting to pay again will fail as Stripe won't allow the payment to be completed twice. The user is informed of this error when the payment fails, but it is not made clear as to why they have recieved the error. Not a critical issue, and one that in practice shouldn't arise too often.

Use of the Javascript let keyword prevents the site working on older versions of Internet Explorer, and the use of Arrow functions in the stats pages mean they won't function at all in Internet Explorer, however users in the target audience are unlikely to be using these browsers.

## Credits

### Acknowledgements

- [This answer](https://stackoverflow.com/a/49129560) to why queryset comparison assertions were failing in tests was a lifesaver.
- [This answer](https://stackoverflow.com/a/27315856) on setting a class based view to CSRF exempt helped get the Stripe webhooks working.
- [This answer](https://stackoverflow.com/questions/6160648/annotating-a-sum-results-in-none-rather-than-zero) on fixing sums returning None in annotations helped fix a bug in counting and ordering by number of votes.
- [This post](https://www.ianlewis.org/en/testing-django-views-without-using-test-client) on testing views without URLs was useful for testing abstract views and mixins.
- [This thread](https://stackoverflow.com/questions/46039315/how-can-i-style-a-stripe-elements-input-with-bootstrap) was helpful to get started styling the stripe card input on the payment page.
