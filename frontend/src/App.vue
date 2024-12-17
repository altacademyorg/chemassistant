<template>
  <div id="app">
    <!-- Floating Button -->
    <button class="floating-button" @click="toggleChatbot" aria-label="Toggle Chatbot">
      💬
    </button>

    <!-- Chatbot Interface -->
    <transition name="slide">
      <div v-if="isChatbotVisible" class="chatbot-container">
        <!-- Chatbot Header -->
        <div class="chatbot-header">
          <h1>Chemistry Assistant</h1>
          <span class="beta-tag">Beta Version</span>
          <button class="close-button" @click="toggleChatbot" aria-label="Close Chatbot">✖</button>
        </div>

        <!-- Chat History -->
        <div class="chat-history" ref="chatContainer">
          <!-- Welcome Message -->
          <div class="chat-group bot-group" v-if="conversation.length === 0">
            <div class="avatar-container">
              <img src="../src/assets/altacademy.png" alt="Bot Avatar" class="avatar" />
            </div>
            <div class="messages-container">
              <div class="message-content bot-message">
                <p>Hey! 👋</p>
              </div>
              <div class="message-content bot-message">
                <p>Let me know how I may help you with chemistry today!</p>
              </div>
            </div>
          </div>

          <!-- Conversation Messages -->
          <template v-for="(group, index) in messageGroups" :key="index">
            <div 
              class="chat-group" 
              :class="{ 'bot-group': group.role === 'assistant', 'user-group': group.role === 'user' }"
            >
              <div class="avatar-container">
                <img 
                  :src="group.role === 'user' ? '../src/assets/user.png' : '../src/assets/altacademy.png'" 
                  :alt="group.role === 'user' ? 'User Avatar' : 'Bot Avatar'"
                  class="avatar"
                />
              </div>
              <div class="messages-container">
                <div 
                  v-for="(message, msgIndex) in group.messages" 
                  :key="msgIndex"
                  class="message-content"
                  :class="{ 'bot-message': group.role === 'assistant', 'user-message': group.role === 'user' }"
                >
                  <p v-if="group.role === 'assistant'" class="katex-rendered">
                    <KaTeXRenderer :content="message.content" />
                  </p>
                  <p v-else>{{ message.content }}</p>
                  <img v-if="message.image" :src="message.image" class="message-image" alt="Uploaded Image" />
                </div>
              </div>
            </div>
          </template>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="chat-group bot-group">
            <div class="avatar-container">
              <img src="../src/assets/altacademy.png" alt="Bot Avatar" class="avatar" />
            </div>
            <div class="messages-container">
              <div class="message-content bot-message">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Typing and Image Upload Area -->
        <form @submit.prevent="sendMessage" class="chatbot-form">
          <input
            type="text"
            v-model="userInput"
            placeholder="Type your question here..."
            id="question"
            required
          />
          <label for="image" class="image-input">
            <font-awesome-icon :icon="['fas', 'paperclip']" />
            <input type="file" @change="handleFileUpload" id="image" accept="image/*" hidden />
          </label>
          <button type="submit" class="send-button" :disabled="isTyping">
            <font-awesome-icon :icon="['fas', 'paper-plane']" />
          </button>
        </form>

        <!-- Image Preview -->
        <div v-if="imagePreview" class="image-preview">
          <img :src="imagePreview" alt="Selected Image" />
          <button @click="removeImage" class="remove-image" aria-label="Remove Image">✖</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import axios from 'axios';
import KaTeXRenderer from './KaTeXRenderer.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faPaperPlane, faPaperclip } from '@fortawesome/free-solid-svg-icons';

library.add(faPaperPlane, faPaperclip);

const conversation = ref([]);
const userInput = ref('');
const selectedFile = ref(null);
const imagePreview = ref(null);
const chatContainer = ref(null);
const isChatbotVisible = ref(false);
const isTyping = ref(false);

// Group messages by role for consecutive messages
const messageGroups = computed(() => {
  const groups = [];
  let currentGroup = null;

  conversation.value.forEach((message) => {
    if (!currentGroup || currentGroup.role !== message.role) {
      currentGroup = {
        role: message.role,
        messages: []
      };
      groups.push(currentGroup);
    }
    currentGroup.messages.push(message);
  });

  return groups;
});

const toggleChatbot = () => {
  isChatbotVisible.value = !isChatbotVisible.value;
};

const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0];
  if (selectedFile.value) {
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target.result;
    };
    reader.readAsDataURL(selectedFile.value);
  }
};

const removeImage = () => {
  selectedFile.value = null;
  imagePreview.value = null;
  if (document.getElementById('image')) {
    document.getElementById('image').value = '';
  }
};

const clearInput = () => {
  userInput.value = '';
  removeImage();
};

