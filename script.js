async function startBiometricAuth() {
    const voterId = document.getElementById("voterId").value;

    if (!voterId) {
        document.getElementById("result").innerText = "Please enter your Voter ID";
        return;
    }

    try {
        // Check if WebAuthn is supported
        if (!window.PublicKeyCredential) {
            alert("WebAuthn not supported on this browser.");
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/start-auth", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ voter_id: voterId })
        });

        const data = await response.json();
        if (data.status !== "success") {
            document.getElementById("result").innerText = data.message;
            return;
        }

        
        const publicKey = data.challenge;
        const credential = await navigator.credentials.get({ publicKey });

        const verificationResponse = await fetch("http://127.0.0.1:5000/verify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                voter_id: voterId,
                credential: JSON.stringify(credential)
            })
        });

        const verificationData = await verificationResponse.json();
        document.getElementById("result").innerText = verificationData.message;
    } catch (error) {
        console.error("Biometric authentication failed", error);
        document.getElementById("result").innerText = "Authentication failed. Try again.";
    }
}
