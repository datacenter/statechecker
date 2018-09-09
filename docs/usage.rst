Usage
=====

StateChecker allows the operator to collect snapshots of the fabric and perform comparisions to 
understand how the fabric has changed. To get started, perform the following steps:

- `Configuring Users`_
- `Connecting to the Fabric`_
- `Creating Snapshots`_
- `Creating Comparisions`_
- `Managing Definitions`_

.. note:: There a few differences when running StateChecker in ``app mode`` vs. ``standalone``. 
    In ``app mode``, all authentication and authorization is handled by the APIC and not enabled 
    on the app.  Second, only the fabric in which the app is installed can be monitored. The app 
    uses certificates installed by the APIC to access the MOs and therefore no fabric setup or 
    configurations are required. All **fabric** and **user** options are hidden when running in 
    ``app mode``.

Configuring Users
^^^^^^^^^^^^^^^^^

.. note:: Configuring users is only available in ``standalone`` mode

At install a single user is created with username ``admin`` and default password ``cisco``.
Operators can configure multiple users for accessing StateChecker app. A user can have one of three
roles:

- ``FULL_ADMIN`` role is capable of performing on all read and write operations within the app
- ``USER`` role is a read only role that can view snapshots and comparisions but cannot create or 
  edit them
- ``BLACKLIST`` role is not allowed to access the application

Click the |icon_users| at the top right of the application to manage users.  Users can be added, 
deleted, and updated as needed. Also, the user tab allows passwords to be changed. It is highly 
recommended to change the default password.

Connecting to the Fabric
^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: Configuring the fabric is only available in ``standalone`` mode

A fabric refers to a single APIC cluster and corresponding switches.  StateChecker app can be 
configured to perform snapshots across multiple fabrics.  Note, snapshot comparision must be between
two snapshots collected from the same fabric.

To get started, click the |icon_fabric| icon. Click the |icon_add| icon to add a new fabric. 
Configure the following for connecting to the fabric:

- **Name** unique identifier for this fabric
- **Hostname** DNS hostname or IP address of a single APIC in the cluster. Ideally this would be 
   APIC-1 but can be any APIC in the cluster. The other APIC controlers within the cluster are 
  discovered dynamically and their out-of-band IPv4 addresses are cached and used in the absence of 
  the configure hostname
- **Username** for API access to the fabric.  Note, the user must have ``admin`` read
  access to the MOs in the fabric for proper operation of StateChecker app.
- **Password** for configured username

The app will test the configured credentials at the time the fabric is created or edited. Users can
additionally test access for a configured fabric by clicking the |icon_verify| icon.


Creating Snapshots
^^^^^^^^^^^^^^^^^^

A

Creating Comparisions
^^^^^^^^^^^^^^^^^^^^^

A

Managing Definitions
^^^^^^^^^^^^^^^^^^^^

A


.. |icon_fabric| image:: icon_fabric.png
   :align: middle
   :width: 150

.. |icon_snapshot| image:: icon_snapshot.png
   :align: middle
   :width: 150

.. |icon_compare| image:: icon_compare.png
   :align: middle
   :width: 150

.. |icon_users| image:: icon_users.png
   :align: middle
   :width: 50

.. |icon_add| image:: icon_add.png
   :align: middle
   :width: 50

.. |icon_verify| image:: icon_verify.png
   :align: middle
   :width: 50


