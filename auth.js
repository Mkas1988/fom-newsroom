(function() {
    const PASS_HASH = '5f4dcc3b5aa765d61d8327deb882cf99'; // not used, simple check
    const CORRECT = 'Fom!1991';
    const KEY = 'fom_newsroom_auth';

    if (sessionStorage.getItem(KEY) === 'true') return;

    // Block page
    document.documentElement.style.overflow = 'hidden';

    const overlay = document.createElement('div');
    overlay.id = 'authOverlay';
    overlay.innerHTML = `
        <style>
            #authOverlay {
                position: fixed; inset: 0; z-index: 10000;
                background: #fff;
                display: flex; align-items: center; justify-content: center;
                font-family: 'Neue-Haas-Grotesk-Text-Pro', Helvetica, Arial, sans-serif;
            }
            #authBox {
                text-align: center; max-width: 380px; width: 100%; padding: 40px;
            }
            #authBox img { height: 56px; margin-bottom: 32px; }
            #authBox h2 {
                font-family: 'Neue-Haas-Grotesk-Display-Pro', Helvetica, Arial, sans-serif;
                font-size: 24px; font-weight: 700; color: #121212; margin-bottom: 8px;
            }
            #authBox p { font-size: 14px; color: #6D6D6D; margin-bottom: 28px; }
            #authInput {
                width: 100%; padding: 14px 18px; border: 1.5px solid #E6E6E6;
                border-radius: 8px; font-size: 16px; font-family: inherit;
                outline: none; transition: border-color .2s; text-align: center;
            }
            #authInput:focus { border-color: #00C6B2; }
            #authInput.error { border-color: #E81818; animation: shake .4s; }
            #authBtn {
                width: 100%; margin-top: 16px; padding: 14px;
                background: #00C6B2; color: white; border: none; border-radius: 8px;
                font-size: 15px; font-weight: 700; cursor: pointer;
                font-family: inherit; transition: background .2s;
            }
            #authBtn:hover { background: #009F8F; }
            #authError { color: #E81818; font-size: 13px; margin-top: 12px; display: none; }
            @keyframes shake {
                0%,100% { transform: translateX(0); }
                25% { transform: translateX(-8px); }
                75% { transform: translateX(8px); }
            }
        </style>
        <div id="authBox">
            <img src="fom-logo.png" alt="FOM">
            <h2>FOM Newsroom</h2>
            <p>Bitte geben Sie das Passwort ein, um fortzufahren.</p>
            <form onsubmit="return checkAuth()">
                <input type="password" id="authInput" placeholder="Passwort" autofocus>
                <button type="submit" id="authBtn">Anmelden</button>
            </form>
            <div id="authError">Falsches Passwort. Bitte versuchen Sie es erneut.</div>
        </div>
    `;

    document.body.prepend(overlay);

    window.checkAuth = function() {
        const val = document.getElementById('authInput').value;
        if (val === CORRECT) {
            sessionStorage.setItem(KEY, 'true');
            document.getElementById('authOverlay').remove();
            document.documentElement.style.overflow = '';
            return false;
        }
        document.getElementById('authInput').classList.add('error');
        document.getElementById('authError').style.display = 'block';
        setTimeout(() => document.getElementById('authInput').classList.remove('error'), 400);
        return false;
    };
})();
