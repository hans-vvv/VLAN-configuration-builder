import ipaddress
from config_templates import l2_vlan
from config_templates import l3_vlan


def create_configs(data, config):
    """"Create device configurations"""
    # unpack layer-2 data
    hostnames = data['hostnames'].split('-')
    vlan_id = data['vlan_id']
    vlan_name = data['vlan_name']
    all_l2_downlinks = [port for port in config['hosts'][hostnames[0]]['ports']]
    l2_downlinks = [all_l2_downlinks[index] for index in data['l2_downlinks']]

    # print data to file
    for hostname in hostnames:
        with open(hostname + '.txt', 'w') as f:
            config = l2_vlan(
                vlan_id, l2_downlinks=l2_downlinks, vlan_name=vlan_name
            )
            print(config, file=f)

    layer3_vlan = data['layer3_vlan']
    if layer3_vlan:
        # unpack layer-3 data
        hsrp_address = data['hsrp_address'].split('/')[0]
        ip_net = ipaddress.IPv4Interface(data['hsrp_address']).network
        ip_hosts = [host for host in ip_net.hosts()]
        vlan_ips = [ip_hosts[0], ip_hosts[1]]
        vlan_mask = ip_net.netmask
        vrf = data['vrf']
        helpers = data['helpers'].split(',') if data['dhcp_relay'] else []

        # append data to file
        for index, hostname in enumerate(hostnames):
            hsrp_state = 'active' if index == 0 else 'standby'
            with open(hostname + '.txt', 'a') as f:
                config = l3_vlan(
                    vlan_id, vlan_ips[index], vlan_mask, hsrp_address,
                    hsrp_state, vrf, helpers
                )
                print(config, file=f)
