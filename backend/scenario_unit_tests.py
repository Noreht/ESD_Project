import unittest
import requests

BASE_URL = "http://localhost:3000"


class TestAPIGateway(unittest.TestCase):
    def test_categorisation(self):
        """
        Test the /categorisation endpoint.
        This endpoint forwards the request to the Cat A service.
        """
        url = f"{BASE_URL}/categorisation"
        # Dummy payload; adjust keys as expected by your endpoint
        payload = {"video": "sample_video_data"}
        response = requests.post(url, json=payload)
        # Check that the status code is 200 (or the error handling if service is unavailable)
        self.assertEqual(response.status_code, 200, msg=response.text)
        # Further assertions can be made on response.json() if you know the expected structure

    def test_retrieve_all_albums(self):
        """
        Test the /RetrieveAllAlbums endpoint.
        """
        url = f"{BASE_URL}/RetrieveAllAlbums"
        payload = {"email": "test@example.com", "categories": ["music", "sports"]}
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200, msg=response.text)
        # Optionally, add assertions for expected keys/values in the JSON response

    def test_save_shared_album(self):
        """
        Test the /saveSharedAlbum endpoint.
        """
        url = f"{BASE_URL}/saveSharedAlbum"
        payload = {"album": "shared album info", "otherData": "example"}
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_get_past_week(self):
        """
        Test the /GetPastWeek endpoint.
        """
        url = f"{BASE_URL}/GetPastWeek"
        payload = {"email": "test@example.com", "category": "music"}
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_load_dashboard(self):
        """
        Test the /LoadDashboard endpoint with a valid email query parameter.
        """
        email = "test@example.com"
        url = f"{BASE_URL}/LoadDashboard?email={email}"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_load_dashboard_missing_email(self):
        """
        Test the /LoadDashboard endpoint when the email query parameter is missing.
        Should return a 400 status with an error message.
        """
        url = f"{BASE_URL}/LoadDashboard"
        response = requests.get(url)
        self.assertEqual(response.status_code, 400, msg=response.text)
        self.assertIn("User email missing", response.json().get("error", ""))

    def test_check_exists(self):
        """
        Test the /CheckExists endpoint.
        """
        url = f"{BASE_URL}/CheckExists"
        payload = {"VideoId": "123", "category": "music", "email": "test@example.com"}
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200, msg=response.text)

    def test_insert_processed_video(self):
        """
        Test the /InsertProcessedVideo endpoint.
        """
        url = f"{BASE_URL}/InsertProcessedVideo"
        payload = {"VideoId": "123", "category": "music", "email": "test@example.com"}
        response = requests.post(url, json=payload)
        self.assertEqual(response.status_code, 200, msg=response.text)


if __name__ == "__main__":
    unittest.main()
