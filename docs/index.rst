State Checker App
=================

Contents
--------

-  `What is State Checker ? <#what-is-state-checker>`
-  `Starting app on local in standalone
   mode <#starting-app-on-local-in-standalone-mode>`__

   -  `Standalone mode requirements <#standalone-mode-requirements>`__
   -  `Building for standalone mode <#building-for-standalone-mode>`__

-  `Starting app on APIC(The app
   mode) <#starting-app-on-apic-the-app-mode>`__

   -  `App mode requirements <#app-mode-requirements>`__
   -  `Building for app mode <#building-for-app-mode>`__

### What is State Checker ? State Checker is an ACI app that will allow
you to snapshot a subset of objects in the fabric and compare them. This
will allow you to answer questions like - \* What changed in my fabric
between windows ? \* Are my critical objects the same after maintenance
? \* Are all my routes/endpoints still present ?

The functionality is can be divided into three parts - 1. Standalone
mode specific operations 2. App mode specific operations 3. Common
operations

The reason for such division is also specified in the subsequent
sections.

Operations in standalone mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Standalone mode ensures that you are able to snapshot the fabric even
though you cannot actually deploy the app on the APIC. This case may
arise if there is a shortage of memory due to large number of apps
installed already , large fabric etc. Thus, standalone mode will allow
you to run the app on your system and still take snapshots of the
fabric. For standalone mode user will need ability to configure three
objects which are not required in the app mode : 1. Settings

::

    * The global app settings need to be configured by the user. The defaults are      created when the app is setup but these can be updated by the user.

2. Users

   -  An ``admin`` user is setup by default via setup_db with password
      ``cisco``.
   -  There are 3 roles defined within the app which are

      1. ``FULL_ADMIN`` - Full access i.e. Create/Read/Update/Delete all
         possible objects.
      2. ``USER`` - read access to all objects but no
         create/update/delete access.
      3. ``BLACKLIST`` - login and access to all resources is denied.

   -  The users icon in the top right corner of the screen can be used
      to add new users.

      -  Steps to add a new user.

         1. Click the users icon.
         2. Click plus icon for adding a new user.
         3. A pop up dialog will open. Enter the username, password and
            role.
         4. Click add. The user will be added to users list.
         5. Any old user can be deleted by clicking on the delete/trash
            icon in the actions column for the user.

   -  There is a logout button at the farthest end of top right for
      logging out of the application.

3. Fabrics

   -  The fabrics section is only available in standalone mode. Since,
      the app runs off APIC, the fabric info must be manually added to
      allow the app to discover the fabric.
   -  Steps to add a new fabric -

      1. Go to fabrics section in the app
      2. Press the plus button at the top marked by 1 in the provided
         screenshot.
      3. A pop up box will appear. Input the fabric alias , hostname ,
         user id and password for the fabric.
      4. Click on add. The app will discover the fabric and add it to
         your fabric list or show you any errors that occurred while
         trying to do so.
      5. If the fabric hostname or credentials change then you can edit
         them within the list by double clicking on the information you
         want to change. Once done, click the blue verify icon marked by
         2 to rediscover/ reverify the fabric.
      6. You may discard a fabric by clicking on the delete/trash icon
         in the actions column of the corresponding fabric. It is marked
         with 3 in the screenshot provided.
      7. If the changes do not reflect due to network connectivity or
         any other reason, you can use the refresh icon at the top
         marked by 4 to retrieve all information on the page.
      8. The back button marked by 5 can be used to go back to previous
         page.

Operations in app mode
~~~~~~~~~~~~~~~~~~~~~~

App mode is when the application is deployed and run on the APIC. The
procedure for which is specified in the `build in app mode
section <#building-for-app-mode>`__. In this mode, their is no feature
for users. The users who have credentials for logging into the APIC can
access the app. Also, there is no fabrics section as the fabric will be
auto discovered based on the APIC. This app is written to confirm to
good/modern restful interface. Unfortunately, ACI app heavily restricts
stateful app backend calls, specifically due to the following
restrictions:

ACI backend app can only receive “POST” or “DELETE” methods ACI backend
app must have all endpoints staticially defined in the app.json file.
There is no support for dynamic urls and cannot be a ‘long’ path To
workaround this restriction, all app API calls when running in app mode
need to be sent to the same URL (proxy.json) with full details regarding
original Rest call embedded in the data sent to proxy. Additionally,
javascript frontend needs to maintain APIC devCookie and APIC-Challenge
set by parent iframe (will re-discuss this, very easy to implement). For
proxy calls, a javascript example is:

Common operations
~~~~~~~~~~~~~~~~~

These are the actual operations you can do with the app and these can be
performed in both the modes. The functions are

