import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import numpy as np

# Load data
df = pd.read_csv('ecoaldeas_red02.csv')

# Helper to get info for a given row
def get_info(row):
    return {
        'nombre': row['nombre'],
        'ubicacion': row['ubicacion'],
        'provincia': row['provincia'],
        'idea_general_en': row['idea_general_en'],
        'enlace': row['enlace'],
        'imagen': row['imagen'],
        'descripcion_en': row['descripcion_en'],
        'coordenadas': row['coordenadas']
    }

# Parse coordinates
def parse_coords(coord_str):
    try:
        lat, lon = map(float, coord_str.split(','))
        return lat, lon
    except:
        return None, None

# Find closest marker to a lat/lon
def closest_marker(lat, lon, df):
    coords = df['coordenadas'].apply(parse_coords)
    arr = np.array([c for c in coords if c[0] is not None and c[1] is not None])
    if len(arr) == 0:
        return 0
    dists = np.sqrt((arr[:,0] - lat)**2 + (arr[:,1] - lon)**2)
    idx = dists.argmin()
    # Map back to original df index (in case of missing coords)
    valid_idx = [i for i, c in enumerate(coords) if c[0] is not None and c[1] is not None]
    return valid_idx[idx]

# Sidebar for selection (hidden, used for state)
if 'selected_idx' not in st.session_state:
    st.session_state['selected_idx'] = 0

def select_marker(idx):
    st.session_state['selected_idx'] = idx

# Layout
st.set_page_config(layout="wide")
left, right = st.columns([2, 1], gap="large")

with left:
    # st.markdown("## Ecovillages Map")
    # Center map on first row by default
    lat0, lon0 = parse_coords(df.iloc[0]['coordenadas'])
    if lat0 is None or lon0 is None:
        lat0, lon0 = 40.0, -4.0  # Default to center of Spain
    m = folium.Map(
        location=[lat0, lon0],
        zoom_start=6
    )
    for idx, row in df.iterrows():
        lat, lon = parse_coords(row['coordenadas'])
        if lat is None or lon is None:
            continue
        # Set marker color based on 'active_Y/N' column
        marker_color = 'green' if row.get('active_Y/N', 'N') == 'Y' else 'red'
        # Add marker with unique id in popup
        popup_html = f"""
        <b>{row['nombre']}</b><br><br>
        {row['ubicacion']}, {row['provincia']}<br>
        {row['idea_general_en']}<br>
        <a href='{row['enlace']}' target='_blank'>{row['enlace']}</a><br>
        <span style='display:none' id='marker_id'>{idx}</span>
        """
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=14,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.5,
            opacity=0.5
        )
        marker.add_child(folium.Popup(popup_html, max_width=300))
        marker.add_to(m)
    # Render map and capture click
    map_data = st_folium(m, width=900, height=700)
    # If a marker is clicked, update selected_idx to the closest marker (by coordinates)
    if map_data:
        # If a marker popup is opened, get its coordinates
        if map_data.get('last_object_clicked'):
            marker_lat = map_data['last_object_clicked']['lat']
            marker_lon = map_data['last_object_clicked']['lng']
            idx = closest_marker(marker_lat, marker_lon, df)
            st.session_state['selected_idx'] = idx
        # If map is clicked (not marker), fallback to previous logic
        elif map_data.get('last_clicked'):
            click_lat = map_data['last_clicked']['lat']
            click_lon = map_data['last_clicked']['lng']
            idx = closest_marker(click_lat, click_lon, df)
            st.session_state['selected_idx'] = idx

# Right panel: split vertically
with right:
    FrameImg, FrameTxt = st.container(), st.container()
    info = get_info(df.iloc[st.session_state['selected_idx']])
    with FrameImg:
        st.markdown(f"<div style='width:100%;height:300px;overflow:hidden;display:flex;align-items:center;justify-content:center;'><img src='{info['imagen']}' style='width:100%;object-fit:cover;'/></div>", unsafe_allow_html=True)
    with FrameTxt:
        st.markdown(f"<div style='padding:1em;'><b>{info['nombre']}</b><br><br>{info['descripcion_en']}</div>", unsafe_allow_html=True)