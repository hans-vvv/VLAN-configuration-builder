# VLAN configuration builder
 
This script generates Cisco IOS configurations for a couple of distribution switches. It was impossible for me to build this GUI without this excellent resource:

https://subscription.packtpub.com/book/application_development/9781788835886

The configuration for the GUI must be provided with the gui_config.yml file. When you start main.py a GUI will appear. You have to fill in some network resources (VLAN, etc) to build two configurations. Special care has been taken about error handling. For example, the HSRP address must be the highest IP address from the given subnet and the prefix length must be between 23 and 28. So for example the input 10.10.10.14/28 will be accepted.

Install jinja2 and pyyaml using pip.


Hans Verkerk January 2021



