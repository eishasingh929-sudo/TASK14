import { useRef, useState } from "react";

export function useVoice() {
  const [isRecording, setIsRecording] = useState(false);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };

    recorderRef.current = recorder;
    recorder.start();
    setIsRecording(true);
  }

  function stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const recorder = recorderRef.current;
      if (!recorder) {
        reject(new Error("Recorder not initialized"));
        return;
      }
      recorder.onstop = () => {
        setIsRecording(false);
        resolve(new Blob(chunksRef.current, { type: "audio/webm" }));
      };
      recorder.stop();
    });
  }

  return { isRecording, startRecording, stopRecording };
}
