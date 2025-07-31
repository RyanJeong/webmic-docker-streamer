/*  Browser logic:
    1. getUserMedia ⇒ MediaRecorder
    2. send Uint8Array chunks through WebSocket (/ws/producer)
*/

(() => {
  let ws, recorder;
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const statusEl = document.getElementById("status");

  startBtn.onclick = async () => {
    // open WS first, so we can push frames immediately
    ws = new WebSocket(`ws://${location.hostname}:33333/ws/producer`);
    ws.binaryType = "arraybuffer";

    // wait until socket is open
    await new Promise((r) => (ws.onopen = r));

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

    recorder.ondataavailable = async (e) => {
      if (ws.readyState === WebSocket.OPEN) {
        const buf = await e.data.arrayBuffer(); // blob → ArrayBuffer
        ws.send(buf);
      }
    };
    recorder.start(1000); // ms per chunk
    statusEl.textContent = "Recording ...";
    startBtn.disabled = true;
    stopBtn.disabled = false;
  };

  stopBtn.onclick = () => {
    recorder.stop();
    ws.close();
    statusEl.textContent = "Stopped";
    startBtn.disabled = false;
    stopBtn.disabled = true;
  };
})();
