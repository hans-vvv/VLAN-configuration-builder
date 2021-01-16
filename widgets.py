import ipaddress
import tkinter as tk
from tkinter import ttk


class ValidatedMixin:
    """Adds validation functionality to an input widget"""

    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)  # Call to base class

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        # Change widget config
        self.config(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _validate(self, proposed, current, char, event, index, action):
        """The validation method.
        Don't override this, override _key_validate, and _focus_validate
        """
        self.error.set('')
        valid = True
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'key':
            self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )

    def _key_invalid(self, **kwargs):
        """Handle invalid data on a key event.
        By default we want to do nothing
        """
        pass

    def trigger_focusout_validation(self):
        return self._validate('', '', '', 'focusout', '', '')


class HsrpEntry(ValidatedMixin, ttk.Entry):

    def _focusout_validate(self, event):
        if self.get():
            try:
                self.ip = ipaddress.IPv4Interface(self.get())
                prefix_length = int(self.ip.with_prefixlen.split('/')[1])
                if not 23 <= prefix_length <= 28:
                    self.error.set('Invalid prefix length')
                    return False
            except ValueError:
                self.error.set('Invalid IP address')
                return False
            ip_net = self.ip.network
            highest_ip = [ip_add for ip_add in ip_net.hosts()][-1]
            if highest_ip != self.ip.ip:
                self.error.set('Not highest IP address')
                return False
        if not self.get() and not self.state():
            self.error.set('Please fill in a value')
            return False
        return True


class VlanEntry(ValidatedMixin, ttk.Entry):

    def _key_validate(self, action, index, char, **kwargs):
        if action == '0':
            return True
        elif index in ('0', '1', '2', '3') and char.isdigit():
            return True
        else:
            return False

    def _focusout_validate(self, event):
        if self.get():
            if not (1 < int(self.get()) <= 4094):
                self.error.set('Invalid VLAN value')
                print('test')
                return False
        elif not self.get() and not self.state():
            self.error.set('Please fill in a value')
            return False
        return True


class LabelInput(ttk.Frame):
    """A widget containing a label and input together."""

    def __init__(self, parent, widgetclass, caption=None, var=None,
                 **kwargs):
        super().__init__(parent)
        self.variable = var or tk.StringVar()  # Use shared variable or own
        self.widget = widgetclass(self, **kwargs)
        self.caption = caption

        if 'button' in widgetclass.__name__.lower():
            self.widget.config(text=self.caption)
            self.widget.config(variable=var)
        else:
            self.label = ttk.Label(self, text=self.caption)
            self.label.grid(row=0, column=0, sticky=tk.W)
            self.widget.config(textvariable=self.variable)

        self.widget.grid(row=1, column=0, sticky=tk.W)

        # Only reserve space for error messages on grid for Entry widgets
        if 'Entry' in widgetclass.__name__:
            self.error = getattr(self.widget, 'error', tk.StringVar())
            self.error_label = ttk.Label(self, textvariable=self.error,
                                         foreground='red')
            self.error_label.grid(row=2, column=0, sticky=(tk.W + tk.E))

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        """ Override default settings """
        super().grid(sticky=sticky, **kwargs)

    def get(self):
        return self.variable.get()

    def set(self, value):
        if isinstance(self.variable, tk.BooleanVar):
            self.variable.set(bool(value))
        else:
            self.variable.set(value)
