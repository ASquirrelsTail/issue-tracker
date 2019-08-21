# UX Process

## Goals

- The core goal of Wish Machine is for users to support the developers and provide feedback on Unicorn Attractor by reporting bugs, and suggesting new features.
- The platform should also support the developers as a form of crowdfunding, where users donate money to help with development.
- Users should feel involved in the development process and listened to.
- Developers should be able to use feedback from the platform to inform and support their decisions.
- Wish machine should fit the developers' agile/kaban approach to development.
- The platform should reflect and reinforce the Unicorn Attractor brand.

## Target Audience

Users of Wish Machine will be split between players of Unicorn Attractor, and members of teh development team working to produce it.

Players of Unicorn Attractor are between the ages of 16 and 44, comprising of more women than men, mostly within the ABC1 social grade. Unicorn Attractor is a mobile game, so users will primarily access the Wish Machine platform from mobile devices.

The development team are aged between 22 and 36, tech savvy, and will generally be using the platform from desktop computers. They are a busy team, and do not have a great deal of time to manage the platform.

### Product Research

Some examples of similar products on the market are [Nolt](https://nolt.io/), and [GitHub Issues](https://help.github.com/en/articles/about-issues).

Nolt feedback management is a very user focused, and remains clear and simple despite being fully featured. Some great features include the roadmap, status updates and duplication detection.

Github is more focused on software developers, both as users and developers. Issues and bugs are linked directly to branches and commits in the codebase on GitHub. It is more intimidating than Nolt.

Various crowdfunding sites allow users or customers to contribute to the development of a product, and while they do allow suggestions from customers, they aren't closely linked with donations.

Many sites, and particularly free to play games, use credits or tokens to abstract the spending of money. This is a feature that particularly suits Wish Machine, and would allow users to easily contribute financially to a variety of ideas, rather than paying seperately for each.

### User Stories

- Jenny is a user that has found a bug in Unicorn Attractor, she snapped a screenshot of it and wants to send it to the developers so they can fix it.
- Suzy is a player that wants to be able to pet the dog in the game and wants to make the suggestion to the developers, she's even started a meme on twitter to encourage other users to support the feature.
- Boris wants to support the developers with a donation, and he wants to see that his money is being put to good use.
- Charlene is having issues with a common bug in Unicorn Attractor, and wants to add her complaints to those of others.
- Eliza is a fan of the game, and wants to keep up to date with how its development is progressing.

- Carol is a manager at the developers of Unicorn Attractor, and wants to know how best to focus the team for the biggest impact on the game.
- Kevin is a developer on Unicorn Attractor, he needs user feedback to help him solve a bug in the game.
- Alex is a designer on the dev team, and wants to see if users would enjoy a new feature he's proposing to the team before the expend time and money implementing it.
- Megan is a community manager, and needs to deal with toxic members of the game's community.
- Martin is a director at the developers of Unicorn Attractor, and he needs to report to shareholders on the performance of the game and its development.

## Features

### Key Features

- Users should be able to report bugs, and make feature requests for the game.
- Users can vote for features, and bug requests to tell the dev team they are interested in them.
- Members of the dev team should be able to approve bug reports and feature requests before they are available to vote on.
- Users should be able to purchase credits to spend on votes for new features.
- The site should include a dashboard showing the most popular feature requests and most annoying bugs.
- Users and members of the dev team should be able to comment on issues, and reply to those comments.
- Users should be able to add images to issues and comments, to assist the dev team.
- Members of the dev team should be able to edit and remove issues and comments if they are innapropriate.

### Additional Features

- Notifications to let users know when issues they've voted for are being worked on or have been completed.
- A blog for the dev team to post general updates and discuss new and upcoming features.
- The dev team should be able to easily find and merge duplicate issues.
- Users should be able to refund unused credits where appropriate.

## Structure

### Information Architecture

Data will be stored in an SQL database using Django's ORM, with important relationships as shown. The bugs and features tables extend the issues table. Votes store the number of votes for an issue, and in the case of credits spent on features the value of those votes via the associated transaction. Transactions also record the purchase of credits, such that adding all of a user's transactions together should result in the value stored in their wallet.

![alt text](https://raw.githubusercontent.com/ASquirrelsTail/issue-tracker/master/preprod/db-relationships.png "Database relationship diagram")
Relationship diagram created with [dbdiagram.io](https://dbdiagram.io/).

### Site Map

![alt text](https://raw.githubusercontent.com/ASquirrelsTail/issue-tracker/master/preprod/db-relationships.png "Site map")

## Wireframes

![alt text](https://raw.githubusercontent.com/ASquirrelsTail/issue-tracker/master/preprod/wireframes.png "Wireframes")

## Visuals

The visual style of the site should reflect the playful design of Unicorn Attractor, while remaining clear and readable. The design will adopt the Monokai colour palette, using them up with gradients for navigation and buttons.

![alt text](https://raw.githubusercontent.com/ASquirrelsTail/issue-tracker/master/preprod/monokai.png "Monokai colour palette")

![alt text](https://raw.githubusercontent.com/ASquirrelsTail/issue-tracker/master/preprod/gradient.png "Example gradient")

Nunito will be the primary font for headings, a clear, slightly sans serif font with rounded corners. It pairs nicely with Montserrat for the body text.

The project will utilise the bootstrap front end framework, and build from there to incorporte the visual style of Unicorn Attractor.
