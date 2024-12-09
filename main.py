from dash import Dash, html, dcc, Input, Output, State, ctx
import networkx as nx
import random
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Create the Dash app
app = Dash(__name__, external_stylesheets=[
    dbc.themes.LITERA
])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Minimum Cut Visualization Tool", className="text-center text-dark"))),

    # Number of Nodes and Edges Inputs
    dbc.Row([
        dbc.Col(html.Label("Number of Nodes:", className="text-dark")),
        dbc.Col(dcc.Input(id='node-count', type='number', value=5, min=2, step=1, className="form-control")),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col(html.Label("Number of Edges:", className="text-dark")),
        dbc.Col(dcc.Input(id='edge-count', type='number', value=7, min=1, step=1, className="form-control")),
    ], className="mb-3"),

    # Generate Graph Button
    dbc.Row(
        dbc.Col(dbc.Button("Generate Graph", id='generate-graph', n_clicks=0, color="primary", style={"width": "100%"},
                           className="btn-lg")),
        className="mt-4"
    ),

    # Step info display with black, white, and gray color scheme
    html.Div(id="step-info", style={
        "margin-top": "20px",
        "font-size": "20px",
        "font-weight": "bold",
        "font-family": "Arial, sans-serif",
        "color": "#333",  # dark gray text
        "background-color": "#f0f0f0",  # light gray background
        "padding": "15px",
        "border-radius": "5px",
        "border": "1px solid #ccc",  # soft gray border
        "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",  # soft shadow
        "text-align": "center",
    }),

    # Graph Visualization
    dcc.Graph(id='graph-visualization'),

    dbc.Row(
        [
            dbc.Col(
                dbc.Button("Previous Step", id='prev-step', n_clicks=0, style={"margin-right": "10px", "width": "100%"},
                           color="dark", className="btn-lg")),
            dbc.Col(dbc.Button("Next Step", id='next-step', n_clicks=0, style={"width": "100%"}, color="dark",
                               className="btn-lg")),
        ],
        style={"margin-top": "20px"}
    ),

    # Result Info Display with dark gray color
    html.Div(id="result-info", style={
        "margin-top": "20px",
        "color": "#333",  # dark gray text
        "font-size": "18px",
        "font-weight": "normal",
        "font-family": "Arial, sans-serif",
        "text-align": "center",
    })

], style={"background-color": "#fafafa", "padding": "20px"})

# Global variables
graph = None
steps = []
current_step = 0
min_cut = 0
set1 = []
set2 =[]

layout_cache = {}
# Create graph visualization layout
# def create_graph_figure(G, next_edge=None, cut_edges=None):
#     pos = nx.spring_layout(G)
#     edge_trace = []
#     node_trace = go.Scatter(
#         x=[],
#         y=[],
#         text=[],
#         mode='markers+text',
#         marker=dict(size=10, color='darkblue', line=dict(width=2)),
#         textposition="top center"
#     )
#
#     for node in G.nodes():
#         x, y = pos[node]
#         node_trace['x'] += (x,)
#         node_trace['y'] += (y,)
#         node_trace['text'] += (str(node),)
#
#     for edge in G.edges():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         color = 'red' if cut_edges and edge in cut_edges else 'blue' if next_edge == edge else 'gray'
#         edge_trace.append(go.Scatter(
#             x=[x0, x1, None],
#             y=[y0, y1, None],
#             line=dict(width=2, color=color),
#             mode='lines'
#         ))
#
#     fig = go.Figure(data=edge_trace + [node_trace])
#     fig.update_layout(showlegend=False)
#     fig.update_xaxes(showgrid=False, zeroline=False)
#     fig.update_yaxes(showgrid=False, zeroline=False)
#     fig.update_layout(
#         plot_bgcolor="white",
#         title="Graph Visualization",
#         margin=dict(l=0, r=0, t=40, b=0)
#     )
#     return fig

def create_graph_figure(G, next_edge=None, cut_edges=None):

    graph_hash = hash(frozenset(G.edges()))
    if graph_hash in layout_cache:
        pos = layout_cache[graph_hash]
    else:
        pos = nx.spring_layout(G, seed=42)
        layout_cache[graph_hash] = pos

    edge_trace = []
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        marker=dict(size=10, color='darkblue', line=dict(width=2)),
        textposition="top center"
    )

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['text'] += (str(node),)

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        color = 'red' if cut_edges and edge in cut_edges else 'blue' if next_edge == edge else 'gray'
        edge_trace.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=2, color=color),
            mode='lines'
        ))

    fig = go.Figure(data=edge_trace + [node_trace])
    fig.update_layout(showlegend=False)
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    fig.update_layout(
        plot_bgcolor="white",
        title="Graph Visualization",
        margin=dict(l=0, r=0, t=40, b=0)
    )

    return fig

