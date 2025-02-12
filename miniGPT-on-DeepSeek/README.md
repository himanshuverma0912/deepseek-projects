
# miniGPT on DeepSeek

This project leverages DeepSeek-R1 and Chainlit to create a 100% locally running mini-ChatGPT app.

## Installation and setup


**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install -r requirements.txt
   ```

**Run the app**:

   Run the chainlit app as follows:
   ```bash
   chainlit run app.py -w
   ```

# Dataflow of the program

 Let's trace the complete data flow of the chatbot program, from the moment a user starts a chat to when they send a single message and receive a response.

### 1. Chat Initialization (@cl.on_chat_start)**

* ***Trigger*** : A user opens the chatbot interface (e.g., in a web browser). This action triggers the start_chat function, decorated with **@cl.on_chat_start** .<br />

* ***Action 1***: Setting up the Chatbot's "Memory":<br />
    * **cl.user_session.set("interaction", [...])**: The program creates a list called "interaction" to store the conversation history. This acts like a         "notepad" for the chatbot.<br />
    * **Initial "System" Message**: It adds a message to the "interaction" list: {"role": "system", "content": "You are a helpful assistant."}. This sets the chatbot's initial instructions (its "personality").<br />

* ***Action 2***: Preparing the Welcome Message:<br />
    * **msg = cl.Message(content="")**: An empty cl.Message object is created. This is where the chatbot's welcome message will be built.<br />
    * **start_message = "Hello, I'm your..."**: The welcome message text is defined.<br />

* ***Action 3***: Streaming the Welcome Message:<br />
    * **for token in start_message**:: The code loops through each character (token) of the start_message.<br />
    * **await msg.stream_token(token)**: Each character is sent asynchronously to the user interface. await allows this to happen smoothly, creating the typing effect. The program doesn't wait for one character to fully display before sending the next.<br />
    * **await msg.send()**: After all characters are sent, msg.send() signals that the welcome message is complete. This is important for Chainlit's internal bookkeeping.<br />
* ***Result***: The user sees the welcome message appearing in the chat interface, and the chatbot is ready to receive input. The "interaction" list now contains only the initial system message.

### 2. User Sends a Message (@cl.on_message)

* ***Trigger***: The user types a message (e.g., "What is the capital of France?") and presses Enter (or clicks a "Send" button). This triggers the main function, decorated with **@cl.on_message**. The message is passed as a cl.Message object to the main function.<br />

* ***Action 1***: Calling the tool Function:<br />
    * **tool_res** = await tool(message.content): The main function immediately calls the **tool** function, passing the text of the user's message (**message.content**). The await keyword is crucial here, as we're about to interact with the LLM (which takes time).<br />

### 3. Inside the tool Function (@cl.step(type="tool"))

* ***Action 1***: Retrieving the Chat History:<br />
    * **interaction = cl.user_session.get("interaction")**: The tool function retrieves the "interaction" list (the conversation history) from the user's session.<br />
* ***Action 2***: Appending the User's Message:<br />
    * **interaction.append({"role": "user", "content": input_message})**: The user's message is added to the "interaction" list, marked with the role "user".<br />
* ***Action 3***: Interacting with the LLM (Ollama):<br />
    * **response = ollama.chat(model="deepseek-r1", messages=interaction)**: This is the core interaction with the LLM. The entire "interaction" list (system message + user message) is sent to the **deepseek-r1 model** using the **ollama.chat** function. This function call is synchronous from Ollama's perspective (we call it and wait for it to finish), but from Chainlit's perspective (and the user's), it's still an asynchronous operation managed by await in the calling function (main).<br />
* ***Action 4***: Appending the LLM's Response:<br />
    * **interaction.append({"role": "assistant", "content": response.message.content})**: The LLM's response is added to the "interaction" list, marked with the role "assistant".<br />
* ***Action 5***: Returning the Response:<br />
    * **return response**: The complete response object from Ollama is returned to the main function.<br />

### 4. Back in the main Function (@cl.on_message - continued)

* ***Action 2***: Preparing to Display the Response:<br />
    * **msg = cl.Message(content="")**: A new, empty cl.Message object is created. This will hold the LLM's response that will be displayed to the user.<br />
* ***Action 3***: Streaming the LLM's Response:<br />
    * **for token in tool_res.message.content:**: The code loops through each character (token) of the LLM's response (which was returned by the tool function).<br />
    * **await msg.stream_token(token)**: Each character is sent asynchronously to the user interface, creating the typing effect.<br />
    * **await msg.send()**: The complete message is marked as sent.<br />

### 5. Final Result

The user sees the LLM's response (e.g., "Paris") appear in the chat interface, character by character. The "interaction" list in the cl.user_session now contains:

```bash
    The initial system message.
    The user message ("What is the capital of France?").
    The LLM response ("Paris").
   ```

### This completes one full cycle of user input and chatbot response. The chatbot is now ready for the next user message, and the process would repeat from Step 2.
