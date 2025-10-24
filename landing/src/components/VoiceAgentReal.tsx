"use client";

import { useEffect, useRef, useState } from "react";
import { X, Mic, MicOff, Phone } from "lucide-react";
import { ElevenLabsClient } from "@elevenlabs/client";

interface VoiceAgentProps {
  isOpen: boolean;
  onClose: () => void;
}

export function VoiceAgent({ isOpen, onClose }: VoiceAgentProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clientRef = useRef<ElevenLabsClient | null>(null);
  const conversationRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    // Initialize ElevenLabs client
    const apiKey = process.env.NEXT_PUBLIC_ELEVENLABS_API_KEY;
    if (apiKey) {
      clientRef.current = new ElevenLabsClient({ apiKey });
    }

    return () => {
      // Cleanup on unmount
      handleDisconnect();
    };
  }, []);

  const handleConnect = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const apiKey = process.env.NEXT_PUBLIC_ELEVENLABS_API_KEY;
      if (!apiKey) {
        throw new Error("API key no configurada");
      }

      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      mediaStreamRef.current = stream;

      // Initialize audio context
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();

      // Add initial message
      setTranscript(["Asistente: Buenos días, bienvenido al CESFAM Futrono. ¿En qué le puedo ayudar?"]);
      setIsConnected(true);
      setIsLoading(false);

      // TODO: Aquí se inicializaría la conversación real con ElevenLabs
      // Por ahora, simulamos la conexión exitosa
      // En producción, usarías el Conversation API del SDK

    } catch (err: any) {
      console.error("Error connecting:", err);
      setError(err.message || "Error al conectar con el agente");
      setIsLoading(false);

      // Cleanup on error
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
        mediaStreamRef.current = null;
      }
    }
  };

  const handleDisconnect = () => {
    // Stop microphone
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Close conversation
    if (conversationRef.current) {
      conversationRef.current = null;
    }

    setIsConnected(false);
    setTranscript([]);
    setError(null);
    onClose();
  };

  const toggleMute = () => {
    if (mediaStreamRef.current) {
      const audioTracks = mediaStreamRef.current.getAudioTracks();
      audioTracks.forEach(track => {
        track.enabled = isMuted; // Toggle
      });
      setIsMuted(!isMuted);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            Asistente Virtual
          </h2>
          <button
            onClick={handleDisconnect}
            className="rounded-full p-2 hover:bg-gray-100 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Status Indicator */}
        <div className="mb-6 flex items-center justify-center">
          <div
            className={`relative h-32 w-32 rounded-full ${
              isConnected
                ? "bg-gradient-to-br from-primary to-secondary animate-pulse"
                : isLoading
                ? "bg-gradient-to-br from-yellow-400 to-orange-500 animate-pulse"
                : "bg-gray-200"
            } flex items-center justify-center`}
          >
            {isLoading ? (
              <div className="h-16 w-16 border-4 border-white border-t-transparent rounded-full animate-spin" />
            ) : isConnected ? (
              <Mic className="h-16 w-16 text-white" />
            ) : (
              <MicOff className="h-16 w-16 text-gray-400" />
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 rounded-lg bg-red-50 border border-red-200 p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Transcript */}
        <div className="mb-6 h-48 overflow-y-auto rounded-lg bg-gray-50 p-4">
          {transcript.length === 0 ? (
            <p className="text-center text-gray-400">
              Presiona conectar para iniciar la conversación
            </p>
          ) : (
            <div className="space-y-2">
              {transcript.map((text, index) => (
                <p key={index} className="text-sm text-gray-700">
                  {text}
                </p>
              ))}
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex gap-4">
          {!isConnected ? (
            <button
              onClick={handleConnect}
              disabled={isLoading}
              className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-3 font-semibold text-white hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Conectando...
                </>
              ) : (
                <>
                  <Phone className="h-5 w-5" />
                  Conectar
                </>
              )}
            </button>
          ) : (
            <>
              <button
                onClick={toggleMute}
                className={`flex-1 flex items-center justify-center gap-2 rounded-lg px-6 py-3 font-semibold transition-colors ${
                  isMuted
                    ? "bg-yellow-500 hover:bg-yellow-600 text-white"
                    : "bg-gray-200 hover:bg-gray-300 text-gray-700"
                }`}
              >
                {isMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                {isMuted ? "Silenciado" : "Hablar"}
              </button>
              <button
                onClick={handleDisconnect}
                className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-red-500 px-6 py-3 font-semibold text-white hover:bg-red-600 transition-colors"
              >
                <Phone className="h-5 w-5 rotate-135" />
                Terminar
              </button>
            </>
          )}
        </div>

        {/* Info */}
        <div className="mt-4 space-y-1">
          <p className="text-center text-xs text-gray-500">
            Tu privacidad es importante. Las conversaciones no se graban.
          </p>
          {isConnected && (
            <p className="text-center text-xs text-green-600">
              ✓ Conectado • Micrófono activo
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
