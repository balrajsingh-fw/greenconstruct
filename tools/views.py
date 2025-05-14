import json

from django.shortcuts import render
from django.http import HttpResponse
from .models import Material
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl
from .forms import CarbonTrackingForm, WasteReductionForm, DesignPlanningForm
import google.generativeai as genai


def carbon_tool(request):
    if request.method == 'POST':
        material_id = request.POST['material']
        quantity = float(request.POST['quantity'])

        # Retrieve the material from the database
        material = Material.objects.get(id=material_id)

        # Calculate carbon emissions
        carbon_emission = material.co2_intensity * quantity

        ai_insight = generate_carbon_footprint_insight(material,
                                                       quantity,
                                                       carbon_emission)

        # Display the result on the page
        return render(request, 'tools/carbon_tool.html', {
            'material': material,
            'quantity': quantity,
            'carbon_emission': carbon_emission,
            'insight': ai_insight
        })

    # If GET request, display the form
    materials = Material.objects.all()
    return render(request, 'tools/carbon_tool.html', {'materials': materials})


def generate_carbon_footprint_insight(material, quantity, carbon_emission):
    prompt = (
        "Based on the following material, quantity and carbon emission data "
        "provide valuable insights for alternatives and effect of using this "
        "quantity of material on environment, also suggest what other materials "
        "can be used instead of the provided material of given amount:"
        "Provide output in json format and do not add any other comments."
        f"- Material: {material.name}"
        f"- Quantity in Kgs: {quantity}%"
        f"- Carbon Emission: {carbon_emission}"

        """Respond only in JSON with:
        {
          "insight": ...,
        }
        """)
    chat_session = create_gemini_model()
    response = chat_session.send_message(prompt)

    raw_text = response.text.strip()

    # Sometimes the model includes triple quotes or markdown-style formatting; remove them
    if raw_text.startswith("```json"):
        raw_text = raw_text.lstrip("```json").rstrip("```").strip()

    try:
        carbon_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        waste_data = {}
    print("waste data", carbon_data)
    return carbon_data


# Waste Reduction Tool (Renamed to waste_tool as per request)
def waste_tool(request):
    if request.method == 'POST':
        form = WasteReductionForm(request.POST)
        if form.is_valid():
            building_size = form.cleaned_data['building_size']
            material = form.cleaned_data['material']
            waste_factor = form.cleaned_data['waste_factor']
            construction_method = form.cleaned_data['construction_method']
            project_phase = form.cleaned_data['project_phase']
            climate = form.cleaned_data['climate']

            # Simple waste calculation (adjust as needed)
            predicted_waste = building_size * (waste_factor / 100)

            ai_result = generate_waste_forecasting(
                building_size, material, waste_factor,
                construction_method, project_phase, climate
            )

            return render(request, 'tools/waste_tool.html', {
                'form': form,
                'predicted_waste': predicted_waste,
                'material': material,
                'construction_method': construction_method,
                'project_phase': project_phase,
                'climate': climate,
                'ai_result': ai_result
            })
    else:
        form = WasteReductionForm()

    return render(request, 'tools/waste_tool.html', {'form': form})

def generate_waste_forecasting(building_size, material, waste_factor,
                construction_method, project_phase, climate):
    prompt = (
                "Based on the following construction context, provide smart waste reduction tips and a brief forecast:"
                "Provide output in json format and do not add any other comments."
                f"- Building size: {building_size} sq ft"
                f"- Material: {material.name}"
                f"- Waste factor: {waste_factor}%"
                f"- Construction method: {construction_method}"
                f"- Project phase: {project_phase}"
                f"- Climate: {climate}"
                
                """Respond only in JSON with:
                {
                  "predicted_waste_kg": ...,
                  "waste_reduction_tips": [
                    "...",
                    "..."
                  ],
                  "expected_material_wastage_kg": float,
                  "reason_for_wastage": str
                }
                """)
    chat_session = create_gemini_model()
    response = chat_session.send_message(prompt)

    raw_text = response.text.strip()

    # Sometimes the model includes triple quotes or markdown-style formatting; remove them
    if raw_text.startswith("```json"):
        raw_text = raw_text.lstrip("```json").rstrip("```").strip()

    try:
        waste_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        waste_data = {}
    print("waste data", waste_data)
    return waste_data


def dashboard(request):
    return render(request, 'dashboard.html')


def design_tool(request):
    if request.method == 'POST':
        sunlight = float(request.POST.get('sunlight'))
        airflow = float(request.POST.get('airflow'))
        size = float(request.POST.get('size'))
        energy_budget = float(request.POST.get('energy_budget'))

        suggestion = generate_design_suggestion_gemini(sunlight, airflow, energy_budget, size)

        print('suggestion', suggestion, type(suggestion))
        return render(request, 'tools/design_tool.html', {
            'design_suggestion': suggestion
        })

    return render(request, 'tools/design_tool.html')


def generate_design_suggestion_gemini(sunlight, airflow, energy_budget, size):
    prompt = (

        """You are an AI assistant for sustainable architecture.
            
            Given the following building design constraints:
            - Sunlight in hrs/day
            - Airflow in cfm
            - Energy Budget in kWh/year
            - Building Size in square meters
            
            Generate optimized green building suggestions, formatted as structured JSON.
            
            Response Format:
            {
              "passive_design_strategies": ["..."],
              "recommended_materials": [
                {"name": "...", "reason": "..."},
                ...
              ],
              "energy_efficiency_tips": ["..."],
              "additional_notes": "..."
            }
            
            Make sure all items are concise, relevant, and environmentally responsible.
            """ +
            f"Suggest sustainable building design strategies for:\n"
            f"- Sunlight: {sunlight} hours/day\n"
            f"- Airflow: {airflow} cfm\n"
            f"- Energy Budget: {energy_budget} kWh/year\n"
            f"- Size: {size} square meters\n"
            f"Include passive design ideas, material suggestions, and energy efficiency tips."
            f"Respond with only a valid json object without any additional commentary."
    )

    chat_session = create_gemini_model()
    response = chat_session.send_message(prompt)

    raw_text = response.text.strip()

    # Sometimes the model includes triple quotes or markdown-style formatting; remove them
    if raw_text.startswith("```json"):
        raw_text = raw_text.lstrip("```json").rstrip("```").strip()

    try:
        design_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        design_data = {}
    return design_data


def create_gemini_model():
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",  # Set the MIME type to JSON
    }
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
    ]
    genai.configure(api_key='AIzaSyCbHyl224pNyX_HOnYFtjwQr_o2nH8GgLU')
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
    )
    chat_session = model.start_chat(
        history=[
        ]
    )
    return chat_session