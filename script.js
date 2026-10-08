/**
 * Secret Santa : Horror Edition - Core Client Script
 * Features:
 * - Procedural Web Audio API Horror Sound Engine
 * - Atmospheric Ember & Ash Particle System
 * - Interactive 25-Color Occult Wheel Canvas & Physics
 * - Bone-and-Iron Dart Aiming & Trajectory Engine
 * - Server-Driven Fair Selection & Dramatic Horror Reveal
 * - Anti-Tamper & One-Time Participation Enforcement
 */

// Global State
let audioContext = null;
let isAudioEnabled = false;
let wheelSlices = [];
let isSpinning = false;
let isDartThrown = false;
let currentRotation = 0;
let targetSlice = null;

/* ==========================================================================
   1. PROCEDURAL WEB AUDIO API SYNTHESIZER
   ========================================================================== */
function initAudio() {
    if (!audioContext) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioCtx();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
}

function playHorrorSound(type) {
    if (!isAudioEnabled) return;
    try {
        initAudio();
        const ctx = audioContext;
        const now = ctx.currentTime;

        if (type === 'tick') {
            // Mechanical wheel tick
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(140, now);
            osc.frequency.exponentialRampToValueAtTime(35, now + 0.04);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.04);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.05);

        } else if (type === 'whoosh') {
            // Dart air slice whoosh (Filtered noise burst)
            const bufferSize = ctx.sampleRate * 0.4;
            const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = Math.random() * 2 - 1;
            }
            const noise = ctx.createBufferSource();
            noise.buffer = buffer;

            const filter = ctx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(800, now);
            filter.frequency.exponentialRampToValueAtTime(220, now + 0.35);

            const gain = ctx.createGain();
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.38);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);
            noise.start(now);

        } else if (type === 'impact') {
            // Heavy bone/wood strike
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(95, now);
            osc.frequency.exponentialRampToValueAtTime(25, now + 0.3);
            gain.gain.setValueAtTime(0.7, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.4);

        } else if (type === 'chime' || type === 'bell') {
            // Deep sinister occult bell
            [65, 130, 195, 260].forEach((freq, idx) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, now);
                const volume = 0.4 / (idx + 1);
                gain.gain.setValueAtTime(volume, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 2.5);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start(now);
                osc.stop(now + 2.6);
            });

        } else if (type === 'curse' || type === 'warning') {
            // Horror glitch sting
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(110, now);
            osc.frequency.linearRampToValueAtTime(55, now + 0.5);
            gain.gain.setValueAtTime(0.5, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.6);
        }
    } catch (e) {
        console.warn('Audio playback inhibited:', e);
    }
}

// Sound Toggle Setup
function setupSoundToggle() {
    const soundBtn = document.getElementById('sound-toggle-btn');
    const soundIcon = document.getElementById('sound-icon');
    const soundText = document.getElementById('sound-text');

    // Retrieve user preference
    const savedAudio = localStorage.getItem('horror_audio_enabled');
    if (savedAudio === 'true') {
        isAudioEnabled = true;
        if (soundIcon) soundIcon.textContent = '🔊';
        if (soundText) soundText.textContent = 'SOUND: ON';
    }

    if (soundBtn) {
        soundBtn.addEventListener('click', () => {
            isAudioEnabled = !isAudioEnabled;
            localStorage.setItem('horror_audio_enabled', isAudioEnabled ? 'true' : 'false');
            if (isAudioEnabled) {
                initAudio();
                if (soundIcon) soundIcon.textContent = '🔊';
                if (soundText) soundText.textContent = 'SOUND: ON';
                playHorrorSound('tick');
            } else {
                if (soundIcon) soundIcon.textContent = '🔇';
                if (soundText) soundText.textContent = 'SOUND: OFF';
            }
        });
    }
}

/* ==========================================================================
   2. ATMOSPHERIC PARTICLE CANVAS (Ash & Blood Embers)
   ========================================================================== */
function setupParticles() {
    const canvas = document.getElementById('particles-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const count = Math.min(50, Math.floor(width / 25));

    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 2 + 0.8,
            speedY: -(Math.random() * 0.4 + 0.15),
            speedX: (Math.random() - 0.5) * 0.25,
            opacity: Math.random() * 0.6 + 0.2,
            isEmber: Math.random() > 0.4
        });
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        particles.forEach(p => {
            p.y += p.speedY;
            p.x += p.speedX;

            if (p.y < -10) {
                p.y = height + 10;
                p.x = Math.random() * width;
            }
            if (p.x < -10) p.x = width + 10;
            if (p.x > width + 10) p.x = -10;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            if (p.isEmber) {
                ctx.fillStyle = `rgba(255, 35, 60, ${p.opacity})`;
                ctx.shadowColor = 'rgba(255, 26, 53, 0.8)';
                ctx.shadowBlur = 6;
            } else {
                ctx.fillStyle = `rgba(200, 190, 180, ${p.opacity * 0.5})`;
                ctx.shadowBlur = 0;
            }
            ctx.fill();
        });

        requestAnimationFrame(animate);
    }
    animate();
}

