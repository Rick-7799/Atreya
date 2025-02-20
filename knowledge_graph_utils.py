import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def load_disease_herb_data(disease_herb_relationships.csv):
    data = pd.read_csv(disease_herb_relationships.csv)
    return data

def create_knowledge_graph(data):
    G = nx.Graph()
    for _, row in data.iterrows():
        disease = row['Disease']  
        herb = row['Herb']        
        G.add_node(disease, type='disease')
        G.add_node(herb, type='herb')
        G.add_edge(disease, herb)
    return G

def visualize_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10, font_color='black', font_weight='bold', edge_color='gray')
    plt.title("Disease-Herb Knowledge Graph")
    plt.axis('off')
    plt.show()

def save_graph(G, file_path):
    nx.write_gml(G, file_path)
    print(f"Knowledge graph saved to {file_path}")

if __name__ == "__main__":
    file_path = 'data/disease_herb_relationships.csv'
    data = load_disease_herb_data(file_path)
    
    G = create_knowledge_graph(data)
    
    visualize_graph(G)
    
    save_graph(G, 'models/disease_herb_knowledge_graph.gml')
