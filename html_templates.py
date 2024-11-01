import os
css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e;
    flex-direction: row-reverse;
    align-self: flex-end;
    text-align: right;
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 100%;
  padding: 0 1.5rem;
  color: #fff;
  text-align: justify;
  word-wrap: break-word;
}
.chat-message.user .message {
  text-align: justify; 
  text-align-last: right; 
}

'''
def get_bot_template(MSG):
    bot_template = f'''
    <div class="chat-message bot">
        <div class="avatar">
            <img src="https://static.vecteezy.com/system/resources/thumbnails/025/271/430/small/robot-chatbot-generative-ai-free-png.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
        </div>
        <div class="message">{MSG}</div>
    </div>
    '''
    return bot_template

def get_user_template(MSG):
    if os.path.exists("image.txt"):
        with open("image.txt", "r") as f:
            img_src = f.read()
    else:
        img_src = "https://cdn-icons-png.flaticon.com/512/3177/3177440.png"
        
    user_template = f'''
    <div class="chat-message user">
        <div class="avatar">
            <img src="{img_src}" width="350" alt="Grab Vector Graphic Person Icon | imagebasket" /></a>
        </div>    
        <div class="message">{MSG}</div>
    </div>
    '''
    return user_template