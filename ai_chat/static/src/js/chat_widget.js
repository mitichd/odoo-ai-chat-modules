// AI Chat Widget - Безпечне завантаження
console.log('🤖 AI Chat widget loading...');

// Глобальні змінні
let chatIsOpen = false;
let chatInitialized = false;

// Безпечне завантаження після того як сторінка готова
(function() {
    'use strict';

    // Функція ініціалізації
    function initializeChatWidget() {
        if (chatInitialized) {
            console.log('⚠️ Chat already initialized');
            return;
        }

        console.log('📄 Initializing chat widget');
        createChatWidget();
        chatInitialized = true;
    }

    // Чекаємо завантаження DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeChatWidget);
    } else {
        // DOM вже завантажений
        initializeChatWidget();
    }

    // Додатково чекаємо повного завантаження сторінки
    window.addEventListener('load', function() {
        setTimeout(initializeChatWidget, 1000); // Затримка для Odoo
    });
})();

// Основна функція створення віджета
function createChatWidget() {
    // Перевіряємо чи вже не створений віджет
    if (document.getElementById('ai-chat-widget')) {
        console.log('⚠️ Chat widget already exists');
        return;
    }

    try {
        // Створюємо кнопку чату
        createChatButton();

        // Створюємо форму чату (спочатку прихована)
        createChatWindow();

        console.log('✅ Chat widget created successfully');
    } catch (error) {
        console.error('❌ Error creating chat widget:', error);
    }
}

// Створюємо кнопку чату
function createChatButton() {
    const chatButton = document.createElement('div');
    chatButton.id = 'ai-chat-button';
    chatButton.className = 'ai-chat-button';
    chatButton.innerHTML = '💬';
    chatButton.title = 'AI Chat Assistant';

    // ВАЖЛИВО: Додаємо обробник через addEventListener, а не onclick
    chatButton.addEventListener('click', function() {
        console.log('💬 Chat button clicked!');
        toggleChat();
    });

    // Додаємо кнопку на сторінку
    document.body.appendChild(chatButton);
}

// Створюємо вікно чату
function createChatWindow() {
    const chatWindow = document.createElement('div');
    chatWindow.id = 'ai-chat-window';
    chatWindow.className = 'ai-chat-window';
    chatWindow.style.display = 'none'; // Спочатку прихований

    chatWindow.innerHTML = `
        <div class="ai-chat-header">
            <span>🤖 AI Assistant</span>
            <button class="ai-chat-close" id="chat-close-btn">×</button>
        </div>
        <div class="ai-chat-messages" id="ai-chat-messages">
            <div class="ai-chat-message bot">
                Привіт! Я твій AI помічник.
                Спробуй команди: /help, /create_task, /list_tasks
            </div>
        </div>
        <div class="ai-chat-input-area">
            <input type="text" id="ai-chat-input" placeholder="Введи повідомлення або команду...">
            <button id="chat-send-btn">Відправити</button>
        </div>
    `;

    document.body.appendChild(chatWindow);

    // Додаємо обробники подій ПІСЛЯ створення елементів
    const closeBtn = document.getElementById('chat-close-btn');
    const sendBtn = document.getElementById('chat-send-btn');
    const input = document.getElementById('ai-chat-input');

    closeBtn.addEventListener('click', toggleChat);
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
}

// Функція відкриття/закриття чату
function toggleChat() {
    console.log('🔄 Toggling chat...');

    const chatWindow = document.getElementById('ai-chat-window');
    const chatButton = document.getElementById('ai-chat-button');

    if (!chatWindow || !chatButton) {
        console.error('❌ Chat elements not found');
        return;
    }

    if (chatIsOpen) {
        // Закриваємо чат
        chatWindow.style.display = 'none';
        chatButton.style.display = 'block';
        chatIsOpen = false;
        console.log('📴 Chat closed');
    } else {
        // Відкриваємо чат
        chatWindow.style.display = 'block';
        chatButton.style.display = 'none';
        chatIsOpen = true;
        console.log('📱 Chat opened');

        // Фокусуємося на поле введення
        const input = document.getElementById('ai-chat-input');
        if (input) {
            input.focus();
        }
    }
}

