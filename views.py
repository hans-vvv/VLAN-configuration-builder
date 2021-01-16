import tkinter as tk
from tkinter import ttk
from widgets import LabelInput, VlanEntry, HsrpEntry


class InputMainForm(ttk.Frame):
    """The form for all input widgets."""

    def __init__(self, parent, gui_config):

        self.gui_config = gui_config
        self.parent = parent
        super().__init__(parent)

        self.widgets = {}  # input widgets

        # Unpack config
        self.hosts_cfg = {k: v for k, v in self.gui_config.items()
                          if k == 'hosts'}.pop('hosts')
        self.network_cfg = {k: v for k, v in self.gui_config.items()
                            if k == 'network'}.pop('network')
        self.hostnames = [host + '-' + values['peerswitch']
                          for host, values in self.hosts_cfg.items()]

        # VLAN frame
        vlan_info = tk.LabelFrame(self, text="VLAN")
        self.widgets['hostnames'] = LabelInput(
            vlan_info, ttk.Combobox, "Hostnames",
            values=self.hostnames,
        )
        self.widgets['hostnames'].widget.bind(
            '<<ComboboxSelected>>', lambda _: self._update_widgets()
        )
        self.widgets['hostnames'].grid(row=0, column=0)

        self.widgets['vlan_id'] = LabelInput(
            vlan_info, VlanEntry, "VLAN_id"
        )
        self.widgets['vlan_id'].grid(row=1, column=0)

        self.widgets['vlan_name'] = LabelInput(
            vlan_info, ttk.Entry, "VLAN name"
        )
        self.widgets['vlan_name'].grid(row=1, column=1, padx=50)

        label = ttk.Label(vlan_info, text="Layer-2 links to access")
        label.grid(row=2, column=0, sticky=tk.W)
        self.widgets['l2_downlinks'] = tk.Listbox(
            vlan_info, listvariable=tk.StringVar(), selectmode="multiple",
        )
        self.widgets['l2_downlinks'].grid(row=3, column=0)

        self.widgets['layer3_vlan'] = LabelInput(
            vlan_info, tk.Checkbutton, "Layer-3 VLAN",
            var=tk.BooleanVar(), command=self._toggle_l3_info,
        )
        self.widgets['layer3_vlan'].grid(row=4, column=0, pady=(10, 0))
        vlan_info.grid(row=0, column=0, sticky=(tk.W + tk.E), pady=(10, 10))

        # Layer-3 frame
        l3_info = tk.LabelFrame(self, text="Layer-3")
        self.widgets['hsrp_address'] = LabelInput(
            l3_info, HsrpEntry, "HSRP address (CIDR)"
        )
        self.widgets['hsrp_address'].grid(row=0, column=0, pady=(18, 0))

        self.widgets['vrf'] = LabelInput(
            l3_info, ttk.Combobox, "VRF", values=[]
        )
        self.widgets['vrf'].grid(row=0, column=1, padx=50)
        self.widgets['vrf'].widget.bind(
            '<<ComboboxSelected>>', lambda _: self._update_widgets()
        )

        self.widgets['dhcp_relay'] = LabelInput(
            l3_info, ttk.Checkbutton,
            "IP Helper", var=tk.BooleanVar(),
        )
        self.widgets['dhcp_relay'].grid(row=1, column=0, pady=(0, 0))

        self.widgets['helpers'] = LabelInput(
            l3_info, ttk.Entry, "Helper addresses"
        )
        self.widgets['helpers'].grid(row=2, column=0)
        self.widgets['helpers'].widget.config(state='disabled')
        l3_info.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # default the form
        self.reset()
        self._set_l3info_state(state='disabled')

    def get(self):
        """Retrieve data from form as a dict"""
        data = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Listbox):
                data[key] = widget.curselection()
            else:
                data[key] = widget.get()
        return data

    def reset(self):
        """Resets the form entries"""

        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Listbox):
                widget.delete(0, 'end')
            elif key == "hostnames":
                self.widgets['hostnames'].widget.config(values=self.hostnames)
                widget.set('')
            elif key == 'layer3_vlan':
                self._set_l3info_state(state='disabled')
                self.widgets['layer3_vlan'].set(False)
            else:
                widget.set('')

    def get_errors(self):
        """ Return string with single error or dict with one or more
         errors from Entry widgets"""

        if not self.widgets['hostnames'].get():
            return "Please select hostnames"
        if not self.widgets['vlan_name'].get():
            return "Please provide a VLAN name"
        if not self.widgets['l2_downlinks'].curselection():
            return "Please select one or more layer-2 down links"
        if (self.widgets['layer3_vlan'].get()
                and self.widgets['vrf'].get() == ''):
            return "Please select a VRF"

        # Errors on Entry widgets
        errors = {}
        for key, child in self.widgets.items():
            if isinstance(child, tk.Listbox):
                continue
            if hasattr(child.widget, 'trigger_focusout_validation'):
                child.widget.trigger_focusout_validation()
            if hasattr(child.widget, 'error'):
                if child.widget.error.get():
                    errors[key] = child.widget.error.get()
        return errors

    def _toggle_l3_info(self):
        if not self.widgets['vrf'].get():
            if self.widgets['layer3_vlan'].get():
                self._set_l3info_state(state='normal')
            else:
                self._set_l3info_state(state='disabled')
        else:
            self._set_l3info_state(state='normal')

    def _set_l3info_state(self, state):
        keys = ['hsrp_address', 'vrf', 'dhcp_relay', 'helpers']
        for key in keys:
            if key == 'helpers' and state == 'normal':
                if not self.widgets['dhcp_relay'].get():
                    continue
            else:
                self.widgets[key].widget.config(state=state)

    def _set_listbox_items(self, listbox, choices):
        for index, item in enumerate(choices):
            listbox.insert(index + 1, item)

    def _update_widgets(self):
        """Insert default layer-2 ports, VRF's and helper addresses
           based on selected hostnames into widgets
        """
        hostname_select = self.widgets['hostnames'].get()
        if not hostname_select:
            return
        # Freeze selection to avoid invalid configurations after reselection
        self.widgets['hostnames'].widget.config(values=hostname_select)
        l2_ports = [list(vals['ports'].keys())
                    for hostname, vals in self.hosts_cfg.items()
                    if hostname in hostname_select]
        if not self.widgets['l2_downlinks'].size():
            for port in l2_ports:
                self._set_listbox_items(self.widgets['l2_downlinks'], port)

        vrfs = [values['vrf_members'] for host, values in self.hosts_cfg.items()
                if host in hostname_select][0]
        self.widgets['vrf'].widget.config(values=vrfs)

        vrf_select = self.widgets['vrf'].get()
        if vrf_select:
            # Freeze selection to avoid invalid configurations after reselection
            self.widgets['vrf'].widget.config(values=vrf_select)
            self._set_l3info_state(state='normal')
            dhcp_servers = [helper['ip_helpers']
                            for values in self.network_cfg.values()
                            for vrf, helper in values.items()
                            if vrf_select == vrf][0]
            self.widgets['helpers'].set(','.join(dhcp_servers))
