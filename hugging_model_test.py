import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import websockets , json



tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2' , pad_token_id = tokenizer.eos_token_id)

def text_generation(sentance):

    input_ids = tokenizer.encode(sentance , return_tensors='pt')
    output = model.generate(input_ids , max_length = 100 , num_beams = 5 , no_repeat_ngram_size = 2 , early_stopping = True)
    text = tokenizer.decode(output[0] , skip_special_tokens = True)
    return text


app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {text_generation(data)}")

