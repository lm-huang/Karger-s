# Minimum Cut Visualization Tool

This is a web-based tool for visualizing and understanding Karger's Minimum Cut algorithm. The tool allows users to generate random graphs and step through the process of finding the minimum cut in a graph. The steps of the algorithm are visualized, showing which edges are contracted and how the graph evolves.

## Features

- **Graph Generation**: Allows users to specify the number of nodes and edges for the graph.
- **Step-by-Step Visualization**: Displays each step of Karger's algorithm, including edge contraction and the resulting graph after each contraction.
- **Previous/Next Step Navigation**: Allows users to navigate through the algorithm’s steps to see the progress of the graph.
- **Minimum Cut Result**: After all steps, the tool displays the final result, showing the two partitions of the graph and the edges that were cut.

## Installation

### Prerequisites

- Python 3.7 or higher
- Pip (Python package installer)

### Required Libraries

Install the required libraries by running the following command:

```
pip install dash networkx plotly dash-bootstrap-components
```

## Running the App

1. Clone or download the project repository.
2. Navigate to the project directory in the terminal.
3. Run the Dash app with the following command:

```
python app.py
```

1. Open a web browser and go to `http://127.0.0.1:8050/` to view the tool.

## Usage

1. **Enter Number of Nodes and Edges**:
   - Set the number of nodes and edges for the graph using the input fields.
2. **Generate Graph**:
   - Click on the "Generate Graph" button to generate a random graph with the specified number of nodes and edges.
3. **Step Through the Algorithm**:
   - After generating the graph, use the "Next Step" and "Previous Step" buttons to step through the minimum cut algorithm.
   - The graph will be updated to show the contracted edges at each step.
4. **View Final Result**:
   - After completing the steps, the final result will show the two partitions of the graph, and the edges that form the minimum cut.

## Features in Detail

- **Graph Visualization**: The graph is visualized using Plotly, with nodes represented as points and edges as lines. The color of the edges changes to reflect the contracted edges (red for contracted edges, blue for the current edge being contracted, and gray for other edges).
- **Step Information**: The current step and the edge to be contracted are displayed. After completing all steps, the minimum cut result is displayed, showing which nodes belong to each partition and the cut edges.

## Karger’s Minimum Cut Algorithm

The tool implements Karger’s Minimum Cut Algorithm, which works as follows:

- Randomly pick an edge and contract it, merging the two nodes into one.
- Repeat the process until only two nodes remain.
- The edges that connect the two final nodes are the minimum cut of the graph.

## Notes

- The tool allows for an arbitrary number of nodes and edges, but keep in mind that the random graph generation may sometimes create disconnected graphs, which may affect the results of the algorithm.
- The visualization updates in real time as you step through the algorithm, showing the graph’s evolution.