/* ==========================================================================
   3. OCCULT 25-COLOR WHEEL CANVAS ENGINE
   ========================================================================== */
function drawWheel(slices) {
    const canvas = document.getElementById('wheel-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = canvas.width;
    const center = size / 2;
    const radius = center - 8;
    const numSlices = slices.length || 25;
    const sliceAngle = (2 * Math.PI) / numSlices;

    ctx.clearRect(0, 0, size, size);

    slices.forEach((slice, i) => {
        const startAngle = i * sliceAngle;
        const endAngle = startAngle + sliceAngle;

        // Draw Sector Wedge
        ctx.beginPath();
        ctx.moveTo(center, center);
        ctx.arc(center, center, radius, startAngle, endAngle);
        ctx.closePath();

        // Unique horror shade
        ctx.fillStyle = slice.color;
        ctx.fill();

        // Dark Border
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = '#050207';
        ctx.stroke();

        // Subtle slice inner texture highlight
        const midAngle = startAngle + sliceAngle / 2;
        ctx.save();
        ctx.translate(center, center);
        ctx.rotate(midAngle);

        // Slice Sigil & Label
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        
        if (slice.is_forbidden) {
            ctx.fillStyle = '#ff2a44';
            ctx.font = 'bold 15px "Cinzel Decorative", serif';
            ctx.fillText('⛔ VOID', radius - 30, 0);
        } else {
            ctx.fillStyle = '#f0eae1';
            ctx.font = 'bold 15px "Outfit", sans-serif';
            ctx.shadowColor = slice.glow || '#ff1a35';
            ctx.shadowBlur = 4;
            ctx.fillText(`${slice.sigil} ${slice.disguised_name}`, radius - 25, 0);
        }

        ctx.restore();
    });
}

/* ==========================================================================
   4. DART AIMING & THROWING ENGINE (secret_santa.html)
   ========================================================================== */
function setupWheelAndDart() {
    const stage = document.getElementById('ritual-stage');
    const disc = document.getElementById('wheel-disc');
    const crosshair = document.getElementById('aim-crosshair');
    const dart = document.getElementById('horror-dart');
    const hudStatus = document.getElementById('hud-status');
    const body = document.body;

    if (!stage || !disc) return;

    // Check if user already played
    const hasPlayed = body.dataset.hasPlayed === 'true';
    if (hasPlayed) {
        showAlreadyPlayedModal();
        return;
    }

    // Fetch Wheel Layout from Backend
    fetch('/api/wheel-data')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.slices) {
                wheelSlices = data.slices;
                drawWheel(wheelSlices);
                if (data.has_played) {
                    showAlreadyPlayedModal();
                }
            }
        })
        .catch(err => console.error('Error fetching wheel data:', err));

    // Mouse & Touch Aim Tracker
    function updateAimPosition(clientX, clientY) {
        if (isSpinning || isDartThrown) return;
        const rect = stage.getBoundingClientRect();
        const x = clientX - rect.left;
        const y = clientY - rect.top;

        if (crosshair) {
            crosshair.style.left = `${x}px`;
            crosshair.style.top = `${y}px`;
        }
    }

    stage.addEventListener('mousemove', (e) => {
        updateAimPosition(e.clientX, e.clientY);
    });

    stage.addEventListener('touchmove', (e) => {
        if (e.touches && e.touches[0]) {
            updateAimPosition(e.touches[0].clientX, e.touches[0].clientY);
        }
    }, { passive: true });

    // Dart Throw Handler (One-Time Execution)
    async function handleThrow(e) {
        if (isSpinning || isDartThrown) return;

        // Ensure user didn't already participate
        if (document.body.dataset.hasPlayed === 'true') {
            showAlreadyPlayedModal();
            return;
        }

        isSpinning = true;
        isDartThrown = true;

        if (hudStatus) {
            hudStatus.textContent = 'STATUS: DART CAST INTO THE SHADOWS...';
            hudStatus.style.color = '#ff1a35';
        }

        // Get aim position for dart flight origin
        const rect = stage.getBoundingClientRect();
        let targetX = rect.width / 2;
        let targetY = rect.height / 2;

        if (e && e.clientX) {
            targetX = e.clientX - rect.left;
            targetY = e.clientY - rect.top;
        } else if (e && e.touches && e.touches[0]) {
            targetX = e.touches[0].clientX - rect.left;
            targetY = e.touches[0].clientY - rect.top;
        }

        // Call backend API to initiate throw and get deterministic recipient slice
        try {
            const response = await fetch('/api/throw-dart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                if (result.code === 'ALREADY_PLAYED') {
                    showAlreadyPlayedModal();
                } else {
                    alert(result.error || 'THE SPIRITS ARE RESTLESS. TRY AGAIN.');
                }
                isSpinning = false;
                isDartThrown = false;
                return;
            }

            targetSlice = result.target_slice_index;
            const targetAngle = result.target_angle; // Target landing angle at top pointer

            // Animate dart flight
            if (dart) {
                dart.style.left = `${targetX}px`;
                dart.style.top = `${targetY}px`;
                dart.classList.add('dart-flying');
            }
            playHorrorSound('whoosh');

            // Wheel physics: Full rotations + calibrated target stop
            // 7 full turns (7 * 360 = 2520) + calculated targetAngle
            const fullSpins = 7 * 360;
            currentRotation = fullSpins + targetAngle;

            // Audio ticks during deceleration
            let tickCount = 0;
            const tickInterval = setInterval(() => {
                tickCount++;
                playHorrorSound('tick');
                if (tickCount > 35) clearInterval(tickInterval);
            }, 140);

            // Apply smooth CSS rotational deceleration
            disc.style.transition = 'transform 5.5s cubic-bezier(0.12, 0.95, 0.22, 1)';
            disc.style.transform = `rotate(${currentRotation}deg)`;

            // On Wheel Stop Landing
            setTimeout(() => {
                clearInterval(tickInterval);
                playHorrorSound('impact');
                document.body.classList.add('glitch-shake');
                setTimeout(() => document.body.classList.remove('glitch-shake'), 600);

                if (hudStatus) {
                    hudStatus.textContent = 'STATUS: DESTINY SEALED. THE WHEEL HAS SPOKEN.';
                }

                // Highlight landed state & open pre-reveal modal
                setTimeout(() => {
                    showPreRevealModal(targetSlice);
                }, 1000);

            }, 5500);

        } catch (err) {
            console.error('Throw exception:', err);
            isSpinning = false;
            isDartThrown = false;
        }
    }

    stage.addEventListener('click', handleThrow);
}

