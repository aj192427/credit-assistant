import React, { useEffect, useRef, useState } from "react";
import { advisorApi } from "../api/client.js";

export default function AdvisorPanel() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi. Ask me about your credit profile, borrowing, or a financial goal.",
    },
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");
  const [speechError, setSpeechError] = useState("");
  const [voiceAvailable, setVoiceAvailable] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const [goal, setGoal] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setVoiceAvailable(Boolean(window.SpeechRecognition || window.webkitSpeechRecognition));
    return () => {
      recognitionRef.current?.abort();
      window.speechSynthesis?.cancel();
    };
  }, []);

  const sendChatMessage = async (text, speakReply = false) => {
    const content = text.trim();
    if (!content || chatLoading) return;

    const nextMessages = [...messages, { role: "user", content }].slice(-12);
    setMessages(nextMessages);
    setChatInput("");
    setChatError("");
    setSpeechError("");
    setChatLoading(true);

    try {
      const res = await advisorApi.chat(nextMessages);
      const reply = res.data.reply;
      setMessages((current) => [...current, { role: "assistant", content: reply }].slice(-12));
      if (speakReply && window.speechSynthesis && window.SpeechSynthesisUtterance) {
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(new window.SpeechSynthesisUtterance(reply));
      }
    } catch (err) {
      setChatError(err.response?.data?.detail || "Could not reach the financial assistant.");
    } finally {
      setChatLoading(false);
    }
  };

  const startVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechError("Voice input is not supported in this browser. You can type your question instead.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => {
      setListening(true);
      setSpeechError("");
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = (event) => {
      setListening(false);
      setSpeechError(event.error === "not-allowed"
        ? "Allow microphone access in your browser to use voice input."
        : "Voice input could not be captured. Try again or type your question.");
    };
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setChatInput(transcript);
      sendChatMessage(transcript, true);
    };
    recognitionRef.current = recognition;
    recognition.start();
  };

  const readAloud = (text) => {
    if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
      setSpeechError("Read-aloud is not supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new window.SpeechSynthesisUtterance(text));
  };

  const runConsultation = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await advisorApi.consult(goal);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not reach the AI advisor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <section className="card advisor-chat">
        <div className="advisor-chat-header">
          <div>
            <p className="advisor-eyebrow">CREDIT ASSISTANT</p>
            <h3>Ask your financial assistant</h3>
            <p className="advisor-description">Personalized answers using your credit profile and goals.</p>
          </div>
          <span className="advisor-status">Profile connected</span>
        </div>

        <div className="chat-transcript" aria-live="polite" aria-label="Conversation">
          {messages.map((message, index) => (
            <article className={`chat-message chat-message-${message.role}`} key={`${index}-${message.role}`}>
              <div className="chat-message-label">{message.role === "assistant" ? "Assistant" : "You"}</div>
              <p>{message.content}</p>
              {message.role === "assistant" && index > 0 && (
                <button className="read-aloud-button" onClick={() => readAloud(message.content)}>
                  Read aloud
                </button>
              )}
            </article>
          ))}
          {chatLoading && <p className="chat-pending" role="status">Thinking through your question...</p>}
        </div>

        {chatError && <div className="error-text" role="alert">{chatError}</div>}
        {(speechError || (!voiceAvailable && "Voice input is not supported in this browser. You can still type.")) && (
          <div className="speech-note" role="status">
            {speechError || "Voice input is not supported in this browser. You can still type."}
          </div>
        )}

        <form
          className="chat-composer"
          onSubmit={(event) => {
            event.preventDefault();
            sendChatMessage(chatInput);
          }}
        >
          <label className="visually-hidden" htmlFor="advisor-chat-input">Ask a financial question</label>
          <textarea
            id="advisor-chat-input"
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                sendChatMessage(chatInput);
              }
            }}
            placeholder="Ask about your score, debt, or goal..."
            maxLength={1200}
            rows={2}
            disabled={chatLoading}
          />
          <div className="chat-actions">
            <button
              className={`voice-button${listening ? " is-listening" : ""}`}
              type="button"
              onClick={() => listening ? recognitionRef.current?.stop() : startVoiceInput()}
              disabled={!voiceAvailable || chatLoading}
              aria-label={listening ? "Stop voice input" : "Speak your question"}
              title={voiceAvailable ? "Speak your question" : "Voice input unavailable"}
            >
              {listening ? "Stop listening" : "Voice input"}
            </button>
            <button className="primary chat-send" type="submit" disabled={chatLoading || !chatInput.trim()}>
              {chatLoading ? "Sending..." : "Send"}
            </button>
          </div>
        </form>
      </section>

      <section className="card">
        <h3>AI Financial Consultation</h3>
        <p className="advisor-description">Get a personalized analysis and a 5-step plan based on your current numbers.</p>
        <label htmlFor="advisor-goal">Optional goal (for example, buying a car in 12 months)</label>
        <input id="advisor-goal" value={goal} onChange={(event) => setGoal(event.target.value)} placeholder="What are you working toward?" />

        <button className="primary" onClick={runConsultation} disabled={loading}>
          {loading ? "Preparing advice..." : "Get AI Advice"}
        </button>

        {error && <div className="error-text" role="alert">{error}</div>}

        {result && (
          <div className="consultation-result">
            <p>{result.analysis}</p>
            <h4>Your 5-Step Plan</h4>
            <ol className="action-plan">
              {result.action_plan.map((step, index) => <li key={index}>{step}</li>)}
            </ol>
          </div>
        )}
      </section>
    </>
  );
}
