from flask import Flask, render_template, request, jsonify ,send_from_directory, abort
import os,uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from werkzeug.utils import secure_filename
import utils as utils
from LLM import FilePerConversationMessageHistory 
from langchain.chains import ConversationChain  
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
import json
from dotenv import load_dotenv


app = Flask(__name__)


# Define the upload folder and allowed file extensions
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}  # Restrict to PDF files for this example
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Base directory for conversation history
CONV_DIR = './conversation_logs'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONV_DIR, exist_ok=True)

def allowed_file(filename):
    """
    Check if a file is allowed (based on its extension).
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Chat page content
@app.route('/')
def home():
    return render_template('index.html')


#Collection page content
@app.route('/collection')
def collection():
    return render_template('collection.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Flask route to handle file uploads and process them.
    """
    if 'pdf' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['pdf']

    # Check if the file has a valid name
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        try:
            # Save the uploaded file securely
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Optional: additional processing (chunking, embedding, etc.)
            utils.add_pdf_to_index(file_path)            

            return jsonify({'message': f'File {filename} uploaded successfully'}), 200

        except Exception as e:
            return jsonify({'message': f'An error occurred: {str(e)}'}), 500

    return jsonify({'message': 'Invalid file type. Only PDF files are allowed.'}), 400

@app.route('/search', methods=['POST'])
def search():
    """
    Flask route to handle search requests. Calls the search_faiss(query) function
    to retrieve relevant results from the FAISS index.
    """
    try:
        # Parse JSON data from the POST request
        data = request.get_json()

        # Validate the presence of the query parameter
        if 'query' not in data or not data['query'].strip():
            return jsonify({'message': 'Search query is required'}), 400

        query = data['query'].strip()

        # Call the search_faiss function with the user's query
        results = utils.search_faiss(query)  # Make sure this function handles FAISS search

        # Return results in a JSON response
        return jsonify({'data': results}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@app.route('/listcollection', methods=['GET'])
def list_collection():
    """
    Flask route to list all PDFs in the collection.
    Calls the get_all_pdfs() function to retrieve the list of PDFs.
    """
    try:
        pdfs = utils.get_all_pdfs()  # Make sure this function retrieves all PDFs
        return jsonify({'data': pdfs}), 200
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    


@app.route('/deletecollection', methods=['POST'])
def delete_pdf():
    """
    Flask route to delete a PDF from the collection.
    Expects a JSON payload with the filename to delete.
    """
    try:
        data = request.get_json()
        if 'filename' not in data or not data['filename'].strip():
            return jsonify({'message': 'Filename is required'}), 400

        filename_to_delete = data['filename'].strip()
        utils.delete_pdf_from_index(filename_to_delete)  # Ensure this function handles deletion

        return jsonify({'message': f'PDF {filename_to_delete} deleted successfully'}), 200

    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    
@app.route('/message/<conv_id>', methods=['POST', 'GET'])
def handle_message(conv_id=None):
    """
    Handle a message from the user. 
    - POST: Starts a new conversation or continues an existing one.
    - GET: Fetches the conversation history for the given conversation ID.
    """
    # Handle GET request
    if request.method == 'GET':
        if not conv_id or conv_id == 'null':  # Conversation ID is required for GET
            return jsonify({
                "message": "A valid conversation ID (conv_id) is required."
            }), 400

        # Initialize conversation history for the given conv_id
        history = FilePerConversationMessageHistory(conv_id=conv_id)

        # Retrieve history messages
        messages = history.load_messages()
        print(f"Retrieved messages for conv_id {conv_id}: {messages}")

        # If no messages exist for this conversation
        if not messages:
            return jsonify({
                "conv_id": conv_id,
                "message": "No messages found for the provided conversation ID."
            }), 404

        # Format messages for response
        formatted_messages = [
            {"type": message["type"], "content": message["content"]}
            for message in messages
        ]

        return jsonify({
            "conv_id": conv_id,
            "messages": formatted_messages
        })

    # Handle POST request
    elif request.method == 'POST':
        data = request.json
        user_message = data.get('message', '')
        knowledge_mode = data.get('knowledge', 'org')  # Default to 'org'


        if not user_message.strip():  # If no user message is provided
            return jsonify({
                "message": "A message is required to start or continue the conversation."
            }), 400

        if not conv_id or conv_id == 'null':  # Start a new conversation if conv_id is null or missing
            conv_id = str(uuid.uuid4())

        # Initialize conversation history for the given conv_id
        history = FilePerConversationMessageHistory(conv_id=conv_id)

        memory = ConversationBufferMemory(chat_memory=history, return_messages=True)
        #print(f"\n \n print memory: {history}")

        #need to load from .env file
        KEY= os.getenv("API_KEY")

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.0, api_key=KEY, stream=True)

        conversation = ConversationChain(llm=llm, memory=memory)

        system_message = f'''You are a helpful assistant. Answer the user's questions based on the provided context.
            If the user message is greetings,thank you etc, please provide the answer without reffering to the context.
            If the user message apart that , then try to provide the answer based only on the context provided, else say "I cannot provide you the answer for this question based on the files uploaded."
            Answer should be precision and with the citation of the file name and page number.
            If the conetext is empty, then proviede the answer based on your world knowledge.
            Add the citation in the end of the answer like this: "\n\n\n\n**Citation**: 'filename' page 'page_number'".
           \n
           When providing citations or references to external files, generate clickable links in Markdown format. Make sure the links include embedded HTML with the target="_blank" attribute so that they open in a new tab or window. Use the following format:
          For a file named example.pdf located at http://127.0.0.1:5000/uploads/example.pdf, the link should appear as:
           <a href="http://127.0.0.1:5000/uploads/example.pdf#page=page_number" target="_blank" rel="noopener noreferrer">example.pdf</a>
           Here are the referenced files:
           1. <a href="http://127.0.0.1:5000/uploads/LLM.pdf#page=5" target="_blank" rel="noopener noreferrer">LLM.pdf</a>
           2. <a href="http://127.0.0.1:5000/uploads/research_notes.docx#page=1" target="_blank" rel="noopener noreferrer">research_notes.docx</a>
           3. <a href="http://127.0.0.1:5000/uploads/image.png" target="_blank" rel="noopener noreferrer">image.png</a>
            '''
        
        #document_content = "context fetched from the documents: " + str(utils.search_faiss(user_message))
        
        if knowledge_mode == "org":
            document_content = "context fetched from the documents: " + str(utils.search_faiss(user_message))
             # Combine System Message and Document Content to Create a Context
            context = f"{system_message}\n\n{document_content}"
            #print(f"\n \n Document content: {document_content}")
        else:  # world knowledge
            document_content = ""  # No context from org docs
            context="Please answer the question based on your world knowledge. If you don't know the answer, say 'I don't know'."





        # Get response from the LLM
        try:
            llm_response = conversation.run(input=f"{context}\n\n User Question: {user_message}")
            #llm_response = conversation.chain.llm_chain.llm.predict(f"{context}\n\n User: {user_message}")
            #llm_response = conversation.predict(input=f"{context}\n\n User: {user_message}")
        except Exception as e:
            return jsonify({"message": "Failed to process the input with LLM", "error": str(e)}), 500

        # Add user message and LLM response to the conversation history
        history.add_message_without_context(HumanMessage(content=user_message)) 
        history.add_message_without_context(AIMessage(content=llm_response))
        # Save the conversation history
        history._save()

        return jsonify({
            "conv_id": conv_id,  # Return the conv_id for the ongoing session
            "response": llm_response
        })


