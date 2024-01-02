import base64
import itertools
from flask import Flask, render_template, request
import networkx as nx
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# calculate the cost and penalty and sum of them for a path between nodes
def calculate_costs(selected_nodes, graph, penalties):
    total_cost = sum(graph[node][neighbor] for node in selected_nodes for neighbor in graph[node])
    penalty_cost = sum(penalties[node] for node in penalties if node not in selected_nodes)
    objective_value = total_cost + penalty_cost
    return total_cost, penalty_cost, objective_value

# finding the best path between all
def find_best_path(graph, penalties):
    all_nodes = list(graph.keys())
    all_paths = itertools.permutations(all_nodes)

    best_path = None
    best_objective_value = float('inf')
    # for all paths compare the sum of penalties and costs and select the best and then return it
    for path in all_paths:
        total_cost, penalty_cost, objective_value = calculate_costs(path, graph, penalties)

        if objective_value < best_objective_value:
            best_path = path
            best_objective_value = objective_value

    return best_path

# draw the graph
def draw_graph(graph, selected_nodes):
    G = nx.Graph(graph)
    pos = nx.spring_layout(G)

    plt.figure(figsize=(8, 6))
    # first draw the graph with nodes and edges in blue
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, font_size=12, font_color='black')
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='blue')
    # now make the selected path color red
    selected_edges = [(selected_nodes[i], selected_nodes[i + 1]) for i in range(len(selected_nodes) - 1)]
    nx.draw_networkx_edges(G, pos, edgelist=selected_edges, edge_color='red', width=2)

    plt.axis('off')

    # make an image of the graph and convert the plot to an image for embedding in the HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    encoded_img = base64.b64encode(img.getvalue()).decode('utf-8')

    return f'<img class="center" style="width:100%;height:100%;display:block" src="data:image/png;base64,{encoded_img}" alt="Graph Visualization">'



@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        # Extract user input from the form
        selected_nodes = request.form.getlist('selected_nodes')
        first = selected_nodes[0].replace("'", "")
        second = first.split(',')
        selected_nodes = second
        # make the graph
        graph = {
            'A': {'B': int(request.form['AB']), 'D': int(request.form['AD']), 'C': int(request.form['AC'])},
            'B': {'A': int(request.form['AB']), 'C': int(request.form['BC']), 'D': int(request.form['BD'])},
            'C': {'A': int(request.form['AC']), 'B': int(request.form['BC']), 'D': int(request.form['CD'])},
            'D': {'A': int(request.form['AD']), 'B': int(request.form['BD']), 'C': int(request.form['CD'])}
        }
        penalties = {
            'A': int(request.form['penalty_A']),
            'B': int(request.form['penalty_B']),
            'C': int(request.form['penalty_C']),
            'D': int(request.form['penalty_D'])
        }
        if len(selected_nodes) < 2:
            # if less than 2 nodes are selected, it returns an error
            result = "Please select nodes!"
            return render_template('result.html', result=result)
        else:
            # else, calculate costs
            best_path = find_best_path(graph, penalties)
            total_cost, penalty_cost, objective_value = calculate_costs(best_path, graph, penalties)
            graph_html = draw_graph(graph, best_path)
            # prepare result
            result = {
                'selected_nodes': selected_nodes,
                'total_cost': total_cost,
                'penalty_cost': penalty_cost,
                'objective_value': objective_value,
                'graph_html': graph_html
            }
            # show result in result.html
            return render_template('result.html', result=result)
    # render the input form page with the result
    if request.method == 'GET':
        return render_template('index.html')
    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
