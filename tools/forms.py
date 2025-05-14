from django import forms
from .models import Material

class CarbonTrackingForm(forms.Form):
    material = forms.ModelChoiceField(queryset=Material.objects.all(), label='Select Material', empty_label="Choose a material")
    material_quantity = forms.FloatField(label='Quantity (in kg)')

class WasteReductionForm(forms.Form):
    building_size = forms.FloatField(label='Building Size (sq ft)', min_value=0)
    material = forms.ModelChoiceField(queryset=Material.objects.all(), label='Select Material', empty_label="Choose a material")
    waste_factor = forms.FloatField(label='Waste Factor (%)', min_value=0, max_value=100)

    construction_method = forms.ChoiceField(
        label='Construction Method',
        choices=[
            ('traditional', 'Traditional'),
            ('prefabricated', 'Prefabricated'),
            ('modular', 'Modular'),
            ('3d_printed', '3D Printed'),
        ]
    )

    project_phase = forms.ChoiceField(
        label='Project Phase',
        choices=[
            ('foundation', 'Foundation'),
            ('framing', 'Framing'),
            ('finishing', 'Finishing'),
            ('interior', 'Interior'),
            ('full_project', 'Full Project'),
        ]
    )

    climate = forms.ChoiceField(
        label='Climate Zone',
        choices=[
            ('hot_humid', 'Hot & Humid'),
            ('hot_dry', 'Hot & Dry'),
            ('cold', 'Cold'),
            ('temperate', 'Temperate'),
            ('tropical', 'Tropical'),
        ]
    )

class DesignPlanningForm(forms.Form):
    sunlight = forms.FloatField(label='Desired Sunlight (hours/day)')
    airflow = forms.FloatField(label='Desired Airflow (cfm)')
    energy_budget = forms.FloatField(label='Energy Budget (kWh)')