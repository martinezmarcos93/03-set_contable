from M1login import VentanaInicioSesion
from M2SelectClient import VentanaTipoCliente
from M3TablaMono import MainWindow
from M4TablaResp import MainWindowRI
from M6Calculadoras import VentanaCalculadoras
# from M6LiquidadorSueldos import VentanaLiquidadorSueldos
from PyQt5.QtWidgets import QApplication


class MainApp:
    def __init__(self):
        self.app = QApplication([])

        # Iniciar sesión en el estudio
        self.ventana_login = VentanaInicioSesion()
        self.ventana_login.show()
        # self.ventana_login.login_correcto.connect(self.mostrar_ventana_select_client)
        
    def mostrar_ventana_select_client(self):
        # Mostrar ventana para seleccionar tipo de cliente
        self.ventana_login.close()

        self.ventana_select_client = VentanaTipoCliente()
        self.ventana_select_client.monotributista_seleccionado.connect(self.mostrar_ventana_tabla_mono)
        self.ventana_select_client.resp_inscripto_seleccionado.connect(self.mostrar_ventana_tabla_resp)
        # self.ventana_select_client.calculadoras_seleccionado.connect(self.mostrar_ventana_calculadoras)
        self.ventana_select_client.show()

    def mostrar_ventana_tabla_mono(self):
        # Mostrar tabla de monotributistas
        self.ventana_select_client.close()

        self.ventana_tabla_mono = MainWindow()
        self.ventana_tabla_mono.show()

    def mostrar_ventana_tabla_resp(self):
        # Mostrar tabla de responsables inscriptos
        self.ventana_select_client.close()

        self.ventana_tabla_resp = MainWindowRI()
        self.ventana_tabla_resp.show()

    def mostrar_ventana_calculadoras(self):
        # Mostrar ventana de calculadoras
        self.ventana_select_client.close()

        self.ventana_calculadoras = VentanaCalculadoras()
        self.ventana_calculadoras.show()

    # def mostrar_ventana_liquidador_sueldos(self):
    #     # Mostrar ventana de liquidador de sueldos
    #     self.ventana_liquidador_sueldos = VentanaLiquidadorSueldos()
    #     self.ventana_liquidador_sueldos.show()

    def run(self):
        return self.app.exec_()


if __name__ == "__main__":
    main_app = MainApp()
    main_app.run()

