import dash
from dash import html, callback_context
from dash.dependencies import Input, Output, State
from dashboard import create_stylesheet, build_dash_layout, create_graph_elements

def remap_servers_to_adjacency_matrix(mutual_servers):
    users_to_servers = {}
    for server_name, members in mutual_servers.items():
        for member_name, info in members.items():
            # Remove everything after and including the hashtag
            clean_name = member_name.split('#')[0]
            if clean_name not in users_to_servers:
                users_to_servers[clean_name] = set()
            users_to_servers[clean_name].add(server_name)
            users_to_servers[clean_name].update(info.get("mutual_servers", []))
    users_to_servers = {user: sorted(list(servers)) for user, servers in users_to_servers.items()}
    return users_to_servers

def create_app(users_to_servers):
    app = dash.Dash(__name__)
    app.title = "Discord Connections"
    elements = create_graph_elements(users_to_servers)
    stylesheet = create_stylesheet()
    app.layout = build_dash_layout(elements, stylesheet)

    @app.callback(
        [Output("discord-graph", "stylesheet"), Output("node-info", "children")],
        [Input("discord-graph", "tapNodeData"), Input("deselect-button", "n_clicks")],
        [State("discord-graph", "elements")]
    )
    def update_graph_on_node_click(clicked_node_data, n_clicks, elements):
        base_stylesheet = create_stylesheet()
        ctx = callback_context
        triggered = ctx.triggered[0]["prop_id"] if ctx.triggered else None

        # If deselect button was clicked, clear selection, restore base
        if triggered and triggered.startswith("deselect-button"):
            info_content = [
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
                html.H4("Stats", style={
                    "margin": "0 0 0.75rem 0",
                    "color": "#f9fafb",
                    "fontSize": "1rem",
                    "fontWeight": "600",
                }),
                html.P(f"Users: {len(users_to_servers)}",
                      style={"margin": "0 0 0.5rem 0", "color": "#9ca3af", "fontSize": "0.875rem"}),
                html.P(f"Servers: {len({srv for lst in users_to_servers.values() for srv in lst})}",
                      style={"margin": "0 0 0.5rem 0", "color": "#9ca3af", "fontSize": "0.875rem"}),
                html.P(f"Connections: {sum(len(servers) for servers in users_to_servers.values())}",
                      style={"margin": "0", "color": "#9ca3af", "fontSize": "0.875rem"}),
            ]
            return base_stylesheet, info_content

        if not clicked_node_data:
            info_content = [
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
                html.H4("Servers", style={
                    "margin": "0 0 0.75rem 0",
                    "color": "#f9fafb",
                    "fontSize": "1rem",
                    "fontWeight": "600",
                }),
                html.Div([
                    *[html.Div([
                        html.P(server, style={
                            "margin": "0",
                            "color": "#10b981",
                            "fontSize": "0.875rem",
                            "fontWeight": "500",
                        }),
                        html.P(f"{sum(1 for user_servers in users_to_servers.values() if server in user_servers)} members",
                              style={"margin": "0", "color": "#6b7280", "fontSize": "0.5rem"}),
                    ], style={
                        "padding": "0.5rem",
                        "margin": "0 0 0.5rem 0",
                        "backgroundColor": "#1f2937",
                        "borderRadius": "0.375rem",
                        "border": "1px solid #374151",
                        "cursor": "pointer",
                    }) for server in sorted({srv for lst in users_to_servers.values() for srv in lst})],
                ]),
                html.H4("Stats", style={
                    "margin": "0 0 0.75rem 0",
                    "color": "#f9fafb",
                    "fontSize": "1rem",
                    "fontWeight": "600",
                }),
            ]
            return base_stylesheet, info_content

        selected_id = clicked_node_data["id"]
        selected_group = clicked_node_data["group"]

        # Find   nodes
        connected_nodes = set()
        connected_edges = set()

        for element in elements:
            if "source" in element["data"] and "target" in element["data"]:
                source, target = element["data"]["source"], element["data"]["target"]
                edge_id = element["data"]["id"]

                if source == selected_id:
                    connected_nodes.add(target)
                    connected_edges.add(edge_id)
                elif target == selected_id:
                    connected_nodes.add(source)
                    connected_edges.add(edge_id)

        # Create highlighting styles
        highlighting_styles = []

        # Highlight selected node
        highlighting_styles.append({
            "selector": f"node[id = '{selected_id}']",
            "style": {
                "border-color": "#FEE75C",
                "border-width": "6px",
                "background-color": "#FFEBB3",
                "color": "#000000",
                "text-outline-color": "#FEE75C",
                "z-index": "10",
            }
        })

        # Highlight connected nodes
        for node_id in connected_nodes:
            highlighting_styles.append({
                "selector": f"node[id = '{node_id}']",
                "style": {
                    "border-color": "#FEE75C",
                    "border-width": "4px",
                    "z-index": "8",
                }
            })

        for edge_id in connected_edges:
            highlighting_styles.append({
                "selector": f"edge[id = '{edge_id}']",
                "style": {
                    "line-color": "#FEE75C",
                    "target-arrow-color": "#FEE75C",
                    "width": "5px",
                    "opacity": "1",
                    "z-index": "5",
                }
            })
        all_node_ids = {elem["data"]["id"] for elem in elements if "source" not in elem["data"]}
        unconnected_nodes = all_node_ids - connected_nodes - {selected_id}
        for node_id in unconnected_nodes:
            highlighting_styles.append({
                "selector": f"node[id = '{node_id}']",
                "style": {"opacity": "0.3"}
            })

        # Create info content based on selected node
        if selected_group == "user":
            servers = users_to_servers.get(selected_id, [])
            info_content = [
                html.H3(selected_id, style={
                    "margin": "0 0 1rem 0",
                    "color": "#3b82f6",
                    "fontSize": "1.125rem",
                    "fontWeight": "600",
                }),
                html.P(f"Member of {len(servers)} servers:",
                      style={"margin": "0 0 0.75rem 0", "color": "#f9fafb", "fontSize": "0.875rem", "fontWeight": "500"}),
                html.Div([
                    *[html.P(server, style={
                        "margin": "0 0 0.5rem 0",
                        "color": "#10b981",
                        "fontSize": "0.875rem",
                        "paddingLeft": "0.5rem",
                    }) for server in servers],
                ])
            ]
        elif selected_group == "server":
            members = [user for user, servers in users_to_servers.items() if selected_id in servers]
            info_content = [
                html.H3(selected_id, style={
                    "margin": "0 0 1rem 0",
                    "color": "#10b981",
                    "fontSize": "1.125rem",
                    "fontWeight": "600",
                }),
                html.P(f"{len(members)} members:",
                      style={"margin": "0 0 0.75rem 0", "color": "#f9fafb", "fontSize": "0.875rem", "fontWeight": "500"}),
                html.Div([
                    *[html.P(member, style={
                        "margin": "0 0 0.5rem 0",
                        "color": "#3b82f6",
                        "fontSize": "0.875rem",
                        "paddingLeft": "0.5rem",
                    }) for member in members],
                ])
            ]
        else:
            total_servers = len({srv for lst in users_to_servers.values() for srv in lst})
            total_users = len(users_to_servers)
            info_content = [
                html.H3("You", style={
                    "margin": "0 0 1rem 0",
                    "color": "#ef4444",
                    "fontSize": "1.125rem",
                    "fontWeight": "600",
                }),
                html.P(f"Connected to {total_servers} users through {total_users} servers",
                      style={"margin": "0 0 0.75rem 0", "color": "#f9fafb", "fontSize": "0.875rem"}),
                html.P("Your network reach in Discord",
                      style={"margin": "0", "color": "#9ca3af", "fontSize": "0.875rem", "fontStyle": "italic"}),
            ]
        return base_stylesheet + highlighting_styles, info_content

    return app

def run_web_server(users_to_servers, debug=False):
    app = create_app(users_to_servers)
    app.run(debug=debug, host="0.0.0.0", port=8050)

if __name__ == "__main__":
    import json
    import sys
    json_file = sys.argv[1] if len(sys.argv) > 1 else ''
    if json_file == '':
        print("Please specify a JSON file to load")
        exit(0)

    with open(json_file, 'r') as f:
        mutual_servers = json.load(f)
    users_to_servers = remap_servers_to_adjacency_matrix(mutual_servers)
    run_web_server(users_to_servers, debug=False)