/* ==========================================================================
   5. REVEAL & OPEN-IT WORKFLOW
   ========================================================================== */
function showPreRevealModal(sliceIndex) {
    const modal = document.getElementById('reveal-modal');
    const openBtn = document.getElementById('open-it-btn');
    const sigilDisplay = document.getElementById('chosen-sigil-display');

    if (!modal) return;

    if (wheelSlices && wheelSlices[sliceIndex]) {
        sigilDisplay.textContent = wheelSlices[sliceIndex].sigil || '⛧';
    }

    modal.classList.remove('hidden');
    playHorrorSound('bell');

    if (openBtn) {
        openBtn.onclick = () => {
            modal.classList.add('hidden');
            triggerDramaticReveal(sliceIndex);
        };
    }
}

function triggerDramaticReveal(sliceIndex) {
    const blackout = document.getElementById('reveal-blackout');
    const nameEl = document.getElementById('revealed-recipient-name');
    const giftEl = document.getElementById('revealed-gift-preference');

    if (blackout) blackout.classList.remove('hidden');
    playHorrorSound('chime');

    // Call backend reveal API to finalize participation & unlock recipient details
    fetch('/api/reveal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slice_index: sliceIndex })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Mark state as completed locally
            document.body.dataset.hasPlayed = 'true';

            // Typewriter / flicker effect on recipient name
            typewriterText(nameEl, data.recipient_name, () => {
                if (giftEl) giftEl.textContent = `"${data.gift_preference}"`;
                playHorrorSound('bell');
            });
        } else {
            alert(data.error || 'COULD NOT UNSEAL YOUR RECIPIENT.');
        }
    })
    .catch(err => {
        console.error('Reveal error:', err);
    });
}

function typewriterText(element, text, callback) {
    if (!element) return;
    element.textContent = '';
    element.dataset.text = text;
    let i = 0;
    const speed = 70;

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            playHorrorSound('tick');
            i++;
            setTimeout(type, speed);
        } else if (callback) {
            callback();
        }
    }
    type();
}

/* ==========================================================================
   6. ALREADY PLAYED HORROR CURSE MODAL
   ========================================================================== */
function showAlreadyPlayedModal() {
    const modal = document.getElementById('already-played-modal');
    if (!modal) return;

    modal.classList.remove('hidden');
    playHorrorSound('warning');

    // Dramatic glitch screen shake
    document.body.classList.add('glitch-shake');
    setTimeout(() => document.body.classList.remove('glitch-shake'), 800);
}

/* ==========================================================================
   INITIALIZATION ON DOM LOAD
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    setupSoundToggle();
    setupParticles();
    setupWheelAndDart();
});
