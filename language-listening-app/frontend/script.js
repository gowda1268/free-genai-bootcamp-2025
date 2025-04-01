class LanguageLearningApp {
    constructor() {
        this.baseURL = 'http://localhost:8000';
        this.audioPlayers = new Map();
    }

    async transcribeVideo() {
        try {
            const url = document.getElementById('youtube-url').value.trim();
            if (!url) {
                throw new Error('Please enter a YouTube URL');
            }

            this.showLoading();
            const response = await fetch(`${this.baseURL}/transcribe`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            if (!response.ok) {
                throw new Error('Failed to transcribe video');
            }

            const data = await response.json();
            this.showSuccess('Transcription completed successfully!');
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }

    async generateQuestions() {
        try {
            const topic = document.getElementById('topic').value.trim();
            if (!topic) {
                throw new Error('Please enter a topic');
            }

            this.showLoading();
            const response = await fetch(`${this.baseURL}/generate-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic }),
            });

            if (!response.ok) {
                throw new Error('Failed to generate questions');
            }

            const data = await response.json();
            this.displayQuestions(data.questions);
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayQuestions(questions) {
        const container = document.getElementById('questions-container');
        container.innerHTML = '';

        questions.forEach(question => {
            const card = document.createElement('div');
            card.className = 'question-card';

            const questionText = document.createElement('div');
            questionText.className = 'question-text';
            questionText.textContent = question.text;

            const difficultyBadge = document.createElement('span');
            difficultyBadge.className = `difficulty-badge difficulty-${question.difficulty}`;
            difficultyBadge.textContent = question.difficulty;

            const audioControl = document.createElement('div');
            audioControl.className = 'audio-control';

            const audioButton = document.createElement('button');
            audioButton.className = 'audio-button';
            audioButton.textContent = 'Play Audio';
            audioButton.onclick = () => this.playAudio(question.audio_url);

            audioControl.appendChild(audioButton);
            card.appendChild(questionText);
            card.appendChild(difficultyBadge);
            card.appendChild(audioControl);
            container.appendChild(card);
        });
    }

    async playAudio(audioUrl) {
        if (!this.audioPlayers.has(audioUrl)) {
            const audio = new Audio(`${this.baseURL}${audioUrl}`);
            this.audioPlayers.set(audioUrl, audio);
        }

        const audio = this.audioPlayers.get(audioUrl);
        if (audio.paused) {
            audio.play();
        } else {
            audio.pause();
        }
    }

    showLoading() {
        const container = document.getElementById('questions-container');
        container.innerHTML = '<div class="loading">Loading...</div>';
    }

    hideLoading() {
        const loading = document.querySelector('.loading');
        if (loading) {
            loading.remove();
        }
    }

    showError(message) {
        const container = document.getElementById('questions-container');
        container.innerHTML = `<div class="error">${message}</div>`;
    }

    showSuccess(message) {
        const container = document.getElementById('questions-container');
        container.innerHTML = `<div class="error" style="color: #2ecc71;">${message}</div>`;
    }
}

// Initialize the app
const app = new LanguageLearningApp();