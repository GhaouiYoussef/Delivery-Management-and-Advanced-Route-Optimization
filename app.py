from flask import Flask, render_template, request , jsonify, make_response
from delivery_optimization_web import optimize_delivery
from flask_cors import CORS

'''    firm = request.form['firm']
    locations = request.form.getlist('location')
    num_vehicles = int(request.form['num_vehicles'])'''
app = Flask(__name__)

CORS(app, resources={r"/optimize": {"origins": "*"}})  # Allow all origins for the /optimize route
#CORS(app)  # Enable CORS for all routes


@app.route('/')
def home():
    return render_template('front_end_flask_adapt.html')


@app.route('/optimize', methods=['POST'])
def optimize():
    # Get the data from the frontend form

    data = request.get_json()
    print(data)
        # Extract individual data elements
    firm = data['firm']
    locations = data['locations']
    num_vehicles = int(data['num_vehicles'])
    max_duration = int(data['max_duration'])
    print(firm)
    # Run the delivery optimization algorithm
    optimized_routes = optimize_delivery(firm=firm, locations=locations, num_vehicules=num_vehicles,max_duration=max_duration)
    print(optimized_routes)
    # Return the results as a JSON response
    # Replace \n with newline escape sequences \\n
    #formatted_routes = optimized_routes.replace('\n', '\\n')

    # Return the results as a JSON response
    return jsonify(optimized_routes), 200


if __name__ == '__main__':
    app.run(debug=True)
