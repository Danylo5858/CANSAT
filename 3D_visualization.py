import numpy as np
import plotly.graph_objects as go

height = 0.12
radio = 0.065

theta = np.linspace(0, 2*np.pi, 50)
z = np.linspace(-height/2, height/2, 50)
Theta, Z = np.meshgrid(theta, z)
X = radio * np.cos(Theta)
Y = radio * np.sin(Theta)

fig = go.Figure()

fig.add_trace(go.Surface(
    x=X,
    y=Y,
    z=Z,
    colorscale=[[0, 'steelblue'], [1, 'steelblue']],
    showscale=False,
    contours={
        "x": {"show": False},
        "y": {"show": False},
        "z": {"show": False}
    },
    lighting=dict(ambient=1, diffuse=0, specular=0),
    hoverinfo='skip'
))

camera = dict(
    eye=dict(x=1.5, y=1.5, z=0.5),
    center=dict(x=0, y=0, z=0),
    up=dict(x=0, y=0, z=1)
)

fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data',
        dragmode='turntable',
        camera=camera
    ),
    title="Satélite",
    margin=dict(l=0, r=0, t=0, b=0)
)

fig.show()
