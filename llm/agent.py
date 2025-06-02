import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph

# Thiết lập API key cho Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyDhZET3wuiHrPZlguoPqpsj-zOkaGRl1ow"

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

# Định nghĩa prompt để truy xuất thông minh hơn
RETRIEVAL_PROMPT = """
Bạn là trợ lý AI truy vấn dữ liệu từ Neo4j Knowledge Graph về hệ thống workflow, các entity, API, hàm core, và các thành phần giao diện web.
- Entity có thể là: Core (Engine, Activity, Gateway, Event, Subprocess, UserTask, ...), Service (API), Web App, Web App Component, External System, ...
- Relationship có thể là: Contains, Calls, Uses, Has Function, Has Component, Part Of, Belongs To, Produces, Manages, ...
- Hỗ trợ tìm kiếm theo tên, loại, mô tả, chức năng, thuộc tính, và các mối quan hệ giữa các entity.
- Hỗ trợ trả lời các câu hỏi như: "Những entity nào có chữ activity?", "Các API nào liên quan đến Engine?", "Các thành phần giao diện của Workflow Designer?", "Các hàm core mà Activity sử dụng?", ...
- Nếu câu hỏi liên quan đến mối quan hệ, hãy truy vấn các node và relationship phù hợp.
- Nếu câu hỏi liên quan đến thuộc tính, hãy truy vấn thuộc tính của node.
- Nếu câu hỏi liên quan đến ví dụ, giải thích, endpoint, input/output, hãy trả về thông tin chi tiết từ node.
- Nếu không tìm thấy, hãy trả lời lịch sự rằng không có dữ liệu phù hợp.
- Nếu câu hỏi không liên quan đến hệ thống workflow, hãy trả lời 1 câu duy nhất "Tôi không có thông tin về chủ đề này.".
- Nếu câu hỏi có tiếng Việt, thêm backtick ` quanh các thành phần tiếng Việt trong truy vấn được sinh ra để đảm bảo định dạng đúng. 
   Ví dụ :n.Mô tả thì là n.`Mô tả`.
- Luôn trả lời ngắn gọn, đúng trọng tâm
"""

# Hàm để đặt câu hỏi
def ask_question(question):
    full_question = RETRIEVAL_PROMPT + "\nCâu hỏi: " + question
    response = qa_chain.invoke(full_question)
    #print(f"❓ Câu hỏi: {question}")
    print(f"✅ Trả lời: {response}")
    return response

# # Ví dụ sử dụng
# if __name__ == "__main__":
#     ask_question("Tôi muốn biết về các tất cả các hàm liên quan đến activity")
