Introduction
============
State Checker (also known as StateChangeChecker) is a Cisco ACI application that allows operators 
to snapshot a collection of managed objects (MO) in the fabric and perform snapshot comparisons. 
This allows operators to answer questions such as:

- What changed in my fabric ?
- Are my critical objects the same after maintenance ? 
- Did any route change on any node ?
- Are all the local endpoint learns still present ?

Predefined templates are available for the most common checks such as verifying basic L1/L2 state
along with routing and VMM hypervisor connectivity and inventory.  Operators can also create their
own templates controlling what objects are collected and how they are compared.

This application can be installed directly on the Cisco APIC or deployed in standalone mode.


