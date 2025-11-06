/**
 * Main application component
 */
import React, { useState, useEffect } from 'react';
import { ChatModal } from './components/ChatModal';
import { HelpModal } from './components/HelpModal';
import { EditPageModal } from './components/EditPageModal';
import { PartyPopper } from './components/PartyPopper';
import { useChat } from './hooks/useChat';
import './styles/App.css';
import './styles/Help.css';
import './styles/Lab.css';

// Helper functions for localStorage
const loadGuardrailSettings = () => {
  try {
    const regex = localStorage.getItem('regexGuardrailsEnabled');
    const nemo = localStorage.getItem('nemoGuardrailsEnabled');
    return {
      regex: regex !== null ? JSON.parse(regex) : true,
      nemo: nemo !== null ? JSON.parse(nemo) : true,
    };
  } catch (error) {
    console.error('Error loading guardrail settings:', error);
    return { regex: true, nemo: true };
  }
};

const saveGuardrailSetting = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Error saving guardrail setting:', error);
  }
};

function App() {
  // Initialize state from localStorage
  const savedSettings = loadGuardrailSettings();
  const [regexGuardrailsEnabled, setRegexGuardrailsEnabled] = useState(savedSettings.regex);
  const [nemoGuardrailsEnabled, setNemoGuardrailsEnabled] = useState(savedSettings.nemo);
  const [chatOpen, setChatOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [editPageOpen, setEditPageOpen] = useState(false);
  const [department, setDepartment] = useState('hr'); // 'hr' or 'payroll'
  const [section, setSection] = useState('general'); // 'benefits', 'timeoff', 'payroll', 'general'
  const [labNumber, setLabNumber] = useState(null); // Which lab is active
  const [poppers, setPoppers] = useState([]); // Party popper animations
  const { messages, isLoading, metadata, sendMessage, clearMessages } = useChat(regexGuardrailsEnabled, nemoGuardrailsEnabled, department);

  const triggerPartyPopper = (e) => {
    const rect = e.target.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const id = Date.now();

    setPoppers(prev => [...prev, { id, x, y }]);
  };

  const triggerCelebration = () => {
    // First wave of party poppers
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    const createPoppers = (offset = 0) => {
      const newPoppers = [];
      for (let i = 0; i < 10; i++) {
        newPoppers.push({
          id: Date.now() + offset + i,
          x: Math.random() * screenWidth,
          y: Math.random() * screenHeight,
        });
      }
      return newPoppers;
    };

    // First wave
    setPoppers(prev => [...prev, ...createPoppers(0)]);

    // Second wave after 800ms
    setTimeout(() => {
      setPoppers(prev => [...prev, ...createPoppers(10000)]);
    }, 800);
  };

  const removePopper = (id) => {
    setPoppers(prev => prev.filter(p => p.id !== id));
  };

  const handleRegexGuardrailsToggle = (e) => {
    const enabled = e.target.checked;
    setRegexGuardrailsEnabled(enabled);
    saveGuardrailSetting('regexGuardrailsEnabled', enabled);
    // Clear messages when toggling to avoid confusion
    clearMessages();
  };

  const handleNemoGuardrailsToggle = (e) => {
    const enabled = e.target.checked;
    setNemoGuardrailsEnabled(enabled);
    saveGuardrailSetting('nemoGuardrailsEnabled', enabled);
    // Clear messages when toggling to avoid confusion
    clearMessages();
  };

  const openChat = (dept, sectionType = 'general', lab = null) => {
    setDepartment(dept);
    setSection(sectionType);
    setLabNumber(lab);
    setChatOpen(true);
    clearMessages(); // Clear previous department's messages
  };

  const getChatTitle = () => {
    switch(section) {
      case 'benefits': return 'Health Benefits Assistant';
      case 'timeoff': return 'Time Off Assistant';
      case 'payroll': return 'Payroll Assistant';
      default: return 'HR Support Bot';
    }
  };

  return (
    <div className="app">
      {/* Help Button */}
      <button
        className="help-button"
        onClick={(e) => {
          triggerPartyPopper(e);
          setHelpOpen(true);
        }}
        title="Lab Guide"
      >
        ?
      </button>

      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo">AIFirst</div>
            <div className="tagline">HR Platform</div>
          </div>
          <div className="header-text">
            <h1>Welcome to AIFirst HR Assistant</h1>
            <p>Your intelligent HR companion for benefits, policies, and employee support</p>
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="controls">
        <div className="guardrails-toggle">
          <label>
            <input
              type="checkbox"
              checked={regexGuardrailsEnabled}
              onChange={handleRegexGuardrailsToggle}
            />
            Regex Guardrails
          </label>
          <label>
            <input
              type="checkbox"
              checked={nemoGuardrailsEnabled}
              onChange={handleNemoGuardrailsToggle}
            />
            NeMo Guardrails
          </label>
        </div>

        <div className="status">
          <div className={`status-item ${regexGuardrailsEnabled ? 'active' : 'inactive'}`}>
            <span className="status-dot"></span>
            Regex {regexGuardrailsEnabled ? 'Active' : 'Inactive'}
          </div>
          <div className={`status-item ${nemoGuardrailsEnabled ? 'active' : 'inactive'}`}>
            <span className="status-dot"></span>
            NeMo {nemoGuardrailsEnabled ? 'Active' : 'Inactive'}
          </div>
          <a
            href="https://smith.langchain.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="traces-link"
          >
            View Traces 📊
          </a>
        </div>
      </div>

      {/* Main Content */}
      <main className="main-content">
        <div className="welcome-section">
          <h2>How can we help you today?</h2>
          <p>Ask about benefits, time off policies, payroll, or any HR-related questions.</p>

          <div className="info-cards">
            <div className="info-card" onClick={() => openChat('hr', 'general', 1)}>
              <div className="card-icon">🎯</div>
              <h3>Lab 1: Check the lab setup</h3>
              <div className="lab-badge">Lab 1: Intro</div>
            </div>
            <div className="info-card hr-card" onClick={() => openChat('hr', 'general')}>
              <div className="card-icon">🌐</div>
              <h3>HR Support</h3>
              <p>General HR inquiries, policies, and assistance</p>
              <div className="lab-badge">Lab 2: SSRF</div>
            </div>
            <div className="info-card payroll-card" onClick={() => openChat('payroll', 'payroll')}>
              <div className="card-icon">💰</div>
              <h3>Payroll System</h3>
              <p>Paychecks, direct deposit, W-2 forms, and salary</p>
              <div className="lab-badge">Lab 3: Prompt Extraction</div>
            </div>
            <div className="info-card timeoff-card" onClick={() => openChat('timeoff', 'timeoff')}>
              <div className="card-icon">🏖️</div>
              <h3>Time Off</h3>
              <p>PTO, vacation, and leave policies</p>
              <div className="lab-badge">Lab 4: IDOR</div>
            </div>
          </div>

          {/* Utilities Section */}
          <div className="utilities-section">
            <h2>Utilities</h2>
            <div className="info-cards">
              <div className="info-card utility-card" onClick={() => setEditPageOpen(true)}>
                <div className="card-icon">✏️</div>
                <h3>Edit External Page</h3>
                <p>Modify content server pages for testing</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Chat Modal Overlay */}
      {chatOpen && (
        <div className="chat-overlay">
          <div className={`chat-modal ${section}-modal`}>
            <div className={`chat-header ${section}-header`}>
              <div className="chat-header-info">
                <h3>{getChatTitle()}</h3>
                <span className="chat-status">Online</span>
              </div>
              <button className="close-chat" onClick={() => setChatOpen(false)}>
                ✕
              </button>
            </div>
            <ChatModal
              messages={messages}
              isLoading={isLoading}
              metadata={metadata}
              onSendMessage={sendMessage}
              onClearMessages={clearMessages}
              onCelebration={triggerCelebration}
              section={section}
              labNumber={labNumber}
            />
          </div>
        </div>
      )}

      {/* Help Modal */}
      {helpOpen && <HelpModal onClose={() => setHelpOpen(false)} />}

      {/* Edit Page Modal */}
      <EditPageModal isOpen={editPageOpen} onClose={() => setEditPageOpen(false)} />

      {/* Party Popper Animations */}
      {poppers.map((popper) => (
        <PartyPopper
          key={popper.id}
          x={popper.x}
          y={popper.y}
          onComplete={() => removePopper(popper.id)}
        />
      ))}
    </div>
  );
}

export default App;
