import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import networkx as nx
from collections import Counter
from pyvis.network import Network
from IPython.core.display import display, HTML

# Read the new CSV file
descriptors_data = pd.read_csv("HEAL CDE Team_CoreMeasures.Study.PI_as of 2024.05-13_forKG.csv")

# Convert DataFrame to a list of lists with all entries as strings
project_data = descriptors_data.astype(str).values.tolist()

# Define a color mapping for each column header
color_map = {
    'Core CDE Measures': '#4b0082',  # Dark Purple
    'Domain': '#dda0dd',            # Light Purple
    'Questionnaire': '#ff1493',     # Dark Pink
    'Study Name': '#1f77b4',        # Blue (if needed)
    'PI Name': '#2ca02c',           # Green (if needed)
    'HEAL Research Program': '#ffb6c1' # Light Pink
}

shape_map = {
    'Core CDE Measures': 'dot',      # Circle
    'Domain': 'ellipse',             # Ellipse
    'Questionnaire': 'square',       # Square
    'HEAL Research Program': 'triangle',  # Triangle
    'Study Name': 'text',            # Text
    'PI Name': 'text'                # Text
}

# Create a Network graph object
net = Network(notebook=True, width="1000px", height="600px", cdn_resources='remote', font_color='white', bgcolor="black", select_menu=True, filter_menu=True)
st.title('Interactive Knowledge Network of HEAL Core CDEs')

# Add description before presenting the knowledge graph
st.markdown("""
This dynamic tool presents a knowledge graph and is designed to help researchers understand [common data elements (CDEs), particularly those that pertain to HEAL](https://heal.nih.gov/data/common-data-elements). The tool allows researchers to explore relationships among CDEs and identify patterns in their use across studies.
            
## Understanding Nodes and Edges

- A **Node** is, essentially, a *noun*. It represents the entities in the graph, such as "Core CDE Measures," "Domain," "Questionnaire," etc. Each node can have various properties like size, color, label, etc.
- An **Edge** is, essentially, a *verb*. It represents the relationships or connections between the nodes, such as a core CDE measure being associated with a particular domain or questionnaire.

## Understanding Pathways
A **Pathway** is, essentially, a *chain*. It represents a sequence of events, influences, or descriptions linking nodes through their edges. Different pathways indicate different patterns, and there can be parallel pathways. Think of a pathway as a series of edges that connect a sequence of nodes, representing a more complex sequence of relationships or interactions.
A pathway might show how a "Core CDE Measure" leads to a "Domain," which then connects to a "Questionnaire," forming a sequence.

- "Core CDE Measure" --> "Domain" --> "Questionnaire"

## Graph Key 

### Node Colors and Shapes:
- `Core CDE Measures`:
  - <span style="color:#4b0082;">&#x25CF;</span> Dark Purple (Circle)
  - **Size**: Proportional to their frequency in the reported CDE use; bigger circles indicate greater usage across studies.
  - **Purpose**: These nodes represent the core measures and are central to the graph.

- `Domain`:
  - <span style="color:#dda0dd;">⬮</span> Light Purple (Ellipse)
  - **Size**: Fixed size.
  - **Purpose**: These nodes categorize different domains within the data.

- `Questionnaire`:
  - <span style="color:#ff1493;">&#x25A0;</span> Dark Pink (Square)
  - **Size**: Fixed size.
  - **Purpose**: These nodes represent various questionnaires.

- `HEAL Research Program`:
  - <span style="color:#ffb6c1;">&#x25B2;</span> Light Pink (Triangle)
  - **Size**: Fixed size.
  - **Purpose**: These nodes represent different programs under the HEAL (Helping to End Addiction Long-term) initiative.

- `Study Name` and `PI Name`:
  - Text (no specific shape)
  - **Size**: Fixed size.
  - **Purpose**: These nodes represent the names of different studies and principal investigators.

### Edges Colors
  - Edges inherit the color of the nodes they connect. For example, an edge connecting a "Core CDE Measures" node (<span style="color:#4b0082;">&#x25CF;</span>) to a "Domain" node (<span style="color:#dda0dd;">⬮</span>) will inherit the color properties **_from_** the connected nodes.
  - For example, if you select the questionnaire (<span style="color:#ff1493;">&#x25A0;</span>), 'PROMIS', you will see:
    - Dark purple edges: connected to 'Core CDE Measures' nodes that are related to 'PROMIS'
    - Light purple edges: connect 'PROMIS' to nodes categorized under 'Domain'
    - Dark pink edges: connect 'PROMIS' to other nodes categorized under 'Questionnaire'
    - Blue edges: connect 'PI names' to other nodes categorized under 'Study names'

## Explore!
This interactive knowledge graph is designed to let researchers highlight and explore individual nodes and their connections. Users can search and navigate through the graph using simple properties like color, shape, and size, easing identification of patterns, relationships, and focal points of interest.
The graph is continually being refined and updated.

For more information on using the filter feature, [explanation below](#selecting-a-node).

            
""", unsafe_allow_html=True)

