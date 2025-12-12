# myapp/views.py
from django.shortcuts import render
from django.http import HttpResponse
import requests
import base64
import json
import re

PERPLEXITY_API_KEY = "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"
PERPLEXITY_API_ENDPOINT = "https://api.perplexity.ai/chat/completions"

# Unsplash API credentials (Sign up at https://unsplash.com/developers)
UNSPLASH_ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"  # Get this from Unsplash
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'aboutus.html')


def contact(request):
    return render(request, 'contactus.html')


def service(request):
    return render(request, 'services.html')


def fetch_dish_image(dish_name):
    """Fetch a food image from Unsplash API based on dish name"""
    try:
        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }
        
        params = {
            "query": f"{dish_name} food dish",
            "per_page": 1,
            "orientation": "landscape"
        }
        
        response = requests.get(UNSPLASH_API_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return {
                    'url': data['results'][0]['urls']['regular'],
                    'thumbnail': data['results'][0]['urls']['small'],
                    'photographer': data['results'][0]['user']['name'],
                    'photographer_url': data['results'][0]['user']['links']['html']
                }
    except Exception as e:
        print(f"Error fetching image: {str(e)}")
    
    # Return a default placeholder if API fails
    return {
        'url': f"https://via.placeholder.com/800x600/ff6b6b/ffffff?text={dish_name.replace(' ', '+')}",
        'thumbnail': f"https://via.placeholder.com/400x300/ff6b6b/ffffff?text={dish_name.replace(' ', '+')}",
        'photographer': 'Placeholder',
        'photographer_url': '#'
    }


def generate_recipe_from_image(image_file):
    """Generate structured recipe data from uploaded image"""
    image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this image and provide 3 different recipe suggestions that can be made with these ingredients.

For each recipe, provide the response in this EXACT format:

RECIPE: [Recipe Name]
PREP_TIME: [time in minutes]
COOK_TIME: [time in minutes]
SERVINGS: [number]

INGREDIENTS:
- [ingredient 1] | [quantity] | [unit]
- [ingredient 2] | [quantity] | [unit]
(continue for all ingredients)

INSTRUCTIONS:
1. [First step] | [time if applicable]
2. [Second step] | [time if applicable]
(continue for all steps)

DISH_NAME: [exact dish name for image search - be specific]
---

Provide all 3 recipes in this format separated by ---"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(PERPLEXITY_API_ENDPOINT, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            recipe_text = data['choices'][0]['message']['content']
            return parse_recipes(recipe_text)
        else:
            return None, f"API error: {response.status_code}"
    except Exception as e:
        return None, f"Error: {str(e)}"


def parse_recipes(recipe_text):
    """Parse the structured recipe text into a list of recipe dictionaries"""
    recipes = []
    recipe_blocks = recipe_text.split('---')
    
    for block in recipe_blocks:
        if not block.strip():
            continue
            
        recipe = {
            'name': '',
            'prep_time': '',
            'cook_time': '',
            'servings': '',
            'ingredients': [],
            'instructions': [],
            'dish_name': '',
            'image': None
        }
        
        # Extract recipe name
        name_match = re.search(r'RECIPE:\s*(.+)', block)
        if name_match:
            recipe['name'] = name_match.group(1).strip()
        
        # Extract times and servings
        prep_match = re.search(r'PREP_TIME:\s*(.+)', block)
        if prep_match:
            recipe['prep_time'] = prep_match.group(1).strip()
            
        cook_match = re.search(r'COOK_TIME:\s*(.+)', block)
        if cook_match:
            recipe['cook_time'] = cook_match.group(1).strip()
            
        servings_match = re.search(r'SERVINGS:\s*(.+)', block)
        if servings_match:
            recipe['servings'] = servings_match.group(1).strip()
        
        # Extract dish name for image search
        dish_match = re.search(r'DISH_NAME:\s*(.+)', block)
        if dish_match:
            recipe['dish_name'] = dish_match.group(1).strip()
        else:
            recipe['dish_name'] = recipe['name']  # Fallback to recipe name
        
        # Fetch dish image from Unsplash
        recipe['image'] = fetch_dish_image(recipe['dish_name'])
        
        # Extract ingredients
        ingredients_section = re.search(r'INGREDIENTS:(.*?)(?=INSTRUCTIONS:|$)', block, re.DOTALL)
        if ingredients_section:
            ingredient_lines = ingredients_section.group(1).strip().split('\n')
            for line in ingredient_lines:
                line = line.strip()
                if line.startswith('-'):
                    parts = line[1:].split('|')
                    if len(parts) >= 3:
                        recipe['ingredients'].append({
                            'name': parts[0].strip(),
                            'quantity': parts[1].strip(),
                            'unit': parts[2].strip()
                        })
                    elif len(parts) == 2:
                        recipe['ingredients'].append({
                            'name': parts[0].strip(),
                            'quantity': parts[1].strip(),
                            'unit': ''
                        })
                    else:
                        recipe['ingredients'].append({
                            'name': line[1:].strip(),
                            'quantity': '',
                            'unit': ''
                        })
        
        # Extract instructions
        instructions_section = re.search(r'INSTRUCTIONS:(.*?)(?=DISH_NAME:|---|\Z)', block, re.DOTALL)
        if instructions_section:
            instruction_lines = instructions_section.group(1).strip().split('\n')
            for line in instruction_lines:
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    parts = line.split('|')
                    step_text = re.sub(r'^\d+\.\s*', '', parts[0]).strip()
                    time_text = parts[1].strip() if len(parts) > 1 else ''
                    recipe['instructions'].append({
                        'step': step_text,
                        'time': time_text
                    })
        
        if recipe['name']:
            recipes.append(recipe)
    
    return recipes, None


def receipegen(request):
    recipes = None
    error_message = None
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            image = request.FILES['image']
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
            if image.content_type not in allowed_types:
                error_message = "Please upload a valid image file (JPEG, PNG, WEBP, or GIF)."
            else:
                # Generate recipes from image
                recipes, error = generate_recipe_from_image(image)
                if error:
                    error_message = error
        else:
            error_message = "No image file uploaded. Please select an image."
    
    return render(request, 'mealgenerator.html', {
        'recipes': recipes,
        'error_message': error_message
    })


def mealplan(request):
    return render(request, 'mealplanner.html')


def signup(request):
    return render(request, 'signup.html')


def signin(request):
    return render(request, 'signin.html')
