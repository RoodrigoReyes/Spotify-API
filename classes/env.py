import json


class EnvAttr:
    """
    Esta clase carga y almacena atributos de entorno desde un archivo JSON.
    """

    def __init__(self, json_path):
        # Abrir archivo JSON en la ruta dada
        with open(json_path) as file_path:
            # Cargue los datos JSON del archivo y guárdelos en el atributo `attr`
            self.attr = json.load(file_path)
