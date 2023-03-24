from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_recipe')
def generate_recipe():
    # API to get a random recipe
    recipe_api_url = 'https://www.themealdb.com/api/json/v1/1/random.php'
    response = requests.get(recipe_api_url)
    recipe_data = response.json()
    
    # Get a random fun fact from an API
    fact_api_url = 'https://uselessfacts.jsph.pl/random.json?language=en'
    response = requests.get(fact_api_url)
    fact_data = response.json()
    fact = fact_data['text']
    
    # Render the recipe template with recipe, fact, and GIF data
    return render_template('recipe.html', recipe=recipe_data['meals'][0], fact=fact)

@app.route('/healthy_recipe', methods=['GET', 'POST'])
def healthy_recipe():
    if request.method == 'POST':
        # Get user's nutritional criteria from the form
        min_calories = request.form['min_calories']
        max_calories = request.form['max_calories']
        max_fat = request.form['max_fat']
        max_protein = request.form['max_protein']
        max_carbs = request.form['max_carbs']
        
        # Call the Nutritionix API to get a list of recipes that meet the user's nutritional criteria
        search_api_url = f'https://api.nutritionix.com/v1_1/search?results=0:50&cal_min={min_calories}&cal_max={max_calories}&fields=item_name,brand_name,item_id,nf_calories,nf_total_fat,nf_protein,nf_total_carbohydrate&appId=YOUR_APP_ID&appKey=YOUR_APP_KEY'
        response = requests.get(search_api_url)
        search_data = response.json()
        
        # Filter the list of recipes by nutritional criteria and choose a random recipe
        filtered_recipes = []
        for hit in search_data['hits']:
            if hit['fields']['nf_total_fat'] <= max_fat and hit['fields']['nf_protein'] <= max_protein and hit['fields']['nf_total_carbohydrate'] <= max_carbs:
                filtered_recipes.append(hit)
        if filtered_recipes:
            random_recipe = random.choice(filtered_recipes)
        else:
            # If no recipes meet the nutritional criteria, choose a random recipe from the search results
            random_recipe = random.choice(search_data['hits'])
        
        # Call the MealDB API to get the recipe details
        recipe_api_url = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={random_recipe["fields"]["item_id"]}'
        response = requests.get(recipe_api_url)
        recipe_data = response.json()

        # Render the healthy recipe template with recipe, nutrition, and GIF data
        return render_template('healthy_recipe.html', recipe=recipe_data['meals'][0], nutrition=random_recipe['fields'])
    else:
        # Render the healthy recipe form template
        return render_template('healthy_recipe_form.html')


if __name__ == '__main__':
    app.run(debug=True)
