
There a few differences when running StateChecker in `app mode` vs. `standalone`.  First, all 
authentication and authorization is handled by the APIC and not enabled on the app.  Second, only 
the fabric in which the app is installed can be monitored. The app uses certificates installed by 
the APIC to access the MOs and therefore no fabric setup or configurations are required. All fabric 
and user options are hidden when running in `app mode`.

