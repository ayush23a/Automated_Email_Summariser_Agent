from src.graph import create_graph
from src.state import GraphState

def main():
    print("Starting Email Summarizer Agent...")
    app = create_graph()
    
    # Initialize with empty state
    initial_state = GraphState()
    
    # Run the graph
    final_state = app.invoke(initial_state)
    
    if final_state.get("error"):
        print(f"❌ Execution failed with error: {final_state['error']}")
        exit(1)
        
    print("✅ Email Summary Draft created successfully!")
    # Optional: Print digest preview
    # print(final_state.get("final_digest"))

if __name__ == "__main__":
    main()
