import os
import subprocess
import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QTextEdit


class JupyterManager(QWidget):
    def __init__(self):
        super().__init__()

        # Import Fields
        self.env_label = QLabel('Environment Name')
        self.env_label.setStyleSheet('font-size: 15px; font-weight: bold;')
        self.env_input = QLineEdit()
        self.env_input.setStyleSheet('font-size: 15px; background-color: #9D73FA; font-weight: bold;')
        self.env_input.setPlaceholderText('Enter Environment Name')

        self.pkg_label = QLabel('Package Name')
        self.pkg_label.setStyleSheet('font-size: 15px; font-weight: bold;')
        self.pkg_input = QLineEdit()
        self.pkg_input.setStyleSheet('font-size: 15px; background-color: #9D73FA; font-weight: bold;')
        self.pkg_input.setPlaceholderText('Enter Package Name (comma-separated)')

        self.port_label = QLabel('Port Number')
        self.port_label.setStyleSheet('font-size: 15px; font-weight: bold;')
        self.port_input = QLineEdit()
        self.port_input.setStyleSheet('font-size: 15px; background-color: #9D73FA; font-weight: bold;')
        self.port_input.setPlaceholderText('Enter Port Number')

        # Create and launch button
        self.create_button = QPushButton('Create and Launch')
        self.create_button.setStyleSheet('background-color: #9D73FA; font-size: 15px; font-weight: bold;')
        self.create_button.clicked.connect(self.create_env_launch_jupyter)

        # Kill button
        self.kill_button = QPushButton('Kill Jupyter Server')
        self.kill_button.setStyleSheet('background-color: #9D73FA; font-size: 15px; font-weight: bold;')
        self.kill_button.clicked.connect(self.kill_jupyter)

        # Text output field
        self.text_output = QTextEdit()
        self.text_output.setStyleSheet('background-color: #F060C3; font-size: 15px; font-weight: bold;')
        self.init_ui()

        self.process = None
        self.create_env = None
        self.activate_env = None
        self.install_packages = None

    def init_ui(self):
        # Add labels and input fields to layout
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.env_label)
        form_layout.addWidget(self.env_input)
        form_layout.addWidget(self.pkg_label)
        form_layout.addWidget(self.pkg_input)
        form_layout.addWidget(self.port_label)
        form_layout.addWidget(self.port_input)

        # Add buttons to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.kill_button)

        # Add form and button layouts to main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.text_output)

        # Set main layout and window properties
        self.setLayout(main_layout)
        self.setWindowTitle('Jupyter Manager')
        self.setGeometry(300, 300, 500, 500)
        self.setStyleSheet('background-color: #332EF0')
        self.show()

    def create_env_launch_jupyter(self):
        env_name = self.env_input.text()
        pkg_name = self.pkg_input.text().replace(',', ' ')

        # Activate virtual environment
        self.text_output.append(f'Activating virtual environment... {env_name}')
        self.create_env = f'python -m venv {env_name}'
        if os.name == 'posix':
            self.activate_env = f'. {env_name}/bin/activate'
            self.install_packages = f'pip install jupyter {pkg_name}'
        else:
            self.activate_env = f'{env_name}\\Scripts\\activate'
            self.install_packages = f'{env_name}\\Scripts\\pip install jupyter {pkg_name}'

        try:
            subprocess.run(self.create_env, shell=True, check=True, stderr=subprocess.STDOUT)
            subprocess.run(self.activate_env, shell=True, check=True, stderr=subprocess.STDOUT)
            subprocess.run(self.install_packages, shell=True, check=True, stderr=subprocess.STDOUT)
            self.text_output.append(f'Virtual environment created and activated successfully!')
        except subprocess.CalledProcessError as e:
            self.text_output.append(f'Error creating virtual environment: {e.output}')
            return
        return

    def launch_jupyter(self):
        port_num = self.port_input.text()
        self.text_output.append('Launching Jupyter Notebook...')
        launch_jupyter = f'jupyter notebook --port={port_num}'
        self.process = subprocess.Popen(launch_jupyter, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        thread = threading.Thread(target=self.reader_thread, args=(self.process,))
        thread.start()
        self.text_output.append(f'Jupyter Notebook launched successfully!')

    def kill_jupyter(self):
        if self.process is None:
            self.text_output.append('No Jupyter Notebook running!')
            return
        self.text_output.append('Killing Jupyter Notebook...')
        self.process.kill()
        self.text_output.append('Jupyter Notebook killed successfully!')
        self.process = None

    def reader_thread(self, process):
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.text_output.append(output.strip())
        rc = process.poll()
        return rc


if __name__ == '__main__':
    app = QApplication(sys.argv)
    jupyter = JupyterManager()
    jupyter.show()
    sys.exit(app.exec_())
