# Think of this as importing tools we need to build our chatbot.
import chainlit as cl  # Chainlit is a library that helps us create chatbot user interfaces.
import ollama  # Ollama is a library that lets us interact with large language models (LLMs) like DeepSeek-R1.

# This section defines what happens when a new chat starts.
@cl.on_chat_start
async def start_chat():
    """
    This function runs when a new chat session begins. It sets up the initial state of the chatbot.
    """
    # We create a "memory" for the chatbot to remember past interactions in the conversation.
    # Think of it like a notepad where the chatbot keeps track of the conversation.
    # We use cl.user_session.set to store this memory, associating it with the key "interaction".
    cl.user_session.set(
        "interaction",  # This is the name of the "notepad" we're using.
        [
            {
                "role": "system",  # This is like setting the chatbot's personality/initial instructions.
                "content": "You are a helpful assistant.",  # We tell the chatbot to be helpful.
            }
        ],
    )

    # We create an empty message that will hold the chatbot's response. This is like preparing a blank piece of paper.
    msg = cl.Message(content="")

    # This is the chatbot's first message to the user.
    start_message = "Hello, I'm your 100% local alternative to ChatGPT running on DeepSeek-R1. How can I help you today?"

    # This loop makes the message appear as if it's being typed out, one character at a time.
    for token in start_message:
        await msg.stream_token(token) # Send each character (token) to the user interface.

    # Finally, send the complete message to the user interface.
    await msg.send()

# This section defines a "tool" the chatbot can use - in this case, talking to the LLM.
@cl.step(type="tool")  # This tells Chainlit that this function represents a distinct step in the process, like using a specific tool.
async def tool(input_message):
    """
    This function acts as a bridge between the user's input and the DeepSeek-R1 language model.
    It takes the user's message, sends it to the LLM, and gets the LLM's response.

    Args:
        input_message (str): The user's message.

    Returns:
        dict: The response from the Ollama language model.
    """
    # Get the chatbot's "memory" (the conversation history).
    interaction = cl.user_session.get("interaction")

    # Add the user's latest message to the conversation history.
    interaction.append({"role": "user",
                            "content": input_message})
    
    # Ask the DeepSeek-R1 model (using ollama) to respond to the conversation.
    response = ollama.chat(model="deepseek-r1",
                           messages=interaction) 
    
    # Add the model's response to the conversation history.
    interaction.append({"role": "assistant",
                        "content": response.message.content})
    
    # Return the model's full response.
    return response


# This section defines what happens when the user sends a message.
@cl.on_message
async def main(message: cl.Message):
    """
    This function is the main entry point when a user sends a message.
    It handles the user's message, gets a response from the LLM, and displays the response.

    Args:
        message (cl.Message): The message object sent by the user.  This contains the text of the user's message.
    """

    # Use the "tool" function to get a response from the LLM.
    tool_res = await tool(message.content)

    # Create an empty message to hold the chatbot's response (again, like a blank piece of paper).
    msg = cl.Message(content="")

    # Stream the LLM's response to the user interface, one token (character) at a time.
    for token in tool_res.message.content:
        await msg.stream_token(token)

    # Send the complete message to the user interface.  
    await msg.send()
