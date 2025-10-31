from dash import html
import dash_cytoscape as cyto

def calculate_text_width(text: str, font_size: int = 14) -> int:
    avg_char_width = font_size * 0.6
    return max(len(text) * avg_char_width + 40, 80)

def calculate_node_dimensions(label: str, node_type: str):
    base_font_size = {"user": 12, "server": 11, "me": 16}[node_type]
    width = calculate_text_width(label, base_font_size)
    height = {"user": 40, "server": 50, "me": 60}[node_type]
    return width, height


def create_stylesheet():
    return [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "text-valign": "center",
                "text-halign": "center",
                "text-wrap": "wrap",
                "text-max-width": "data(width)",
                "font-family": "ui-sans-serif, system-ui, sans-serif",
                "font-weight": "500",
                "width": "data(width)",
                "height": "data(height)",
                "border-width": "3px",
                "color": "#ffffff",
                "text-outline-width": "1px",
                "text-outline-color": "#000000",
                "background-opacity": "0.9",
                "transition-property": "background-color, border-color, width, height",
                "transition-duration": "0.3s",
                "shape": "round-rectangle",
                "border-radius": "12px",
            },
        },
        {
            "selector": "[group = 'user']",
            "style": {
                "background-color": "#5865F2",
                "border-color": "#5865F2",
                "font-size": "12px",
                "color": "#ffffff",
                "text-outline-width": "0px",
                "font-weight": "600",
            },
        },

        # Server nodes (Discord Green theme)
        {
            "selector": "[group = 'server']",
            "style": {
                "background-color": "#10b981",
                "border-color": "#059669",
                "color": "#ffffff",
                "font-size": "11px",
                "text-outline-width": "0px",
                "font-weight": "600",
            },
        },

        # Me node (Discord Red theme)
        {
            "selector": "[group = 'me']",
            "style": {
                "background-color": "#ef4444",
                "border-color": "#dc2626",
                "font-size": "15px",
                "color": "#ffffff",
                "text-outline-width": "0px",
                "font-weight": "700",
                "border-width": "4px",
            },
        },

        # Base edge styling
        {
            "selector": "edge",
            "style": {
                "width": "3px",
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "arrow-scale": "1.5",
                "transition-property": "line-color, target-arrow-color, width",
                "transition-duration": "0.3s",
            },
        },

        # Membership edges (user -> server)
        {
            "selector": "[edge_type = 'membership']",
            "style": {
                "line-color": "#3b82f6",
                "target-arrow-color": "#3b82f6",
                "line-style": "solid",
            },
        },

        # Connection edges (server -> me)
        {
            "selector": "[edge_type = 'connection']",
            "style": {
                "line-color": "#10b981",
                "target-arrow-color": "#10b981",
                "line-style": "dashed",
                "line-dash-pattern": [10, 5],
            },
        },

        # Hover effects
        {
            "selector": "node:active",
            "style": {
                "overlay-opacity": "0.2",
                "overlay-color": "#ffffff",
            },
        },

        # Highlighted nodes and edges
        {
            "selector": ".highlighted-node",
            "style": {
                "border-color": "#fbbf24",
                "border-width": "4px",
                "background-color": "#fef3c7",
                "color": "#000000",
                "text-outline-color": "#f59e0b",
                "z-index": "10",
            },
        },

        {
            "selector": ".highlighted-edge",
            "style": {
                "line-color": "#fbbf24",
                "target-arrow-color": "#fbbf24",
                "width": "5px",
                "opacity": "1",
                "z-index": "5",
            },
        },

        # Dimmed elements during highlighting
        {
            "selector": ".dimmed",
            "style": {
                "opacity": "0.3",
            },
        },
    ]