def contracted_edge(G, edge):
    a, b = edge
    H = G.copy()
    edges_to_remap = list(H.edges(b))
    print("b's edges:",edges_to_remap)
    H.remove_node(b)

    for u, v in edges_to_remap:
        if u == b:
            u = a
        if v == b:
            v = a
        if {u, v} == {a, b}:
            continue

        if not H.has_edge(u, v):
            H.add_edge(u, v)

    return H

# Karger's Minimum Cut Algorithm
def karger_min_cut(G):
    steps = []
    cut = set([])
    node_map = {node: {node} for node in G.nodes}
    H = G.copy()
    while len(G.nodes) > 2:
        edge = random.choice(list(G.edges()))
        u, v = edge
        steps.append((G.copy(), edge))
        node_map[u] = node_map[u].union(node_map[v])
        node_map.pop(v)
        G = contracted_edge(G, edge)
    steps.append((G.copy(),list(G.edges)[0]))

    list1, list2 = list(node_map.values())
    set1 = set(list1)
    set2 = set(list2)

    for a, b in H.edges():
        if ((a in set1 and b in set2) or (a in set2 and b in set1)) and tuple([b, a]) not in cut:
            cut.add((a, b))

    print(steps)
    print(node_map)
    return steps, len(cut), set1, set2

@app.callback(
    Output('graph-visualization', 'figure'),
    Output('step-info', 'children'),
    Output('result-info', 'children'),
    Output('next-step', 'disabled'),
    Output('prev-step', 'disabled'),
    Input('generate-graph', 'n_clicks'),
    Input('next-step', 'n_clicks'),
    Input('prev-step', 'n_clicks'),
    State('node-count', 'value'),
    State('edge-count', 'value'),
    prevent_initial_call=True
)
def update_graph(generate_clicks, next_clicks, prev_clicks, node_count, edge_count):
    #next_step 禁用状态  prev_step 禁用状态
    global graph, steps, current_step, min_cut, set1, set2
    ctx_triggered = ctx.triggered_id

    if ctx_triggered == 'generate-graph':
        # Generate a random graph
        graph = nx.gnm_random_graph(node_count, edge_count)
        steps, min_cut, set1, set2 = karger_min_cut(graph.copy())
        current_step = 0
        # Display the first step (edge to be contracted)
        if steps:
            next_edge = steps[current_step][1]
            step_info = f"Step 1: Contract the edge {next_edge}"
        else:
            next_edge = None
            step_info = ""
      #  print("kaishi de current_step", current_step)
        return create_graph_figure(graph, next_edge=next_edge), step_info, "", False, True


    elif ctx_triggered == 'next-step':
        if current_step < len(steps):
            current_step += 1
            if current_step == len(steps):
                G, _ = steps[0]
                step_info = f"Cut number is {min_cut}. We have nodes: {set1} in a set and nodes: {set2} in the other"
                return create_graph_figure(G, next_edge=""), step_info, "", True, False
            G, edge = steps[current_step]
            # Update step info to show the next edge to be contracted
            step_info = f"Step {current_step + 1}: Contract the edge {edge}"
            if current_step == len(steps):
                # Final result
                nodes = list(G.nodes)
                cut_edges = list(graph.edges - G.edges)
                result_info = f"Minimum Cut Result: Nodes {nodes[0]} and {nodes[1]} belong to two partitions, with {len(cut_edges)} cut edges"
                return create_graph_figure(graph, cut_edges=cut_edges), step_info, result_info, True, False
            return create_graph_figure(G, next_edge=steps[current_step][1] if current_step < len(steps) else None), step_info, "", False, False


    elif ctx_triggered == 'prev-step':
        if current_step > 1:
            current_step -= 1
            G, edge = steps[current_step]
            # Update step info to show the previous edge contracted
            step_info = f"Step {current_step + 1}: Contract the edge {edge}"
            return create_graph_figure(G, next_edge=edge), step_info, "", False, False
        elif current_step == 1:
            current_step -=1
            G, edge = steps[current_step]
            step_info = f"Step {current_step + 1}: Contract the edge {edge}"
            return create_graph_figure(G, next_edge=edge), step_info, "", False, True

    return create_graph_figure(graph), "No more steps to process", "", current_step == len(steps), current_step == 0

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)