1. Definitions

   -  Definitions is a set of classes/objects that need to be collected
      for a snapshot along with details regarding how it should be
      collected and what the attributes mean.
   -  At setup a default definition is created that contains all the
      classes.
   -  Steps to create a new definition :

      1. Click the definitions icon in the top right corner.
      2. On the definitions page, click plus icon to add a new
         definition.
      3. In the popup, enter name for the definition, description , and
         from the classes dropdown select all the classes that are of
         interest and click create.
      4. The definition will now be available in the definitions list.
      5. There are two actions available in the actions column, one is
         details icon in blue that allows you to look at the details of
         the definition , and the delete/trash icon that will delete the
         selected definition.
      6. The default definition cannot be deleted by default.

2. Snapshots

   -  Snapshot, as the name suggests is the record of the state of
      different components in the fabric.
   -  This section can be accessed from the home page of the app.
   -  Steps to create a new snapshot :

      1. Ensure that you have created a definition that you want the
         snapshot to cover.
      2. Go to snapshots section.
      3. Click on the plus button to add a new snapshot
      4. A popup will show up. Name your snapshot , select the fabric
         you want to snapshot and select the definition the snapshot
         must cover.
      5. Click create. Your snapshot will appear in the list and the
         status of the snapshot will be listed.
      6. Depending on the size of the fabric and the classes included in
         the definition , the snapshot may require some time to process.

3. Comparisons

   -  Comparison, again as the name suggests, compares two snapshots and
      shows the difference between them.
   -  The results may be affected by definitions the snapshots are
      covering.
   -  Here are the steps for creating a new comparison :

   1. From the main page, go to the comparison section.
   2. Click the add button.
   3. Select snapshots you want to compare in snapshot 1 and snapshot 2
      dropdown.
   4. Select the severity of the comparison.
   5. There are five additional parameters that affect the calculation
      of the comparision.

      1. Dynamic
      2. Remap
      3. Serialize
      4. Statistic
      5. Timestamp

   6. Finally, you can select the definition who will govern the context
      of the comparison.
   7. Click compare. The comparison will appear in the list of
      comparisons and the status will be updated.
   8. Depending on the size of fabric, selected definition and the
      calculation parameter, the calculation may take some time.

Starting app on local in standalone mode
----------------------------------------

Standalone mode requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Linux/ macOS
-  Python 2.7.9
-  `Docker <https://www.docker.com/get-docker>`__
-  Node.js v9.8.0
-  Npm v5.8.0
-  Git CLI
-  Pyenv (virtual environment for managing multiple versions of python,
   not mandatory).

   -  You can run the following bash script for installing pyenv. Please
      note that the .bash_profile file might need a substitution based
      on the platform.

      .. code:: text

           cd ~/
           git clone https://github.com/yyuu/pyenv.git .pyenv
           git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
           echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
           echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
           echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
           source ~/.bash_profile

   -  Pyenv may be installed using package managers as well. But
      ultimate goal is to have python version 2.7.9.

-  In case of windows, the build must be done on a linux vm.

Building for standalone mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the requirements listed above are installed, the docker container
that will host the application in standalone mode can be built from
dockerfile and started. Once the container is started, the application
can be accessed from the host environment. Following the steps listed
below will build the container : \* Clone this
`repository <https://github.com/datacenter/statechecker>`__ using git
clone. \* Ensure that the working directory of terminal is inside the
cloned directory. \* If you are using the pyenv virtual environment,
then activate the environment that corresponds to python version 2.7.9
\* Run ``./build/build_app.sh -s``. This will create a container with
volume mount on the present working directory, in this case the
directory with the repository clone. This ensures local development can
be quickly started. The ``s`` flag, as you might expect, stands for
standalone mode. \* Also note, this starts the web server on port 5000
of your host environment. \* The app can now be accessed at
``localhost:5000/UIAssets`` \* Running ``docker ps`` in command line,
you can see that a container for image named aci/statechangechecker:1.0
is started.

Starting App on APIC (The app mode)
-----------------------------------

App Mode Requirements
~~~~~~~~~~~~~~~~~~~~~

The requirements for building the app in apic mode is same as that for
standalone mode.

Building for app mode
~~~~~~~~~~~~~~~~~~~~~

Following the steps listed below will build the container : \* Clone
this
`repository <https://wwwin-gitlab-sjc.cisco.com/aci-escalate/StateChangeChecker>`__
using git clone. \* Ensure that the working directory of terminal is
inside the cloned directory. \* If you are using the pyenv virtual
environment, then activate the environment that corresponds to python
version 2.7.9 \* Run ``./build/build_app.sh``. This will build the
container and package it as a ``.aci`` file that is required by the APIC
to run it. \* This aci file will be placed in the ``/tmp/appbuild/``
folder with filename ``Cisco-StateChangeChecker-1.0.aci``. \* For
deploying this on the apic, do the following steps :

-  Login to the APIC.
-  Go to the apps page using navigation bar.
-  Select the option to upload a new app in the right hand topside menu.
-  Upload the packaged ``.aci`` file.
-  Once the app is uploaded, it will be listed in the apps page.
-  You can enable the app from there and start using it once enabled.