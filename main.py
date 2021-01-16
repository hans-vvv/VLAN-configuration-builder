import yaml
import application
from create_configs import create_configs

with open('gui_config.yml') as f:
    gui_config = yaml.load(f, Loader=yaml.Loader)


def main(app):

    form_data = app.get_form_data()

    create_configs(form_data, gui_config)


if __name__ == '__main__':
    app = application.Application(gui_config)
    app.mainloop()