// Відправка повідомлення
function sendMessage() {
    const input = document.getElementById('ai-chat-input');
    if (!input) {
        console.error('❌ Input field not found');
        return;
    }

    const message = input.value.trim();

    if (!message) {
        console.log('⚠️ Empty message');
        return;
    }

    console.log('📨 Sending message:', message);

    // Показуємо повідомлення користувача
    addMessage(message, 'user');

    // Обробляємо повідомлення
    handleMessage(message);

    // Очищуємо поле
    input.value = '';
}

// Додаємо повідомлення в чат
function addMessage(text, sender, isHtml = false) {
    const messagesContainer = document.getElementById('ai-chat-messages');
    if (!messagesContainer) {
        console.error('❌ Messages container not found');
        return;
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `ai-chat-message ${sender}`;

    // Перевірка на HTML
    if (isHtml) {
        messageDiv.innerHTML = text;
        console.log('🎨 Added HTML message');
    } else {
        messageDiv.textContent = text;
    }

    messagesContainer.appendChild(messageDiv);

    // Після HTML форми прикріпляємо обробники
    if (isHtml) {
        setTimeout(() => attachFormHandlers(), 100);
    }

    // Плавна прокрутка
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

/// ГОЛОВНА ФУНКЦІЯ - обробка повідомлень
async function handleMessage(message) {
    console.log('🧠 Processing message:', message);

    try {
        const response = await fetch('/ai_chat/process_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: { message: message },
                id: Math.random()
            })
        });

        const data = await response.json();

        if (data.result) {
            // Перевірка на is_html
            const isHtml = data.result.is_html || false;
            addMessage(data.result.reply, 'bot', isHtml);

            console.log(`📨 Response type: ${isHtml ? 'HTML' : 'TEXT'}`);
        } else {
            addMessage('Помилка сервера. Спробуй ще раз.', 'bot');
        }

    } catch (error) {
        console.error('❌ Error:', error);
        addMessage('Помилка з\'єднання. Перевір інтернет.', 'bot');
    }
}

// Додаємо глобальні функції для відладки
window.aiChatDebug = {
    toggleChat: toggleChat,
    sendMessage: sendMessage,
    addMessage: addMessage,
    handleMessage: handleMessage
};

console.log('✅ AI Chat widget script loaded');

function attachFormHandlers() {
    const form = document.getElementById('ai-create-task-form');
    if (!form) {
        console.log('⚠️ No form found to attach handlers');
        return;
    }

    console.log('🔗 Attaching form handlers');

    // Обробка відправки форми
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('📝 Form submitted');

        // Збираємо дані з форми
        const formData = new FormData(form);
        const taskData = Object.fromEntries(formData.entries());

        console.log('📊 Form data:', taskData);

        try {
            // Відправляємо на сервер
            const response = await fetch('/ai_chat/save_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: taskData,
                    id: Math.random()
                })
            });

            const result = await response.json();
            console.log('📊 Server response:', result);

            if (result.result) {
                if (result.result.success) {
                    addMessage(result.result.reply, 'bot');
                    console.log('✅ Task created successfully');
                } else {
                    addMessage(result.result.reply || 'Помилка створення', 'bot');
                    console.log('❌ Task creation failed');
                }
            } else {
                addMessage('Помилка сервера. Перевір консоль.', 'bot');
                console.error('❌ Unexpected response:', result);
            }

            if (result.result && result.result.success) {
                addMessage(result.result.message, 'bot');
            } else {
                addMessage(result.result?.message || 'Помилка створення завдання', 'bot');
            }

            // Видаляємо форму після створення
            form.closest('.ai-chat-message').remove();

        } catch (error) {
            console.error('❌ Form submission error:', error);
            addMessage('Помилка відправки форми. Спробуй ще раз.', 'bot');
        }
    });

    // Обробка кнопки "Скасувати"
    const cancelBtn = form.querySelector('.btn-cancel');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            console.log('❌ Form cancelled');
            form.closest('.ai-chat-message').remove();
            addMessage('Створення завдання скасовано.', 'bot');
        });
    }
}

// Глобальна функція для кнопки "Скасувати" в HTML
function cancelTaskForm() {
    const form = document.getElementById('ai-create-task-form');
    if (form) {
        form.closest('.ai-chat-message').remove();
        addMessage('Створення завдання скасовано.', 'bot');
    }
}

