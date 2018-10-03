Install
=======

StateChecker can be installed directly on the APIC as an ACI app or deployed in standalone mode.

Currently, the APIC imposes a **2G** memory limit and a **10G** disk quota on stateful applications.  
If an operator needs to create and maintain a large number of snapshots or to manage multiple
fabrics within a single instance of the application, it may be beneficial to run the application in
standalone mode.

App Mode
^^^^^^^^

``app mode`` is when the application is deployed and run on the APIC. 
The most recent public release can be downloaded from `ACI AppCenter <https://aciappcenter.cisco.com/statechangechecker-2-2-1n.html>`_.  
After downloading the app, follow the directions for uploading and installing the app on the APIC:

* `2.x Install Video Example <https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/2-x/App_Center/video/cisco_aci_app_center_overview.html>`_
* `2.x Install Instructions <https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/2-x/App_Center/developer_guide/b_Cisco_ACI_App_Center_Developer_Guide/b_Cisco_ACI_App_Center_Developer_Guide_chapter_0110.html#d11320e518a1635>`_
* `3.x Install Instructions <https://www.cisco.com/c/en/us/td/docs/switches/datacenter/aci/apic/sw/2-x/App_Center/developer_guide/b_Cisco_ACI_App_Center_Developer_Guide/b_Cisco_ACI_App_Center_Developer_Guide_chapter_0110.html#d11320e725a1635>`_

Users can also build the app from source prior to installing on the APIC.  See the 
`Building ACI Application`_ to build the app as an ACI application from source.  


Standalone Mode
^^^^^^^^^^^^^^^

``standalone`` mode allows the application to run on a dedicated host, VM, or container controlled by
the operator and make remote connections to the APIC to collect the required data. There are a few
options for deploying the app in ``standalone`` mode below.  Once deployed, the default credentials
for logging into the application are:

- username: ``admin``
- password: ``cisco``

Pre-build OVA
-------------

.. warning:: Details to come

Deployment
----------

The app has been developed to be deployed as an all-in-one container. This relaxes the requirements
on the host machine as all dependencies are already installed within the container.  To deploy the
app in ``standalone`` mode, install docker and execute the following command:

.. code-block:: bash

    docker run --name statechecker -p 5000:443 -d agccie/statechecker:latest

The container will be pulled from Dockerhub and started with an HTTPS web server running on port 
**5000**. The application can be access via `https://localhost:5000 <https://localhost:5000>`_.

Deployment (Development)
------------------------

The application can also be deployed in ``standalone`` mode by manually building the container and
mounting the source code into the appropriate directories. Similar to the all-in-one approach, all
dependencies are still installed within the container so the host machine only requires the
following:

- git
- docker
- linux or macOS

.. note:: Deployment scripts are written in bash and have not been tested on Windows.  Want to get 
    the build script working in windows? Feel free to submit a pull request!

To begin, use git to clone the source repository:

.. code-block:: bash

    $ git clone https://github.com/datacenter/statechecker.git

Next execute the ``build_app.sh`` script with the ``-s`` flag to deploy the application in 
``standalone`` mode. By default the build script will deploy the application running on http port 
(p) 5000 and https port (P) 5001. You can customize these ports using the ``-p`` and ``-P`` flags, 
respectively.

.. code-block:: bash

    $ ./statechecker/build/build_app.sh -h

    Help documentation for ./statechecker/build/build_app.sh
        -a [name] build all-in-one container image (used for creating docker hub image only)
        -i [image] docker image to bundled into app (.tgz format)
        -h display this help message
        -k [file] private key uses for signing app
        -P [https] https port when running in standalone mode
        -p [httsp] http port when running in standalone mode
        -r relax build checks (ensure tools are present but skip version check)
        -s build and deploy container for standalone mode
        -v [file] path to intro video (.mp4 format)
        -x send local environment proxy settings to container during build

    $ ./statechecker/build/build_app.sh -s
    2018-09-07T19:23:16 check build tools: backend
    2018-09-07T19:23:16 checking following dependencies: docker
    2018-09-07T19:23:16 all build tool dependencies met
    2018-09-07T19:23:16 deploying standalone container Cisco/StateChangeChecker:1.0
    2018-09-07T19:23:16 building container
    ...
    Successfully tagged aci/statechangechecker:1.0
    2018-09-07T19:23:16 starting container

You can validate that the container is running on the configured ports via:

.. code-block:: bash

    $ docker ps
    CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS              PORTS                                         NAMES
    c81a139aed67        aci/statechangechecker:1.0   "/bin/sh -c $BACKEND…"   17 minutes ago      Up 17 minutes       0.0.0.0:5000->80/tcp, 0.0.0.0:5001->443/tcp   statechangechecker_1.0

Once deployed you can access the application on the host and port number you configured. If running 
on a local machine with default options, you would access the site at
`http://localhost:5000 <http://localhost:5000>`_.

.. note:: the build script will mount the source code as a read only directory within the container.
    Any development should be done on the host, not the container.  Similarly, if the source code is 
    removed from the host it will cause the application running in the container to fail.


Building ACI Application
^^^^^^^^^^^^^^^^^^^^^^^^

If you are unable to download the app from the appstore or need to build from source to resolve a
bug or enhancement, you can build the application from source. On the development environment, 
you'll need to have the following installed:

- git
- docker
- zip
- python2.7 + pip
- Node.js v9.8.0
- Npm v5.8.0

First, clone the source code repo. From within the source directory, use pip to install the packager
dependencies.  Finally, execute the ``build_app.sh`` script. 

.. note:: If using a node or npm version higher than that listed in the requirements, used the 
    ``-r`` flag during the build process.

.. code-block:: bash

    $ git clone https://github.com/datacenter/statechecker.git 
    $ cd ./statechecker
    $ pip install build/app_package/cisco_aci_app_tools-1.1_min.tar.gz
    $ ./build/build_app.sh


