import os
import warnings
#from dotenv import load_dotenv

#os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
#warnings.filterwarnings("ignore")

#load_dotenv()

from graph_builder import build_graph

if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"query": "How much sorbitol does a 3 kg child get from Netupitant suspension?"})
    print(result["answer"])

