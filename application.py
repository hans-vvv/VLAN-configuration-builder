import main
import threading
import tkinter as tk
from tkinter import ttk
from views import InputMainForm


class Application(tk.Tk):
    """Application root window"""

    def __init__(self, gui_config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.gui_config = gui_config

        self.title("VLAN configuration builder")
        self.resizable(width=False, height=False)

        ttk.Label(
            self, text="VLAN configuration builder", font=("TkDefaultFont", 16)
        ).grid(row=0)

        self.main_form = InputMainForm(self, self.gui_config)
        self.main_form.grid(row=1, padx=10)

        self.savebutton = ttk.Button(self, text="Save", command=self.on_save)
        self.savebutton.grid(sticky=tk.E, row=2, padx=10)

        self.resetbutton = ttk.Button(
            self, text="Reset", command=self.main_form.reset
        )
        self.resetbutton.grid(sticky=tk.W, row=2, padx=10)

        self.status = tk.StringVar()
        self.statusbar = ttk.Label(
            self, textvariable=self.status, foreground='red')
        self.statusbar.grid(sticky="we", row=3, padx=10)

    def get_form_data(self):
        """Return data from form"""
        return self.main_form.get()

    def on_save(self):
        """Handles save button clicks"""

        errors = self.main_form.get_errors()
        if errors:
            if isinstance(errors, dict):
                fmt = 'Cannot save, error in fields: {}'
                self.status.set(fmt.format(', '.join(errors.keys())))
            else:
                self.status.set(errors)
            return False
        self.status.set('')
        # Start main worker
        threading.Thread(target=main.main, args=[self], daemon=True).start()
