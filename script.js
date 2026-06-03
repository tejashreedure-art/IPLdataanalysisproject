document.addEventListener('DOMContentLoaded', () => {

    const loginPanel = document.getElementById('loginPanel');
    const mainDashboard = document.querySelector('.dashboard-container');
    const loginForm = document.getElementById('loginForm');
    const logoutButton = document.getElementById('logoutButton');
    const audioButton = document.getElementById('audioButton');
    const mainHeader = document.getElementById('mainHeader');
    const sidebar = document.getElementById('sidebar');

    // State Variables
    let isLoggedIn = false;
    let audioPlaying = false;
    const audio = new Audio('audio/IPL-theme-RMX.wav'); // Path to your audio file

    // --- Login & Logout Functions ---
    const users = {
        "samarth": "samarth123",
        "tejashree": "tejashree",
        "ramesh": "ramesh123"
    };

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = e.target.username.value;
        const password = e.target.password.value;
        const loginMessage = document.getElementById('loginMessage');

        if (users[username] === password) {
            isLoggedIn = true;
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('username', username);
            renderDashboard();
        } else {
            loginMessage.textContent = 'Invalid username or password.';
        }
    });

    logoutButton.addEventListener('click', () => {
        isLoggedIn = false;
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('username');
        renderDashboard();
    });

    function renderDashboard() {
        if (isLoggedIn) {
            loginPanel.style.display = 'none';
            mainDashboard.classList.add('logged-in');
            mainHeader.style.display = 'flex';
            sidebar.style.display = 'block';
            document.getElementById('welcomeMessage').textContent = `Welcome, ${localStorage.getItem('username')}!`;
            // Call functions to load data and charts
            fetchAndRenderOverallStats();
            setupNavigation();
        } else {
            loginPanel.style.display = 'flex';
            mainDashboard.classList.remove('logged-in');
            mainHeader.style.display = 'none';
            sidebar.style.display = 'none';
        }
    }

    // Check login status on page load
    isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    renderDashboard();

    // --- Audio Playback ---
    audioButton.addEventListener('click', () => {
        if (audioPlaying) {
            audio.pause();
            audioButton.innerHTML = '<i class="fas fa-play"></i>';
        } else {
            audio.play();
            audioButton.innerHTML = '<i class="fas fa-pause"></i>';
        }
        audioPlaying = !audioPlaying;
    });

    // --- Dynamic Navigation ---
    function setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('.dashboard-section');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                
                navLinks.forEach(nav => nav.classList.remove('active'));
                link.classList.add('active');
                
                sections.forEach(section => {
                    if (section.id === targetId) {
                        section.classList.add('active');
                    } else {
                        section.classList.remove('active');
                    }
                });
            });
        });
    }

    // --- Placeholder Data & Charting Functions (to be replaced with API calls) ---

    // Function to fetch and render Overall Stats
    function fetchAndRenderOverallStats() {
        // This is a placeholder. In a real app, you would fetch data from a backend.
        // E.g., fetch('/api/overall-stats').then(res => res.json()).then(data => { ... });

        // Dummy data
        const overallData = {
            totalMatches: 80,
            totalTeams: 10,
            topTeam: 'Chennai Super Kings',
            matchesPerSeason: { 'IPL-2023': 74, 'IPL-2024': 78, 'IPL-2025': 80 },
            tossDecisions: { 'Bat': 45, 'Field': 35 },
            topPlayers: [
                { name: 'Virat Kohli', awards: 15 },
                { name: 'Rohit Sharma', awards: 12 },
                { name: 'MS Dhoni', awards: 10 }
            ]
        };

        // Render stats cards
        document.getElementById('totalMatches').textContent = overallData.totalMatches;
        document.getElementById('totalTeams').textContent = overallData.totalTeams;
        document.getElementById('topTeam').textContent = overallData.topTeam;

        // Render charts using Chart.js
        renderMatchesPerSeasonChart(overallData.matchesPerSeason);
        renderTossDecisionChart(overallData.tossDecisions);

        // Render top players table
        const topPlayersTableBody = document.querySelector('#topPlayersTable tbody');
        topPlayersTableBody.innerHTML = '';
        overallData.topPlayers.forEach(player => {
            const row = `<tr><td>${player.name}</td><td>${player.awards}</td></tr>`;
            topPlayersTableBody.innerHTML += row;
        });
    }

    // Chart.js specific functions
    function renderMatchesPerSeasonChart(data) {
        const ctx = document.getElementById('matchesPerSeasonChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Matches Per Season',
                    data: Object.values(data),
                    backgroundColor: [
                        '#1a237e', '#d32f2f', '#ffca28', '#4caf50', '#00bcd4'
                    ],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Matches Hosted per Season' }
                }
            }
        });
    }

    function renderTossDecisionChart(data) {
        const ctx = document.getElementById('tossDecisionChart').getContext('2d');
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Toss Decision',
                    data: Object.values(data),
                    backgroundColor: ['#d32f2f', '#1a237e']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = (value / total * 100).toFixed(1) + '%';
                                return `${label}: ${value} (${percentage})`;
                            }
                        }
                    }
                }
            }
        });
    }
});