def build_dash_layout(elements, stylesheet):
    return html.Div([
        html.Div([
            html.Div([
                cyto.Cytoscape(
                    id="discord-graph",
                    elements=elements,
                    layout={
                        "name": "preset",
                        "fit": True,
                        "padding": 20,
                    },
                    style={
                        "width": "100%",
                        "height": "100vh",
                        "backgroundColor": "#1f2937",
                        "border": "none",
                    },
                    stylesheet=stylesheet,
                    responsive=True,
                    boxSelectionEnabled=False,
                    wheelSensitivity=0.3,
                    zoomingEnabled=True,
                    panningEnabled=True,
                    minZoom=0.3,
                    maxZoom=3.0,
                    zoom=1.0,
                    autoungrabify=False,
                    userZoomingEnabled=True,
                    userPanningEnabled=True,
                )
            ], style={
                "flex": "1",
                "height": "100vh",
            }),

            # Right side - Info panel
            html.Div([
                html.Div([
                    html.Button("Deselect Node", id="deselect-button", n_clicks=0, style={
                        "width": "100%",
                        "padding": "0.5rem",
                        "margin": "1rem 0",
                        "backgroundColor": "#374151",
                        "color": "#f9fafb",
                        "border": "none",
                        "borderRadius": "0.375rem",
                        "cursor": "pointer",
                    }),
                ], style={"padding": "0 1.5rem 0 1.5rem"}),
                html.Div(id="node-info", children=[
                    html.H3("Guide", style={
                        "margin": "0 0 1rem 0",
                        "color": "#f9fafb",
                        "fontSize": "1.125rem",
                        "fontWeight": "600",
                    }),
                    html.Div([
                        html.P("Click any node to see connections",
                              style={"margin": "0 0 0.75rem 0", "color": "#9ca3af", "fontSize": "0.875rem"}),
                        html.P("Blue = Users",
                              style={"margin": "0 0 0.5rem 0", "color": "#3b82f6", "fontSize": "0.875rem", "fontWeight": "500"}),
                        html.P("Green = Servers",
                              style={"margin": "0 0 0.5rem 0", "color": "#10b981", "fontSize": "0.875rem", "fontWeight": "500"}),
                        html.P("Red = You",
                              style={"margin": "0 0 1rem 0", "color": "#ef4444", "fontSize": "0.875rem", "fontWeight": "500"}),
                    ]),
                    html.Hr(style={"border": "none", "borderTop": "1px solid #374151", "margin": "1rem 0"}),
                ], style={
                    "padding": "1.5rem",
                    "height": "100vh",
                    "overflowY": "auto",
                    "fontSize": "0.875rem",
                    "scrollbarWidth": "thin",
                })
            ], style={
                "width": "300px",
                "backgroundColor": "#111827",
                "borderLeft": "1px solid #374151",
                "flexShrink": "0",
            }),
        ], style={
            "display": "flex",
            "height": "calc(100vh - 80px)",
        }),

    ], style={
        "backgroundColor": "#111827",
        "height": "100vh",
        "fontFamily": "ui-sans-serif, system-ui, sans-serif",
        "overflow": "hidden",
    })

def create_graph_elements(users_to_servers):
    elements = []
    users = list(users_to_servers.keys())
    servers = sorted({srv for lst in users_to_servers.values() for srv in lst})
    # Calculate layout positions
    max_nodes_column = max(len(users), len(servers))
    vertical_spacing = max(70, 800 / max_nodes_column) if max_nodes_column > 0 else 100

    # Add user nodes (left column)
    user_start_y = (1200 - (len(users) - 1) * vertical_spacing) / 2
    for i, user in enumerate(users):
        width, height = calculate_node_dimensions(user, "user")
        elements.append({
            "data": {
                "id": user,
                "label": user,
                "group": "user",
                "width": width,
                "height": height,
                "connections": len(users_to_servers[user])
            },
            "position": {"x": -500, "y": user_start_y + i * vertical_spacing},
        })

    # Add server nodes (middle column)
    server_start_y = (1200 - (len(servers) - 1) * vertical_spacing) / 2
    for i, server in enumerate(servers):
        width, height = calculate_node_dimensions(server, "server")
        user_count = sum(1 for user_servers in users_to_servers.values() if server in user_servers)
        elements.append({
            "data": {
                "id": server,
                "label": server,
                "group": "server",
                "width": width,
                "height": height,
                "user_count": user_count
            },
            "position": {"x": 600, "y": server_start_y + i * vertical_spacing},
        })

    me_width, me_height = calculate_node_dimensions("You", "me")
    elements.append({
        "data": {
            "id": "Me",
            "label": "You",
            "group": "me",
            "width": me_width,
            "height": me_height,
            "total_servers": len(servers)
        },
        "position": {"x": 1100, "y": 500},
    })

    # Add edges: user -> server
    for user, server_list in users_to_servers.items():
        for server in server_list:
            elements.append({
                "data": {
                    "id": f"{user}-{server}",
                    "source": user,
                    "target": server,
                    "edge_type": "membership"
                }
            })

    # Add edges: server -> Me
    for server in servers:
        elements.append({
            "data": {
                "id": f"{server}-Me",
                "source": server,
                "target": "Me",
                "edge_type": "connection"
            }
        })

    return elements
