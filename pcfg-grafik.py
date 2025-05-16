import graphviz

def export_pcfg_to_dot(pcfg, filepath):
    dot = graphviz.Digraph()
    for rule in pcfg:
        lhs = rule['lhs']
        rhs = ' '.join(rule['rhs'])
        prob = rule['probability']
        dot.edge(lhs, rhs, label=f'{prob:.2f}')
    dot.render(filepath, format='png', cleanup=True)