const sendMessage = async () => {
  if (!userInput.value.trim() && !selectedFile.value) return;

  const formData = new FormData();
  formData.append('question', userInput.value);
  if (selectedFile.value) {
    formData.append('image', selectedFile.value);
  }

  conversation.value.forEach((message, index) => {
    formData.append(`conversation[${index}][role]`, message.role);
    formData.append(`conversation[${index}][content]`, message.content);
  });

  const userMessage = { role: 'user', content: userInput.value };
  if (selectedFile.value) {
    userMessage.image = imagePreview.value;
  }
  conversation.value.push(userMessage);

  clearInput();
  isTyping.value = true;

  try {
    const response = await axios.post('http://127.0.0.1:8000', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    isTyping.value = false;
    conversation.value.push({ role: 'assistant', content: response.data.response });

    if (selectedFile.value) {
      conversation.value.push({
        role: 'assistant',
        content: "I noticed you uploaded an image. Do you want me to analyze it further?"
      });
    }
  } catch (error) {
    console.error('Error sending message:', error);
    conversation.value.push({ role: 'assistant', content: 'Sorry, there was an error processing your request.' });
    isTyping.value = false;
  }

  await nextTick();
  scrollToBottom();
};

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;600&display=swap');

body {
  font-family: 'Inter Tight', sans-serif;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.message-content, .chatbot-form input[type="text"] {
  font-family: 'Inter Tight', sans-serif;
}

h1 {
  font-family: 'Inter Tight', sans-serif;
  color: white;
  margin: 0;
}
.message-image {
  max-width: 200px;
  max-height: 200px;
  object-fit: cover;
  padding-top: 20px;
  cursor: pointer;
}

.full-size-image-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.full-size-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.close-full-size-image {
  position: absolute;
  top: 20px;
  right: 20px;
  color: white;
  font-size: 30px;
  cursor: pointer;
}
.beta-tag {
  background-color: #e74c3c;
  color: white;
  font-size: 0.8rem;
  font-weight: bold;
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  animation: blink 2s linear infinite; /* Blinking animation */
}

@keyframes blink {
  0%, 100% {
    opacity: 1; /* Fully visible */
  }
  50% {
    opacity: 0; /* Fully hidden */
  }
}

.floating-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 50%;
  width: 64px;
  height: 64px;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.floating-button:hover {
  background-color: #2980b9;
  transform: scale(1.05);
}

.chatbot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 480px;
  height: 600px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chatbot-header {
  background-color: #2c3e50;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.chatbot-header h1 {
  font-size: 1.25rem;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
}

.chat-history {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chat-group {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.bot-group {
  align-self: flex-start;
}

.user-group {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar-container {
  flex-shrink: 0;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 2px;
}


.message-content {
  padding: 12px 16px;
  border-radius: 16px;
  max-width: 100%;
  overflow-x: auto;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.bot-message {
  background-color: #f0f0f0;
  color: #2c3e50;
  width: 300px; /* Set a fixed width for chat bubbles */

  border-radius: 16px 16px 16px 4px;
}

.bot-group .messages-container .message-content:last-child {
  border-radius: 16px 16px 16px 4px;
}

.user-message {
  background: rgb(245, 245, 247);  
  
  border-radius: 16px 16px 4px 16px;
}

.user-group .messages-container .message-content:last-child {
  border-radius: 16px 16px 4px 16px;
}

.chatbot-form {
  display: flex;
  align-items: center;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  background-color: white;
}

.chatbot-form input[type="text"] {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  outline: none;
  margin-right: 12px;
  font-size: 14px;
}

.image-input {
  cursor: pointer;
  margin-right: 12px;
  font-size: 20px;
  color: #2c3e50;
  transition: color 0.2s ease;
}

.image-input:hover {
  color: #2980b9;
}

.send-button {
  background-color: transparent;
  color: inherit;
  border: none;
  padding: 12px;
  border-radius: 99%;
  cursor: pointer;
  font-size: 20px;
  transition: color 0.2s ease;
}

.send-button:hover {
  color: #2980b9;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
.typing-indicator {
  display: flex;
  align-items: center;
  column-gap: 2px;
  padding: 10px 15px;
}

.typing-indicator span {
  height: 10px;
  width: 10px;
  float: left;
  margin: 0 1px;
  background-color: #9E9EA1;
  display: block;
  border-radius: 50%;
  opacity: 0.4;
}

.typing-indicator span:nth-of-type(1) {
  animation: typingBlink 1s infinite 0.3333s;
}

.typing-indicator span:nth-of-type(2) {
  animation: typingBlink 1s infinite 0.6666s;
}

.typing-indicator span:nth-of-type(3) {
  animation: typingBlink 1s infinite 0.9999s;
}

@keyframes typingBlink {
  50% {
    opacity: 1;
  }
}

.image-preview {
  position: relative;
  margin-top: 10px;
  max-width: 200px;
  margin-left: auto;
  margin-right: auto;
}

.image-preview img {
  width: 100%;
  border-radius: 8px;
}

.remove-image {
  position: absolute;
  top: -10px;
  right: -10px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-image:hover {
  background-color: #ff7875;
}

.katex-rendered {
  font-size: 1.1em;
  max-width: 100%;
  overflow-x: auto;
  padding-bottom: 8px;
  margin: 0;
  -webkit-overflow-scrolling: touch;
}

.katex-rendered::-webkit-scrollbar {
  height: 4px;
}

.katex-rendered::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
}

.katex-rendered::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

@media (max-width: 480px) {
  .chatbot-container {
    width: 100%;
    height: 100%;
    bottom: 0;
    right: 0;
    border-radius: 0;
  }

  .chat-group {
    max-width: 90%;
  }
  
  .avatar {
    width: 32px;
    height: 32px;
  }
}
</style>

