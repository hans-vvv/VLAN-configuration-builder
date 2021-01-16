from jinja2 import Environment, FileSystemLoader, StrictUndefined


def _j2_parser(template_name, **kwargs):
    
    file_loader = FileSystemLoader('j2templates')
    env = Environment(
        loader=file_loader, trim_blocks=True, lstrip_blocks=True,
        undefined=StrictUndefined
    )
    template = env.get_template(template_name)
    return template.render(**kwargs)


def l2_vlan(vlan_id, vlan_name=None, l2_downlinks=None):

    if l2_downlinks is None:
        l2_downlinks = []
    kwargs = {'vlan_id': vlan_id, 'vlan_name': vlan_name,
              'l2_downlinks': l2_downlinks}
    return _j2_parser('l2_vlan.txt', **kwargs)


def l3_vlan(vlan_id, vlan_ip, vlan_mask, hsrp_address,
            hsrp_state, vrf, helpers):

    kwargs = {'vlan_id': vlan_id, 'hsrp_address': hsrp_address,
              'hsrp_state': hsrp_state, 'vlan_ip': vlan_ip,
              'vrf': vrf, 'helpers': helpers, 'vlan_mask': vlan_mask}
    return _j2_parser('l3_vlan.txt', **kwargs)
