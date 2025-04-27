class BehaviorTracker {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.data = {
            typing_intervals: [],
            mouse_speeds: [],
            click_timings: [],
            scroll_events: [],
            device: this.getDeviceInfo(),
            startTime: new Date().toISOString()
        };
        this.setupEventListeners();
        this.startSending();
    }

    generateSessionId() {
        return 'sess-' + Math.random().toString(36).substr(2, 9) + 
               '-' + Date.now().toString(36);
    }

    getDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            screen: { width: screen.width, height: screen.height },
            platform: navigator.platform,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            touchSupport: 'ontouchstart' in window
        };
    }

    setupEventListeners() {
        // Typing dynamics
        let lastKeyTime = performance.now();
        document.addEventListener('keydown', (e) => {
            const now = performance.now();
            this.data.typing_intervals.push(now - lastKeyTime);
            lastKeyTime = now;
        });

        // Mouse movements
        let lastPos = null, lastTime = null;
        document.addEventListener('mousemove', (e) => {
            const now = performance.now();
            if (lastPos && lastTime) {
                const distance = Math.sqrt(
                    Math.pow(e.clientX - lastPos.x, 2) + 
                    Math.pow(e.clientY - lastPos.y, 2)
                );
                const timeDelta = now - lastTime;
                if (timeDelta > 0) {
                    this.data.mouse_speeds.push(distance / timeDelta);
                }
            }
            lastPos = { x: e.clientX, y: e.clientY };
            lastTime = now;
        });

        // Click analysis
        document.addEventListener('click', (e) => {
            this.data.click_timings.push({
                x: e.clientX,
                y: e.clientY,
                time: performance.now()
            });
        });

        // Scroll behavior
        let lastScroll = 0;
        window.addEventListener('scroll', (e) => {
            const now = performance.now();
            this.data.scroll_events.push({
                time: now,
                delta: window.scrollY - lastScroll
            });
            lastScroll = window.scrollY;
        });
    }

    async sendData() {
        try {
            const payload = {
                session_id: this.sessionId,
                typing_speed: this.data.typing_intervals,
                mouse_speed: this.data.mouse_speeds,
                click_accuracy: this.data.click_timings.map(t => t.time),
                scroll_behavior: this.data.scroll_events,
                device_info: this.data.device,
                transactionTime: new Date().toISOString()
            };

            const response = await fetch('/behavior', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            this.handleRiskResponse(result);
            
            // Reset for next batch (keep first values as baseline)
            this.data.typing_intervals = this.data.typing_intervals.slice(-10);
            this.data.mouse_speeds = this.data.mouse_speeds.slice(-10);
            this.data.click_timings = this.data.click_timings.slice(-5);
            this.data.scroll_events = this.data.scroll_events.slice(-5);

        } catch (error) {
            console.error('Error sending behavior data:', error);
        }
    }

    handleRiskResponse(result) {
        if (result.risk_level === "high") {
            this.showWarning("High risk detected! Session will be terminated.");
        } else if (result.risk_level === "medium") {
            this.showWarning("Verification required: Please complete CAPTCHA.");
        }
    }

    showWarning(message) {
        const existingAlert = document.getElementById('risk-alert');
        if (existingAlert) existingAlert.remove();
        
        const alert = document.createElement('div');
        alert.id = 'risk-alert';
        alert.style = `position: fixed; top: 20px; right: 20px; padding: 15px;
                      background: ${message.includes('High') ? '#ff4444' : '#ffbb33'};
                      color: white; border-radius: 5px; z-index: 1000;`;
        alert.textContent = message;
        document.body.appendChild(alert);
        
        setTimeout(() => alert.remove(), 5000);
    }

    startSending() {
        // Initial send after 3 seconds
        setTimeout(() => this.sendData(), 3000);
        // Then every 5 seconds
        setInterval(() => this.sendData(), 5000);
    }
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    new BehaviorTracker();
});
