NOTE: These are just snippets and act as simple templates to build on.

== Search_FortiCloud_AssetManagement.py script == 

Utilizes FortiCloud Asset Mangement API to search for FortiGate devices based on description name.
Returns serial # and description field from the platform.


== FortiZTP_Console.py ==

Searches for FortiGate appliance in Asset Management inventory based on serial # or device description name.
Retrieves the provision status of that device on the FortiZTP portal.
Followed by an option to provision or deprovision the device to the specified FortiManager configured on the script.
