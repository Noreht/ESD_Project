from flask import Flask, request, jsonify
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import Counter
import requests

app = Flask(__name__)
CORS(app)

GATEWAY_URL= "http://gateway:3000"
# will be deleted after gateway connection
CATEGORIES_SERVICE_URL = "http://categories-service:5001"
LAST_TOP_5_SERVICE_URL = "http://last-top-5-service:5002"
EMAIL_NOTIFICATION_SERVICE_URL = "http://email-service:5003"

DATABASE_URL = "https://personal-e5asw36f.outsystemscloud.com/LastTop5/rest/Top5API" 

def get_top_5(records):
    """Extract top 5 most frequent categories from a list of dicts with 'category' keys."""
    category_list = [record['Category'] for record in records]
    category_counts = Counter(category_list)
    top_5 = [category for category, _ in category_counts.most_common(5)]
    return ",".join(top_5)


@app.route('/find_top_5', methods=['POST'])
def find_top_5():
   
    try:
       
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"error": "Email parameter missing"}), 400

        print("Get Top 5 Past Week activated for email:", email)
        # this step should be through the api gateway. fuck my life legit
        # Step 1: Fetch category records from Categories Service
        print("Get Top 5 Past Week activated for this Email")
        category_response = requests.post(f"{GATEWAY_URL}/GetPastWeek", json={"email":email, "category":""})
        if category_response.status_code == 500:
            return jsonify({"error": "User does not exist"}) #create new entry for user, code 201(?)

        records = category_response.json()
        if not records:
            return jsonify({"error": "No categories found for user"})
        # end of step 1.

        # Step 2: Extract Top 5 Categories
        print("step 1 working")
        top_5_categories_str = get_top_5(records)
        print("step 2 working")
        # Step 3: put in this weeks, retrieve last weeks
        last_top5_response = requests.post(
            f"{DATABASE_URL}/GetTop5",
            json={
                "UserId": email,
                "CategoriesJSON": top_5_categories_str
            }
        )
        last_top5_data = last_top5_response.json().get("Text")
        if last_top5_data is not None:
            last_week_categories = last_top5_data.get("CategoriesJSON")
        else:
            last_week_categories = ""
        print("step 3 working")
        """ To be sent send as a AMQP
        email_data = f"Hi {UserId}, the top 5 video categories you saved these week are {top_5_categories} and the last top 5 video categories you saved last week are {last_week_categories}. "
        """

        return jsonify({
            "UserId": email,
            "top_5_categories": top_5_categories_str,
            "last_week_categories": last_week_categories
        })
        

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5300, debug=True)
