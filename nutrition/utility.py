import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


from google import genai
from google.genai import types

def analyze_food(image):
  
    food_image = image
    if not food_image:
        return {"error": "No image provided"}

    # 2. Initialize the New Client
    # Replace with your actual API key or use an environment variable
    client = genai.Client(api_key=GOOGLE_API_KEY)

    # 3. Read image bytes
    image_bytes = food_image.read()

    # 4. Define the Prompt & Schema
    prompt = "You are a nutrition expert. Identify the food in the image and estimate calories.get me response.txt with calorie_low, calorie_high, food name , based on the current indian standard time respond any of these  meal_type also (breakfast,lunch,snack,dinner) as json."

    try:
        # Using the new SDK's generate_content
        response = client.models.generate_content(
            model="gemini-2.5-flash", # or gemini-1.5-flash
            contents=[
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=food_image.content_type
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction="You are a clinical nutritionist. Return ONLY JSON.",
                response_mime_type="application/json",
                # Explicit schema ensures the JSON structure is 100% consistent
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "food_name": {"type": "STRING"},
                        "average_calorie": {"type": "NUMBER"},
                        "meal_type":{"type":"STRING"}
                        # "calorie_high": {"type": "NUMBER"} # Changed to NUMBER for easier math later
                    },
                    "required": ["food_name", "average_calorie","meal_type"]
                }
            )
        )

        # 5. Access the parsed JSON directly
        # The new SDK automatically parses JSON if response_mime_type is set
     
        return response.parsed

    except Exception as e:
        return {"error": str(e)}
    

def generate_kerala_diet_plan(goal="weight loss",age =None,weight=None,gender="male",target_weight=None,duration=None):
    
    # Initialize the new Client
    client = genai.Client(api_key=GOOGLE_API_KEY)
    
    # Extract user
   
    
    prompt = f"Create a Kerala-style {goal} diet plan.User: {gender}, {age}yrs, {weight}kg. Target: {target_weight}kg in {duration} months"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a Kerala Nutritionist. Return ONLY JSON.",
                response_mime_type="application/json",
                # This schema ensures your frontend never breaks
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "daily_calories": {"type": "NUMBER"},
                        "diet_plan": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "day": {"type": "STRING"},
                                    "meals": {"type": "ARRAY", "items": {"type": "STRING"}}
                                }
                            }
                        }
                    }
                }
            )
        )
        return response.parsed
    except Exception as e:
        return e

# generate_kerala_diet_plan(goal="weight loss",age=32,weight=75,gender="male",target_weight=68,duration=4)




# prompt = f"""
#     Act as a Clinical Nutritionist. Create a Kerala-style weight loss diet plan.
#     User: {"male"}, {32}yrs, {64}kg. Target: {60}kg in 2 months.
    
#     Format the output strictly as a JSON object with these keys:
#     - "daily_calories": (int)
#     - "nutritional_advice": (string)
#     - "weekly_plan": (list of 7 objects with keys: "day", "breakfast", "lunch", "snack", "dinner")
#     - "kerala_tips": (list of strings)

#     Use traditional Kerala foods (Matta rice, Thoran, Fish curry, etc.). 
#     Ensure portions are specific (e.g., "1/2 cup Matta rice"). 
#     Return ONLY the JSON. No preamble.
#     """






# def process_food_image():

#         food_image = self.request.FILES.get('food_image')

#         genai.configure(api_key = '')

#         image_bytes = food_image.read()

#         model = genai.GenerativeModel("gemini-2.5-flash",
#                                       generation_config={
#                                           "response_mime_type": "application/json"
#                                       })

#         prompt = """
        
#         identify this food item and return the response  strictly  and only in this json format
#         {
#          "food_name" :"",
#          "quantity" : "",
#          "calories" : ""
#         }

#         """

#         response = model.generate_content([prompt, {'mime_type':food_image.content_type, 'data':image_bytes} ])

#         result = response.text

#         data = json.loads(result)




# print(generate_kerala_diet_plan(goal="weight loss",age=19,gender="male",target_weight=80,duration=4))



"""
 'diet_plan': [{'day': 'Monday', 'meals': ['Breakfast: Puttu (3-4 pieces) with Kadala Curry (chickpea curry with coconut milk), 1 large Nendran banana, 1 glass full-fat milk.', 'Mid-morning: Nendran banana milkshake (1 large banana, 200ml milk, 1 tbsp jaggery/honey, few cashews).', 'Lunch: 2.5 cups Brown/White Rice, Fish Curry (2-3 pieces, prepared with coconut milk/oil), Cabbage Thoran, 1 cup Sambar, 1 cup Buttermilk.', 'Evening Snack: Pazham Pori (2 banana fritters), 1 glass Tea with milk.', 'Dinner: 4 Chappathi, Chicken Curry (2-3 pieces, prepared with coconut), Dal Curry, Avial.', 'Before bed: 1 glass warm milk with 2-3 dates.']}
"""
