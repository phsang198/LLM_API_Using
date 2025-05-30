import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph

# Thiết lập API key cho Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyCIIYXs3aadHbCugrSYMq95BKHK96-eSgM"

# Kết nối đến Neo4j
graph = Neo4jGraph(
    url="bolt://10.225.0.240:7687",
    username="neo4j",
    password="ZmRT-BpcDJq6B7g5XGH4ppauFZz4QoORxsQ1CbAzshk"
)

# Khởi tạo mô hình Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Tạo chuỗi hỏi đáp sử dụng GraphCypherQAChain
qa_chain = GraphCypherQAChain.from_llm(llm, graph=graph, verbose=True,
    allow_dangerous_requests=True)

# Hàm để đặt câu hỏi
def ask_question(question):
    response = qa_chain.invoke(question)
    #print(f"❓ Câu hỏi: {question}")
    #print(f"✅ Trả lời: {response}")
    return response

# # Ví dụ sử dụng
# if __name__ == "__main__":
#     ask_question("Tôi muốn biết về các tất cả các hàm liên quan đến activity")
