import json

from django.shortcuts import render, get_object_or_404, redirect
from django.forms import formset_factory
from .models import Material, Project, BuildingType
from .forms import *
import google.generativeai as genai

MaterialFormSet = formset_factory(MaterialQuantityForm, extra=1)


def carbon_tool(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    MaterialFormSet = formset_factory(MaterialQuantityForm, extra=1)

    if request.method == 'POST':
        formset = MaterialFormSet(request.POST)
        if formset.is_valid():
            total_emission = 0
            breakdown = []

            for form in formset:
                material = form.cleaned_data.get('material')
                quantity = form.cleaned_data.get('quantity')

                if material and quantity:
                    emission = material.co2_intensity * quantity
                    total_emission += emission
                    breakdown.append({
                        'material': material.name,
                        'quantity': quantity,
                        'emission': round(emission, 2),
                    })

            insight = generate_carbon_footprint_insight(breakdown, total_emission)

            # Save carbon data to project
            project.carbon_data = breakdown
            project.carbon_insight = insight
            project.save()

            # Redirect to next step: waste tool
            return redirect('waste_tool', project_id=project.id)
    else:
        formset = MaterialFormSet()
    materials = Material.objects.all()
    return render(request, 'tools/carbon_tool.html', {'materials': materials,
                                                      'formset': formset,
                                                      'project': project})


def generate_carbon_footprint_insight(breakdown, total_emission):
    prompt = (
        "You are an AI sustainability assistant analyzing carbon emissions from construction materials. "
        "You are given a list of materials, each with a name, quantity used (in kg), and total carbon emissions (in kg CO2). "
        "For each material, provide detailed insights about its environmental impact and suggest sustainable alternatives. "
        "Also include a total emission summary and a high-level insight for the overall material usage."

        "\n\nRespond ONLY in the following JSON format and include nothing else:\n"
        """{
          "materials": [
            {
              "material": "string",
              "quantity": float,
              "emission": float,
              "emission_per_unit": float,
              "environmental_impact": "string",
              "alternatives": [
                {
                  "material": "string",
                  "description": "string",
                  "emission_factor": "string or float",
                  "considerations": "string"
                }
              ],
              "recommendations": "string"
            }
          ],
          "total_emission": float,
          "summary_insight": "string"
        }"""

        "\n\nHere is the input data of materials with their quantities and emissions:\n"
        f"{breakdown}, with total emission: {total_emission}.\n"
        "Only return the valid JSON response as described above."
    )
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
def waste_tool(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = WasteReductionForm(request.POST)
        if form.is_valid():
            building_size = form.cleaned_data['building_size']
            material = form.cleaned_data['material']
            waste_factor = form.cleaned_data['waste_factor']
            construction_method = form.cleaned_data['construction_method']
            project_phase = form.cleaned_data['project_phase']
            climate = form.cleaned_data['climate']

            predicted_waste = building_size * (waste_factor / 100)

            ai_result = generate_waste_forecasting(
                building_size, material, waste_factor,
                construction_method, project_phase, climate
            )

            # Save waste data and insights to project
            project.waste_data = {
                'building_size': building_size,
                'waste_factor': waste_factor,
                'construction_method': construction_method,
                'project_phase': project_phase,
                'climate': climate,
                'predicted_waste': predicted_waste
            }
            project.waste_insight = ai_result
            project.save()

            return redirect('design_tool', project_id=project.id)
    else:
        form = WasteReductionForm()
    return render(request, 'tools/waste_tool.html', {'form': form, 'project': project})

def generate_waste_forecasting(building_size, material, waste_factor,
                construction_method, project_phase, climate):
    prompt = (
                "Based on the following construction context, provide smart waste reduction tips and a brief forecast:"
                "Provide output in json format and do not add any other comments."
                f"- Building size: {building_size} sq ft"
                f"- Materials used are: {material}"
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




def design_tool(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        sunlight = float(request.POST.get('sunlight'))
        airflow = float(request.POST.get('airflow'))
        size = float(request.POST.get('size'))
        energy_budget = float(request.POST.get('energy_budget'))

        suggestion = generate_design_suggestion_gemini(sunlight, airflow, energy_budget, size)

        # Save design data and insights to project
        project.design_data = {
            'sunlight': sunlight,
            'airflow': airflow,
            'size': size,
            'energy_budget': energy_budget
        }
        project.design_insight = suggestion
        project.save()

        # After design tool, generate combined insight & redirect to project detail
        combined_insight = generate_combined_insight(project)
        project.combined_insight = combined_insight['insight']
        project.graph_metrics = combined_insight['graph_metrics']
        project.save()

        return redirect('project_step', project_id=project.id, step=4)

    return render(request, 'tools/design_tool.html', {'project': project})



def generate_design_suggestion_gemini(sunlight, airflow, energy_budget, size):
    prompt = (

        """You are an AI assistant for sustainable architecture.
            
            Given the following building design constraints:
            - Sunlight in hrs/day
            - Airflow in cfm
            - Energy Budget in kWh/year
            - Building Size in square ft
            
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


def dashboard(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, "dashboard.html", {"projects": projects})


import json

def generate_combined_insight(project):
    # Gather existing insights from project
    carbon = project.carbon_insight or {}
    waste = project.waste_insight or {}
    design = project.design_insight or {}

    # Convert JSON strings if needed
    import json
    for insight in [carbon, waste, design]:
        if isinstance(insight, str):
            try:
                insight = json.loads(insight)
            except:
                insight = {}

    # Compose the prompt with all insights embedded
    prompt = f"""
You are an AI sustainability assistant tasked with generating a combined insight and forecasting for a construction project.
You are given detailed JSON data from three separate tools:

1. Carbon Emission Insight:
{json.dumps(carbon, indent=2)}

2. Waste Reduction Insight:
{json.dumps(waste, indent=2)}

3. Design Tool Insight:
{json.dumps(design, indent=2)}

Please analyze all data and provide a combined JSON output with:

- A human-readable combined insight summary containing two parts
    1. LEED score according to current practise and current data available will be value for key "score" and reason for its calculation will be value of key "reasons", reasons value will be list of strings.
    2. Suggestions for improving all factors to maximise LEED score and then predicted LEED score once user follows all suggestion properly. Here also provide result in two keys 'score' and 'reasons'. Similar to above point.
- In forecasting make sure no past year is provide , forecasting will be made from current year to current year + 1 year
- In the final insight also add the percentage reduction or increase in cost if adviced material are
 used.
- Forecasting information for future emissions, waste, and energy efficiency.
- Graph metrics data suitable for bar graphs, pie charts, or line charts, including:
  - total_carbon_emission (float)
  - predicted_waste_kg (float)
  - energy_efficiency_score (float, 0-100)
  - sustainability_recommendation_score (int, 0-110) (USGBC LEED Certificate score according to your analysis)
  - sustainability_recommendation_grade (str)
Note: sustainability_recommendation_grade is string providing grades for particular range of score 110 Points [Failed(0-39 Points),Certified(40-49 Points),Silver(50-59 Points), Gold(60-79Points),Platinum(80+ Points)],
Return ONLY the JSON response exactly in this format, with no extra text:

{{
  "combined_insight": {{
    "current_scenario": {{'score': int, 'reasons': list of strings}},
    "suggestion": {{'score': int, 'reasons': list of strings}}
  }},
  "forecasting": {{
    "carbon_emission_trend": [{{"year": int, "emission": float}}, ...],
    "waste_trend": [{{"year": int, "waste": float}}, ...],
    "energy_efficiency_trend": [{{"year": int, "score": float}}, ...]
  }},
  "graph_metrics": {{
    "total_carbon_emission": float,
    "predicted_waste_kg": float,
    "energy_efficiency_score": float,
    "sustainability_recommendation_score": int,
    "sustainability_recommendation_grade": string
  }}
}}
"""

    chat_session = create_gemini_model()
    response = chat_session.send_message(prompt)

    raw_text = response.text.strip()

    # Clean possible markdown or code fences
    if raw_text.startswith("```json"):
        raw_text = raw_text.lstrip("```json").rstrip("```").strip()

    try:
        combined_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("JSON parse error:", e)
        combined_data = {}
    print("insight", combined_data.get("insight"))
    # Save back to project
    project.combined_insight = combined_data.get("combined_insight", "")
    project.combined_forecasting = combined_data.get("forecasting", {})
    project.graph_metrics = combined_data.get("graph_metrics", {})
    project.save()

    return combined_data


def project_create(request):
    MaterialFormSet = formset_factory(MaterialQuantityForm, extra=1)
    building_types = BuildingType.objects.all()

    if request.method == 'POST':
        formset = MaterialFormSet(request.POST)
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        city = request.POST.get("city")
        country = request.POST.get("country")
        building_type = request.POST.get("building_type")
        well_certification = request.POST.get("well_certification")
        leed_certification = request.POST.get("leed_certification")
        name = request.POST.get("name")
        if formset.is_valid():
            total_emission = 0
            breakdown = []

            for form in formset:
                material = form.cleaned_data.get('material')
                quantity = form.cleaned_data.get('quantity')
                if material and quantity:
                    emission = material.co2_intensity * quantity
                    total_emission += emission
                    breakdown.append({
                        'material': material.name,
                        'quantity': quantity,
                        'emission': round(emission, 2),
                    })

            insight = generate_carbon_footprint_insight(breakdown, total_emission)

            project = Project.objects.create(
                carbon_data=breakdown,
                latitude=float(latitude),
                longitude=float(longitude),
                city=city,
                country=country,
                building_type=building_type,
                carbon_insight=insight,
                name=name,
                leed_certification=leed_certification,
                well_certification=well_certification,
                current_step=2  # Step 1 done, move to step 2
            )
            return redirect('project_step', project_id=project.id, step=2)
    else:
        formset = MaterialFormSet()

    return render(request, 'projects/create.html',
                  {'formset': formset,
                   "building_types": building_types})


# List all projects
def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/list.html', {'projects': projects})

# Handle step-wise form filling for project
def project_step(request, project_id, step):
    project = get_object_or_404(Project, id=project_id)
    step = int(step)

    # Prevent access to steps beyond current progress
    if step > project.current_step:
        return redirect('project_step', project_id=project.id, step=project.current_step)

    MaterialFormSet = formset_factory(MaterialQuantityForm, extra=1)
    context = {'project': project, 'step': step}

    if request.method == 'POST':
        # STEP 1: Carbon
        if step == 1:
            formset = MaterialFormSet(request.POST)
            if formset.is_valid():
                total_emission = 0
                breakdown = []

                for form in formset:
                    material = form.cleaned_data.get('material')
                    quantity = form.cleaned_data.get('quantity')
                    if material and quantity:
                        emission = material.co2_intensity * quantity
                        total_emission += emission
                        breakdown.append({
                            'material': material.name,
                            'quantity': quantity,
                            'emission': round(emission, 2),
                        })

                insight = generate_carbon_footprint_insight(breakdown, total_emission)
                project.carbon_data = breakdown
                project.carbon_total_emission = total_emission
                project.carbon_insight = insight

                if project.current_step < 2:
                    project.current_step = 2
                project.save()

                return redirect('project_step', project_id=project.id, step=2)

        # STEP 2: Waste
        elif step == 2:
            form = WasteReductionForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                predicted_waste = data['building_size'] * (data['waste_factor'] / 100)

                ai_result = generate_waste_forecasting(
                    data['building_size'], project.carbon_data, data['waste_factor'],
                    data['construction_method'], data['project_phase'], data['climate']
                )

                project.waste_data = {
                    **data,
                    'predicted_waste': predicted_waste
                }
                project.waste_insight = ai_result
                if project.current_step < 3:
                    project.current_step = 3
                project.save()

                return redirect('project_step', project_id=project.id, step=3)

        # STEP 3: Design
        elif step == 3:
            sunlight = float(request.POST.get('sunlight'))
            airflow = float(request.POST.get('airflow'))
            energy_budget = float(request.POST.get('energy_budget'))
            size = project.waste_data.get("building_size")

            suggestion = generate_design_suggestion_gemini(sunlight, airflow, energy_budget, size)

            project.design_data = {
                'sunlight': sunlight,
                'airflow': airflow,
                'energy_budget': energy_budget,
                'size': size
            }
            project.design_insight = suggestion

            combined = generate_combined_insight(project)

            if project.current_step < 4:
                project.current_step = 4
            project.save()

            return redirect('project_step', project_id=project.id, step=4)

    else:
        # GET request: render the correct step's form or data
        if step == 1:
            context['formset'] = MaterialFormSet()
            context['materials'] = Material.objects.all()
            context['project'] = project
        elif step == 2:
            context['form'] = WasteReductionForm()
            context['material'] = project.carbon_data
            context['project'] = project
        else:
            context['project'] = project  # contains previous design data if any

    return render(request, 'projects/steps.html', context)

def project_gallery(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    documents = project.documents.all()  # assuming a related name like `documents`
    return render(request, 'projects/gallery.html', {'project': project, 'documents': documents})
