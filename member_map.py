import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# WG2 Members data with coordinates
people = [
    {"name": "Dennis Bouvier", "country": "USA", "lat": 39.8283, "lon": -98.5795, "iso_alpha": "USA"},
    {"name": "Bruno Pereira Cipriano", "country": "Portugal", "lat": 39.3999, "lon": -8.2245, "iso_alpha": "PRT"},
    {"name": "Richard Glassey", "country": "Sweden", "lat": 60.1282, "lon": 18.6435, "iso_alpha": "SWE"},
    {"name": "Raymond Pettit", "country": "USA", "lat": 39.8283, "lon": -98.5795, "iso_alpha": "USA"},
    {"name": "Emma Anderson", "country": "UK", "lat": 55.3781, "lon": -3.4360, "iso_alpha": "GBR"},
    {"name": "Anastasiia Birillo", "country": "Serbia", "lat": 44.0165, "lon": 21.0059, "iso_alpha": "SRB"},
    {"name": "Ryan Dougherty", "country": "USA", "lat": 39.8283, "lon": -98.5795, "iso_alpha": "USA"},
    {"name": "Orit Hazzan", "country": "Israel", "lat": 31.0461, "lon": 34.8516, "iso_alpha": "ISR"},
    {"name": "Olga Petrovska", "country": "UK", "lat": 55.3781, "lon": -3.4360, "iso_alpha": "GBR"},
    {"name": "Nuno Pombo", "country": "Portugal", "lat": 39.3999, "lon": -8.2245, "iso_alpha": "PRT"},
    {"name": "Ebrahim Rahimi", "country": "Netherlands", "lat": 52.1326, "lon": 5.2913, "iso_alpha": "NLD"},
    {"name": "Charanya Ramakrishnan", "country": "Australia", "lat": -25.2744, "lon": 133.7751, "iso_alpha": "AUS"},
    {"name": "Alexander Steinmaurer", "country": "Austria", "lat": 47.5162, "lon": 14.5501, "iso_alpha": "AUT"},
    {"name": "Shubbhi Taneja", "country": "USA", "lat": 39.8283, "lon": -98.5795, "iso_alpha": "USA"},
    {"name": "Muhammad Usman", "country": "Sweden", "lat": 60.1282, "lon": 18.6435, "iso_alpha": "SWE"},
    {"name": "Annapurna Vadaparty", "country": "USA", "lat": 39.8283, "lon": -98.5795, "iso_alpha": "USA"},
]

df = pd.DataFrame(people)

# Get unique countries and their members
countries_with_people = df.groupby(['country', 'iso_alpha', 'lat', 'lon'])['name'].apply(lambda x: '<br>'.join(x)).reset_index()
countries_with_people['has_people'] = 1

# More spaced out callout positions
callout_offsets = {
    'USA': {'lat': 0, 'lon': -120},
    'Portugal': {'lat': 25, 'lon': -30},
    'Sweden': {'lat': 75, 'lon': 60},
    'UK': {'lat': 70, 'lon': -20},
    'Serbia': {'lat': 35, 'lon': 60},
    'Israel': {'lat': 15, 'lon': 65},
    'Netherlands': {'lat': 85, 'lon': 15},
    'Australia': {'lat': 10, 'lon': 150},
    'Austria': {'lat': 55, 'lon': 55}
}

# Create choropleth showing only countries with members
fig = px.choropleth(
    countries_with_people,
    locations="iso_alpha",
    color="has_people",
    color_continuous_scale=["lightgreen", "lightgreen"],  # All countries same green
    title="WG2 Members"
)

# Add callout boxes
for _, row in countries_with_people.iterrows():
    country = row['country']
    members = row['name']
    
    if country in callout_offsets:
        callout_lat = callout_offsets[country]['lat']
        callout_lon = callout_offsets[country]['lon']
        
        # Add line from country to callout FIRST (so it's behind)
        fig.add_trace(
            go.Scattergeo(
                lat=[row['lat'], callout_lat],
                lon=[row['lon'], callout_lon],
                mode="lines",
                line=dict(width=2, color="lightgray"),
                showlegend=False,
                hoverinfo='skip'
            )
        )
        
        # Add callout text with background SECOND (so it's on top)
        fig.add_trace(
            go.Scattergeo(
                lat=[callout_lat],
                lon=[callout_lon],
                text=[f"<b>{country}</b><br>{members}"],
                mode="markers+text",
                marker=dict(
                    size=100,  # Adjust size as needed
                    color="white",
                    opacity=0.7,
                    line=dict(width=2, color="white")  # White border
                ),
                textfont=dict(size=26, color="black"),
                textposition="middle center",
                showlegend=False,
                hoverinfo='skip'
            )
        )

# Style the map - white sea, only show member countries
fig.update_geos(
    projection_type="robinson",
    lataxis_range=[-60, 90],
    showland=False,  # Hide all land
    showocean=True,
    oceancolor="white",  # White sea
    showcountries=True,  # Show countries
    countrycolor="white",  # White country borders
    countrywidth=2,  # Border width
    showcoastlines=False,  # Remove coastline outlines
    showframe=False,  # Remove map frame/border
    showlakes=False,  # Remove lake outlines
    showrivers=False  # Remove river outlines
)

# Hide color bar
fig.update_layout(coloraxis_showscale=False)

# Export to PNG with high resolution for print quality
fig.write_image("member_map.png", 
                width=2800,   # Increased width
                height=2000,  # Increased height  
                scale=3)      # 3x scaling for higher DPI (effectively 300 DPI)