@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    conversations = []  # List to store conversation ID and first truncated question

    # Sort files in the directory by their last modification time (most recent first)
    files = sorted(os.listdir(CONV_DIR), key=lambda f: os.path.getmtime(os.path.join(CONV_DIR, f)), reverse=True)


    # Traverse conversation log files
    for filename in files:
        if filename.endswith('.json'):
            conv_id = filename.split('.')[0]  # Extract conversation ID from filename
            file_path = os.path.join(CONV_DIR, filename)
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    if 'messages' in data:
                        # Extract the first human message's content
                        for message in data['messages']:
                            if message.get('type') == 'human':
                                first_question = message['data'].get('content', '')[:50]  # Truncate to 15 chars
                                conversations.append({'id': conv_id, 'first_question': first_question})
                                break  # Stop after first human message
                except json.JSONDecodeError:
                    print(f'Error reading file: {file_path}')  # Log issues with JSON files

    # Return as JSON response
    return jsonify(conversations)

# Route to serve files from the uploads folder
@app.route('/uploads/<path:filename>')
def serve_file(filename):
    try:
        safe_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if not safe_path.startswith(os.path.abspath("uploads")):
            return "File access forbidden", 403

        if os.path.exists(safe_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error processing file: {str(e)}", 500
    


@app.route('/delete_conversation', methods=['POST'])
def delete_conversation():
    """
    Delete a conversation by convId (conversation ID).
    Expects JSON: { "id": "<convId>" }
    """
    try:
        data = request.get_json()
        conv_id = data.get('id', '').strip()
        if not conv_id:
            return jsonify({'message': 'Conversation ID is required.'}), 400

        file_path = os.path.join(CONV_DIR, f"{conv_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': f'Conversation {conv_id} deleted successfully.'}), 200
        else:
            return jsonify({'message': 'Conversation file not found.'}), 404
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    







if __name__ == '__main__':
    app.run(debug=True)