def create_knowledge_graph(data, columns):
    all_descriptors = [descriptor for entry in data for descriptor in entry if descriptor not in ['nan', '']]
    descriptor_frequency = Counter(all_descriptors)
    max_frequency = max(descriptor_frequency.values())

    added_nodes = set()  # Track added nodes to avoid duplicates and ensure node existence before adding edges
    min_size = 15 # Minimum size for nodes

    for entry in data:
        core_cde_measure = entry[columns.get_loc('Core CDE Measures')]
        if core_cde_measure not in ['nan', '']:
            if core_cde_measure not in added_nodes:
                net.add_node(core_cde_measure, label=core_cde_measure, color=color_map['Core CDE Measures'],
                             size=30 * (descriptor_frequency[core_cde_measure] / max_frequency), shape=shape_map['Core CDE Measures'])
                added_nodes.add(core_cde_measure)

        # Create and connect nodes for each category
        entries_dict = {}
        for key in ['Domain', 'Questionnaire', 'HEAL Research Program', 'Study Name', 'PI Name']:
            entries = entry[columns.get_loc(key)]
            entries_dict[key] = process_entries(entries, key, added_nodes)

        # Create edges between Core CDE Measure and other nodes, and between all other node pairs
        for key, nodes in entries_dict.items():
            for node in nodes:
                net.add_edge(core_cde_measure, node)  # Link Core CDE Measure to each node
                # Link each node to every other node
                for other_key, other_nodes in entries_dict.items():
                    if other_key != key:
                        for other_node in other_nodes:
                            net.add_edge(node, other_node)

    # Configure physics options
    net.set_options("""
    var options = {
        "nodes": {
            "borderWidth": 1,
            "borderWidthSelected": 2,
            "font": {
                "size": 14,
                "color": "white"
            }
        },
        "edges": {
            "color": {
                "inherit": true
            },
            "smooth": {
                "type": "continuous"
            }
        },
        "physics": {
        "enabled": true,
        "stabilization": {
          "enabled": true,
          "iterations": 2000,
          "updateInterval": 100
        },
        "barnesHut": {
          "gravitationalConstant": -100000,
          "centralGravity": 0.02,
          "springLength": 1000,
          "springConstant": 0.02,
          "springStrength": 0.02,  
          "damping": 0.3
        }
      },
      "interaction": {
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)

    # Generate the HTML content as a string
    html_content = net.generate_html()

    # Write the HTML content to a file with utf-8 encoding
    with open('knowledge_graph.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

def process_entries(entries, entry_type, added_nodes):
    item_nodes = []
    if entries not in ['nan', '']:
        items = entries.split(',')
        for item in items:
            item = item.strip()
            if item and item not in added_nodes:
                net.add_node(item, label=item, color=color_map[entry_type],
                             size=15, shape=shape_map[entry_type])  # Fixed size for all other nodes
                added_nodes.add(item)
                item_nodes.append(item)
            elif item:
                item_nodes.append(item)
    return item_nodes

create_knowledge_graph(project_data, descriptors_data.columns)

### If nodes still overlap/graph doesn't run, delete line 162
# try this line of code
# net.repulsion(spring_strength = 0)

# Display the graph in the Streamlit app
html_path = 'knowledge_graph.html'
try:
    with open(html_path, 'r', encoding='utf-8') as HtmlFile:
        html_content = HtmlFile.read()

    components.html(html_content, height=800, width=1000)

except FileNotFoundError:
    st.warning(f"HTML file not found at {html_path}.")
except Exception as e:
    st.error(f"An error occurred while reading the HTML file: {e}")

# Details about filtering 
st.markdown("""
### Selecting a Node

- **Select a Node by ID**:
  - You can use the dropdown menu labeled "Select a Node by ID" to choose a specific node. This will highlight the node and its connections, helping you focus on a particular part of the graph. 
  - See [Guide to Possible Selection Choices below](#guide-to-possible-selection-choices)

- **Select a Network Item (Node)**:
  - When you select "node" from the "Select a network item" dropdown, you can then choose a property and value(s) to filter nodes based on those properties. For example, you might filter nodes to only show those with a specific label or color.

- **Node Properties**:
  - Properties you might filter on include label, color, size, etc.
  - Example: To highlight nodes with a specific research focus area, you can select label and type the specific focus area you're interested in.

### Selecting an Edge

- **Select a Network Item (Edge)**:
  - When you select "edge" from the "Select a network item" dropdown, you can choose properties related to the edges. This is useful for highlighting or filtering specific relationships in the graph.

- **Edge Properties**:
  - Properties for edges might include from (starting node), to (ending node), color, width, etc.
  - Example: You might filter edges to show only those connected to a particular node or of a specific color.

### Filtering and Resetting

- **Filter**:
  - After selecting the node or edge and specifying the properties, clicking the "Filter" button will apply the filter to the graph, highlighting the nodes or edges that match your criteria.

- **Reset Selection**:
  - Clicking "Reset Selection" will clear the current filter, returning the graph to its default state where all nodes and edges are visible.

### Practical Use Case

- Highlight Specific **Nodes**: let's say you want to highlight nodes related to a specific institution. You would:
  - Select "node" from "Select a network item".
  - Choose label from "Select a property".
  - Enter the institution name in "Select value(s)" and click "Filter".

- Highlight Specific **Edges**: to highlight edges to focus on the pathway:
  - Select "edge" from "Select a network item".
  - Choose 'from' or 'to' in "Select a property".
  - As a general rule-of-thumb, selecting:
    - '**to**' allows you to see overlapping CDE use between _research programs_ by selecting the HEAL Research Program names in the 'Select value(s)' section.
    - '**from**' allows you to see overlapping CDE use between _HEAL study name_ by selecting specific study names in the 'Select value(s)' section. 
""")

# Generate and display the guide table for possible selection choices
unique_values = {column: descriptors_data[column].unique().tolist() for column in descriptors_data.columns}
st.title('Guide to Possible Selection Choices')

# Iterate through each column and create a table for its unique values
for column in descriptors_data.columns:
    # Extract unique values for the column, ensuring to drop NaNs
    unique_values = descriptors_data[column].dropna().unique()
    
    # Handle splitting for specific columns like 'Domain'
    if column == 'Domain':
        split_values = []
        for value in unique_values:
            # Split by comma and strip spaces
            split_values.extend([item.strip() for item in value.split(',')])
        # Get unique values from split results
        unique_values = pd.Series(split_values).unique()
    
    # Create a DataFrame for the unique values
    df_unique = pd.DataFrame(unique_values, columns=[column])
    
    # Display a subheader for the column name
    st.subheader(f"Unique values in {column}")
    
    # Display DataFrame as a table
    st.table(df_unique)
