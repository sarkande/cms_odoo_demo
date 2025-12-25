    FROM odoo:19.0

    USER root

    # Installer les dépendances nécessaires

    RUN apt-get update && apt-get install -y python3-pip

    # Installer debugpy
    RUN pip3 install --break-system-package debugpy
    RUN pip3 install --break-system-package pydevd-odoo

    # Installer JupyterLab
    RUN pip3 install --break-system-package ipython
    RUN pip3 install --break-system-package jupyterlab

    # Exposer le port pour debugpy
    EXPOSE 5678 8888
    USER odoo
