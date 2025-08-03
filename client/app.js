/* 22050 Hz, mono, Float32 1-second chunks -> WebSocket */
(() => {
  let ws,
    ctx,
    worklet,
    acc,
    pos = 0; // runtime state holders
  const FRAME = 22050; // samples per 1 second

  const $start = document.getElementById("startBtn");
  const $stop = document.getElementById("stopBtn");
  const $status = document.getElementById("status");

  // AudioWorklet (128-sample callback)
  const workletURL = URL.createObjectURL(
    new Blob(
      [
        `
      class Capture extends AudioWorkletProcessor {
        process(inputs) {                        // called every 128 samples
          const mono = inputs[0][0];             // first channel
          if (mono) this.port.postMessage(mono); // send Float32Array to main
          return true;                           // keep processor alive
        }
      }
      registerProcessor('capture', Capture);
    `,
      ],
      { type: "application/javascript" }
    )
  );

  $start.onclick = async () => {
    /* 1. open WebSocket first */
    ws = new WebSocket(`ws://${location.hostname}:33333/ws/producer`);
    ws.binaryType = "arraybuffer";
    await new Promise((r) => (ws.onopen = r)); // wait for connection

    /* 2. configure 22 kHz AudioContext */
    ctx = new (window.AudioContext || window.webkitAudioContext)({
      sampleRate: 22050,
    });
    await ctx.audioWorklet.addModule(workletURL); // load worklet JS

    /* 3. stream microphone -> worklet */
    const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
    const src = ctx.createMediaStreamSource(mic);
    worklet = new AudioWorkletNode(ctx, "capture");
    src.connect(worklet);

    /* 4. accumulate 1-second frames */
    acc = new Float32Array(FRAME);
    pos = 0;

    worklet.port.onmessage = ({ data }) => {
      const chunk = data; // Float32Array (128 samples)
      const remain = FRAME - pos; // still needed to reach 1 s
      const n = Math.min(remain, chunk.length);
      acc.set(chunk.subarray(0, n), pos); // copy into accumulator
      pos += n;

      if (pos === FRAME) {
        // got full 1-second buffer
        ws.send(acc.buffer); // send raw bytes
        pos = 0; // reset pointer
      }
    };

    $status.textContent = "Recording ...";
    $start.disabled = true;
    $stop.disabled = false;
  };

  $stop.onclick = () => {
    worklet?.disconnect(); // stop audio graph
    ctx?.close(); // close AudioContext
    ws?.close(); // close socket
    $status.textContent = "Stopped";
    $start.disabled = false;
    $stop.disabled = true;
  };
})();
