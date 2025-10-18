// src/components/RecordButton.jsx
import { useState, useRef } from "react";
import axiosClient from "../api/axiosClient";
import { Button } from "@/components/ui/button";

export default function RecordButton({ onAdded }) {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", blob, "patient_audio.webm");

        try {
          setLoading(true);
          await axiosClient.post("/voice-input", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          if (onAdded) onAdded(); // refresh table
        } catch (err) {
          console.error("Error uploading voice input:", err);
          alert("Failed to process audio");
        } finally {
          setLoading(false);
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Mic access denied:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6">
      <Button
        onClick={recording ? stopRecording : startRecording}
        disabled={loading}
        className={recording ? "bg-red-600 hover:bg-red-700" : ""}
      >
        {loading
          ? "Processing..."
          : recording
          ? "Stop Recording"
          : "Record Voice"}
      </Button>
    </div>
  );
}