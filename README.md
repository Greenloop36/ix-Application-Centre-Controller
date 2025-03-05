# IX - Application Centre Controller
developed by @gl36

Utility tool to manage access to the application center for Installation IX.

#### Information Security Notice
> This software is classified **Level 0** (For Official Use Only) - anyone may download, distribute or modify this software.
> For more information, see the Licensimg section below.

## Dependencies
Built for Windows 10/11. Not suitable for any other operating system.
The program attempts to install all of the required dependencies, but should it run into an error, you may install them manually:
* PIP;
* colorama;
* requests.

## Setup
When you first start this program, you will be prompted to enter a username, email and "commit token".
**If you do not intend to change the centre's status, you may skip this part by pressing `Control+C`.**

Your username and email should match those used for IX.
Contact `@gl36` for the Commit Access Token.

#### Information
> If prompted to update, select either **Y** (for YES) or **N** (for NO).


## Usage
To change the status, simply edit the form as needed and click *Submit*.
If you have provided a commit token, wait a short while for the commit to process.

Once committed, you can click *Refresh* to see if your changes have been made properly (it may take a few seconds for your changes to be published, even after committing).

## Troubleshooting

### Repairing your installation
The application provides an easy way to repair your installation.
Once launched, click on "*File*", then "*Repair/update installation*". You will then be prompted to update to the latest version.

If this fails, you can always re-download from the repository. A link to the controller's repository is in the "*View*" menu.

### Resetting user data
If you wish to reset your data, you can do so via the "*Edit*" menu, and then by clicking on the "*Initialise user data*" button.
Once reset, relaunch the program.

To do this manually, go to `internal/persistent/Data.json`, and then clear the file entirely.

## Licensing
This software is licensed under the Apache 2.0 license.
For more information, view the `LICENSE` file, located in this directory, or (https://www.tldrlegal.com/license/apache-license-2-0-apache-2-0)[view a summary].

### Requests
This utility makes the use of the `requests` library, developed by Kenneth Reitz.

### Colorama
This utility makes the use of the `colorama` library, developed by Jonathan Hartley.




*Developed using Python 3.12. All rights reserved.*