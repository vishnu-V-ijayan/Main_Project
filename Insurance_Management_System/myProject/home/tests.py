from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginTests(LiveServerTestCase):
    def setUp(self):
        self.live_server_url = 'http://127.0.0.1:8000'
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()

    def test_valid_login_redirects_to_admin_dashboard_and_performs_category_actions(self):
        # Open the login page
        self.browser.get(self.live_server_url + '/handlelogin/')

        # Wait for the email input field to be present
        email_input = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'email'))
        )

        # Enter valid admin credentials
        password_input = self.browser.find_element(By.ID, 'password')
        submit_button = self.browser.find_element(By.ID, 'submit')

        email_input.send_keys('vvvadoor@gmail.com')
        password_input.send_keys('Admin@123')
        submit_button.click()

        # Check if the admin is redirected to the admin dashboard
        expected_url = self.live_server_url + '/admin_dashboard/'
        self.assertEqual(self.browser.current_url, expected_url)

        # Click on the "Category" button in the admin dashboard
        category_button = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/admin-category"]'))
        )
        category_button.click()

        # Check if the admin is redirected to the admin_category page
        expected_url = self.live_server_url + '/admin-category'
        self.assertEqual(self.browser.current_url, expected_url)

        # Click on the "Add Category" link
        add_category_link = WebDriverWait(self.browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="admin-add-category"]'))
        )
        add_category_link.click()

        # Check if the admin is redirected to the admin-add-category page
        expected_url = self.live_server_url + '/admin-add-category'
        self.assertEqual(self.browser.current_url, expected_url)

        # Fill in the form to add a category
        category_name_input = WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.ID, 'id_category_name'))
        )
        category_name_input.send_keys('Travel Insurance')

        # Submit the form
        submit_button = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()

        # Check if the admin is redirected to the admin-view-category page (adjust the URL accordingly)
        expected_url = self.live_server_url + '/admin-view-category'
        self.assertEqual(self.browser.current_url, expected_url)

        # Add more assertions or actions as needed based on the behavior of the admin-view-category page
        # For example, check if the added category is visible on the page.
