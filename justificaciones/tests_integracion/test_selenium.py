from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

class SeleniumTests(StaticLiveServerTestCase):

    def setUp(self):
        # Asegurar que no exista un usuario duplicado
        User.objects.filter(username="admin").delete()

        self.user = User.objects.create_user(
            username="admin",
            password="adminpass123",
            rol="ADMINISTRATIVO"
        )

        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.browser.maximize_window()

    def tearDown(self):
        self.browser.quit()

    def login(self, username="admin", password="adminpass123"):
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        time.sleep(1)

        self.browser.find_element(By.NAME, "username").send_keys(username)
        self.browser.find_element(By.NAME, "password").send_keys(password)
        self.browser.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(1)

    def test_login_correcto(self):
        self.login()
        self.assertNotIn("login", self.browser.current_url)

    def test_login_incorrecto(self):
        self.browser.get(f"{self.live_server_url}/accounts/login/")

        self.browser.find_element(By.NAME, "username").send_keys("mal_user")
        self.browser.find_element(By.NAME, "password").send_keys("mal_pass")
        self.browser.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        time.sleep(1)
        self.assertIn("login", self.browser.current_url)

    def test_crear_justificacion(self):
        self.login()

        self.browser.get(f"{self.live_server_url}/justificaciones/nueva/")
        time.sleep(1)

        self.browser.find_element(By.NAME, "fecha_inicio").send_keys("2025-01-10")
        self.browser.find_element(By.NAME, "fecha_fin").send_keys("2025-01-12")
        self.browser.find_element(By.NAME, "motivo").send_keys("Enfermedad fuerte")
        self.browser.find_element(By.NAME, "descripcion").send_keys("Reposo médico.")

        # Crear archivo de prueba
        filepath = os.path.join(os.getcwd(), "test.pdf")
        with open(filepath, "wb") as f:
            f.write(b"%PDF-1.4 test file")

        self.browser.find_element(By.NAME, "archivo").send_keys(filepath)

        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        self.assertIn("justificaciones", self.browser.current_url)

    def test_validaciones_formulario(self):
        self.login()

        self.browser.get(f"{self.live_server_url}/justificaciones/nueva/")
        time.sleep(1)

        # Enviar vacío
        self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        html = self.browser.page_source

        # Buscar fragmento confiable
        self.assertIn("obligatorio", html)
