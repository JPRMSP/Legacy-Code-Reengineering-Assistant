import streamlit as st
import ast
import networkx as nx
import matplotlib.pyplot as plt
import io
import sys

st.set_page_config(page_title="Legacy Code Reengineering Assistant", layout="wide")

st.title("Legacy Code Reengineering Assistant")

# --- Step 1: Input Legacy Code ---

st.sidebar.header("Input Legacy Code")
input_method = st.sidebar.radio("Input Method", ("Upload File", "Paste Code"))

code = ""
if input_method == "Upload File":
    uploaded_file = st.sidebar.file_uploader("Upload your legacy Python code file", type=["py"])
    if uploaded_file:
        code = uploaded_file.read().decode("utf-8")
elif input_method == "Paste Code":
    code = st.sidebar.text_area("Paste your legacy Python code here")

if not code.strip():
    st.info("Please upload or paste Python legacy code to start analysis.")
    st.stop()

st.subheader("Legacy Code Input")
st.code(code, language="python")

# --- Backend Analysis Functions ---

def parse_python_functions(source_code):
    """Return list of function names in source code."""
    try:
        tree = ast.parse(source_code)
        funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return funcs
    except Exception as e:
        return []

def find_variable_usage(source_code, var_name):
    """Return sorted list of line numbers where variable/function is used."""
    try:
        tree = ast.parse(source_code)
        lines = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == var_name:
                lines.append(node.lineno)
        return sorted(set(lines))
    except Exception as e:
        return []

def find_long_functions(source_code, length_threshold=10):
    """Return list of tuples (func_name, length) for functions longer than threshold."""
    try:
        tree = ast.parse(source_code)
        long_funcs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # line numbers start at 1
                if node.body:
                    func_len = node.body[-1].lineno - node.body[0].lineno + 1
                    if func_len > length_threshold:
                        long_funcs.append((node.name, func_len))
        return long_funcs
    except Exception as e:
        return []

def build_call_graph(source_code):
    """Build directed graph of function calls."""
    try:
        tree = ast.parse(source_code)
        graph = nx.DiGraph()
        funcs = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        for func_name, func_node in funcs.items():
            graph.add_node(func_name)
            for node in ast.walk(func_node):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    called_func = node.func.id
                    if called_func in funcs:
                        graph.add_edge(func_name, called_func)
        return graph
    except Exception as e:
        return nx.DiGraph()

def plot_call_graph(graph):
    """Plot function call graph using matplotlib and return figure."""
    fig, ax = plt.subplots(figsize=(8,6))
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color="skyblue", edge_color="gray", node_size=2000, font_size=12, ax=ax)
    ax.set_title("Function Call Graph")
    plt.tight_layout()
    return fig

def execute_code_snippet(snippet):
    """Execute a Python snippet safely and capture output/errors."""
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        exec(snippet, {})
        output = redirected_output.getvalue()
    except Exception as e:
        output = f"Error: {e}"
    finally:
        sys.stdout = old_stdout
    return output

# --- Streamlit UI: Tabs for different features ---

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Function Analysis", "Variable Slicing", "Refactoring Suggestions",
    "Call Graph Visualization", "Code Snippet Testing"
])

# Tab 1: List Functions
with tab1:
    st.header("Function Extraction")
    funcs = parse_python_functions(code)
    if funcs:
        st.write(f"Functions detected ({len(funcs)}):")
        for f in funcs:
            st.write(f"- {f}")
    else:
        st.warning("No functions detected or error parsing code.")

# Tab 2: Variable / Function Usage Slicing
with tab2:
    st.header("Variable / Function Usage Slicing")
    var_name = st.text_input("Enter variable or function name to slice for usage")
    if st.button("Show Usage Lines", key="slice"):
        if var_name.strip() == "":
            st.error("Please enter a valid variable or function name.")
        else:
            usage_lines = find_variable_usage(code, var_name.strip())
            if usage_lines:
                st.write(f"`{var_name}` used at line numbers: {usage_lines}")
            else:
                st.info(f"No usage found for `{var_name}`.")

# Tab 3: Refactoring Suggestions
with tab3:
    st.header("Refactoring Suggestions")
    threshold = st.slider("Function length threshold (lines)", 5, 50, 10)
    if st.button("Analyze for Long Functions", key="refactor"):
        long_funcs = find_long_functions(code, threshold)
        if long_funcs:
            st.write("Long functions detected (consider refactoring):")
            for fname, length in long_funcs:
                st.write(f"- Function `{fname}` is {length} lines long")
        else:
            st.success("No long functions detected above the threshold.")

# Tab 4: Call Graph Visualization
with tab4:
    st.header("Function Call Graph")
    if st.button("Generate Call Graph", key="graph"):
        graph = build_call_graph(code)
        if graph.number_of_nodes() > 0:
            fig = plot_call_graph(graph)
            st.pyplot(fig)
        else:
            st.warning("No function calls found or graph is empty.")

# Tab 5: Interactive Code Snippet Testing
with tab5:
    st.header("Test Refactored Code Snippets")
    snippet = st.text_area("Enter Python code snippet to execute")
    if st.button("Run Snippet", key="exec"):
        if snippet.strip():
            output = execute_code_snippet(snippet)
            st.text_area("Output", value=output, height=200)
        else:
            st.error("Please enter a code snippet to execute.")

# Footer
st.markdown("---")
st.caption("Developed as a Legacy Code Reengineering Assistant demo aligned with FI1931 syllabus concepts.")
