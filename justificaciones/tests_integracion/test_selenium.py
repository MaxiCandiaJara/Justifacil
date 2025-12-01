import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

User = get_user_model()

@pytest.mark.selenium
class SeleniumTests(StaticLiveServerTestCase):

    def setUp(self):
        # Limpiar usuario duplicado
        User.objects.filter(username="admin").delete()

        self.user = User.objects.create_user(
            username="admin",
            password="adminpass123",
            rol="ADMINISTRATIVO"
        )

        # Iniciar navegador
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.browser.set_window_size(1920, 1080)

        self.wait = WebDriverWait(self.browser, 10)

    def tearDown(self):
        self.browser.quit()

    # ------------------------------ LOGIN ------------------------------

    def login(self, username="admin", password="adminpass123"):
        self.browser.get(f"{self.live_server_url}/accounts/login/")

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        self.browser.find_element(By.NAME, "username").send_keys(username)
        self.browser.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)

        # Esperar a que cambie la URL
        self.wait.until(lambda d: "login" not in d.current_url)

    # ------------------------------ TEST: LOGIN CORRECTO ------------------------------

    def test_login_correcto(self):
        self.login()
        assert "login" not in self.browser.current_url

    # ------------------------------ TEST: LOGIN INCORRECTO ------------------------------

    def test_login_incorrecto(self):
        self.browser.get(f"{self.live_server_url}/accounts/login/")

        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        self.browser.find_element(By.NAME, "username").send_keys("mal_user")
        self.browser.find_element(By.NAME, "password").send_keys("mal_pass" + Keys.RETURN)

        self.wait.until(lambda d: "login" in d.current_url)

        assert "login" in self.browser.current_url

    # ------------------------------ TEST: CREAR JUSTIFICACIÓN ------------------------------

    def test_crear_justificacion(self):
        self.login()

        self.browser.get(f"{self.live_server_url}/justificaciones/nueva/")
        self.wait.until(EC.presence_of_element_located((By.NAME, "fecha_inicio")))

        # Completar formulario
        self.browser.find_element(By.NAME, "fecha_inicio").send_keys("2025-01-10")
        self.browser.find_element(By.NAME, "fecha_fin").send_keys("2025-01-12")
        self.browser.find_element(By.NAME, "motivo").send_keys("Enfermedad fuerte")
        self.browser.find_element(By.NAME, "descripcion").send_keys("Reposo médico.")

        # Crear archivo temporal
        filepath = os.path.join(os.getcwd(), "test.pdf")
        with open(filepath, "wb") as f:
            f.write(b"%PDF-1.4 test file")

        self.browser.find_element(By.NAME, "archivo").send_keys(filepath)

        # SCROLL + CLICK SEGURO
        submit = self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", submit)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        self.browser.execute_script("arguments[0].click();", submit)


        # Esperar redirección
        self.wait.until(lambda d: "justificaciones" in d.current_url)

        assert "justificaciones" in self.browser.current_url

