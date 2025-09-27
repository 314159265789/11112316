// --- User Data Management ---
const USERS_KEY = 'bank_users';
const SESSION_KEY = 'bank_session';
const ADMIN_PASSWORD = 'SuperSecretAdmin123'; // Change for demo

function getUsers() {
    return JSON.parse(localStorage.getItem(USERS_KEY) || '{}');
}
function setUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
}
function getSession() {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
}
function setSession(username) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(username));
}
function clearSession() {
    localStorage.removeItem(SESSION_KEY);
}

// --- Registration ---
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').onsubmit = function(e) {
        e.preventDefault();
        const username = document.getElementById('register-username').value.trim();
        const password = document.getElementById('register-password').value;
        const confirm = document.getElementById('register-confirm').value;
        const errorDiv = document.getElementById('register-error');
        if (password !== confirm) {
            errorDiv.textContent = 'Passwords do not match.';
            return;
        }
        let users = getUsers();
        if (users[username]) {
            errorDiv.textContent = 'Username already exists.';
            return;
        }
        users[username] = {
            password: btoa(password),
            balance: 1000 + Math.floor(Math.random()*9000),
            transactions: [
                { type: 'credit', amount: 1000, date: new Date().toLocaleString(), desc: 'Initial deposit' }
            ]
        };
        setUsers(users);
        setSession(username);
        window.location = 'dashboard.html';
    };
}

// --- Login ---
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').onsubmit = function(e) {
        e.preventDefault();
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const errorDiv = document.getElementById('login-error');
        let users = getUsers();
        if (!users[username] || users[username].password !== btoa(password)) {
            errorDiv.textContent = 'Invalid username or password.';
            return;
        }
        setSession(username);
        window.location = 'dashboard.html';
    };
}

// --- Dashboard ---
if (window.location.pathname.endsWith('dashboard.html')) {
    const session = getSession();
    if (!session) {
        window.location = 'index.html';
    } else {
        let users = getUsers();
        document.getElementById('user-name').textContent = session;
        document.getElementById('account-balance').textContent = users[session].balance;
        // Transaction history
        const txList = document.getElementById('transaction-list');
        txList.innerHTML = '';
        users[session].transactions.slice().reverse().forEach(tx => {
            const li = document.createElement('li');
            li.textContent = `${tx.date}: ${tx.type === 'credit' ? '+' : '-'}$${tx.amount} (${tx.desc})`;
            txList.appendChild(li);
        });
        // Logout
        document.getElementById('logout-btn').onclick = function() {
            clearSession();
            window.location = 'index.html';
        };
        // Transfer
        document.getElementById('transferForm').onsubmit = function(e) {
            e.preventDefault();
            const to = document.getElementById('transfer-to').value.trim();
            const amount = parseFloat(document.getElementById('transfer-amount').value);
            const errorDiv = document.getElementById('transfer-error');
            if (!users[to]) {
                errorDiv.textContent = 'Recipient not found.';
                return;
            }
            if (to === session) {
                errorDiv.textContent = 'Cannot transfer to yourself.';
                return;
            }
            if (amount <= 0 || isNaN(amount)) {
                errorDiv.textContent = 'Invalid amount.';
                return;
            }
            if (users[session].balance < amount) {
                errorDiv.textContent = 'Insufficient funds.';
                return;
            }
            users[session].balance -= amount;
            users[to].balance += amount;
            const now = new Date().toLocaleString();
            users[session].transactions.push({ type: 'debit', amount, date: now, desc: `Transfer to ${to}` });
            users[to].transactions.push({ type: 'credit', amount, date: now, desc: `Transfer from ${session}` });
            setUsers(users);
            window.location.reload();
        };
    }
}

// --- Admin Panel ---
if (window.location.pathname.endsWith('admin.html')) {
    const adminForm = document.getElementById('adminLoginForm');
    const adminContent = document.getElementById('admin-content');
    const adminData = document.getElementById('admin-data');
    const adminLogout = document.getElementById('admin-logout');
    if (adminForm) {
        adminForm.onsubmit = function(e) {
            e.preventDefault();
            const pass = document.getElementById('admin-password').value;
            const errorDiv = document.getElementById('admin-error');
            if (pass !== ADMIN_PASSWORD) {
                errorDiv.textContent = 'Incorrect admin password.';
                return;
            }
            adminContent.style.display = 'none';
            adminData.style.display = 'block';
            adminLogout.style.display = 'block';
            // Show all users
            const users = getUsers();
            const userList = document.getElementById('user-list');
            userList.innerHTML = '';
            Object.keys(users).forEach(u => {
                const li = document.createElement('li');
                li.textContent = `${u} | Balance: $${users[u].balance}`;
                userList.appendChild(li);
            });
        };
    }
    if (adminLogout) {
        adminLogout.onclick = function() {
            adminContent.style.display = 'block';
            adminData.style.display = 'none';
            adminLogout.style.display = 'none';
        };
    }
}

// --- Hidden Files Simulation ---
// These files are not linked in the UI, but exist for "security through obscurity" demo
// e.g., /hidden-logs.html, /secret-backup.html
